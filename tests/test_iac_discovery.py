import pytest
from app.collectors.iac import collect_iac
from app.detectors.iac import detect_iac
from app.services.signature_loader import load_signatures_from_yaml
from app.config import settings
from app.models import SourceType, Specificity, SignalType

def test_iac_valid_signals(tmp_path):
    tf_content = """provider "aws" {
  region = "us-east-1"
}

resource "aws_bedrock_agent" "helper" {
  name = "helper-agent"
}
"""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(tf_content, encoding="utf-8")
    
    collected = collect_iac(tf_file)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    ev_list = detect_iac(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 1
    ev = ev_list[0]
    
    assert ev.application == "test-app"
    assert ev.source_type == SourceType.IAC
    assert ev.source_path == str(tf_file)
    assert ev.line_number == 5
    assert ev.matched_signature == "aws-bedrock-iac"
    assert ev.provider == "aws"
    assert ev.model is None
    assert ev.ai_type == "bedrock"
    assert ev.confidence_weight == 0.8
    assert ev.specificity == Specificity.HIGH
    assert ev.signal_type == SignalType.EXISTENCE

def test_iac_generic_signals_no_evidence(tmp_path):
    tf_content = """# Comments containing AI or Bedrock plans
variable "ai_enabled" {
  type    = bool
  default = true
}

resource "aws_instance" "app_server" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
}
"""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(tf_content, encoding="utf-8")
    
    collected = collect_iac(tf_file)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    ev_list = detect_iac(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 0

def test_iac_unreadable_graceful_handling():
    # Pass invalid content type to check graceful return of empty list
    ev_list = detect_iac(None, "main.tf", "test-app", [])
    assert ev_list == []
