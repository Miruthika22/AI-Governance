import pytest
from app.collectors.config import collect_config
from app.detectors.config import detect_config
from app.services.signature_loader import load_signatures_from_yaml
from app.config import settings
from app.models import SourceType, Specificity, SignalType

def test_config_valid_signals(tmp_path):
    # Test .env config format
    env_content = """PORT=8000
OPENAI_MODEL=gpt-4o-mini
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content, encoding="utf-8")
    
    collected = collect_config(env_file)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    ev_list = detect_config(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 1
    ev = ev_list[0]
    
    assert ev.application == "test-app"
    assert ev.source_type == SourceType.CONFIG
    assert ev.source_path == str(env_file)
    assert ev.line_number == 2
    assert ev.matched_signature == "openai-gpt4-sdk"
    assert ev.provider == "openai"
    assert ev.model == "gpt-4o-mini"
    assert ev.ai_type == "llm"
    assert ev.specificity == Specificity.HIGH
    assert ev.signal_type == SignalType.USAGE

    # Test JSON config format
    json_content = """{
        "services": {
            "openai": {
                "provider": "openai"
            }
        }
    }"""
    json_file = tmp_path / "config.json"
    json_file.write_text(json_content, encoding="utf-8")
    
    collected = collect_config(json_file)
    ev_list = detect_config(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 1
    ev = ev_list[0]
    
    assert ev.source_type == SourceType.CONFIG
    assert ev.matched_signature == "openai-generic-config"
    assert ev.provider == "openai"
    assert ev.model is None
    assert ev.specificity == Specificity.MEDIUM
    assert ev.signal_type == SignalType.EXISTENCE

def test_config_key_alone_no_evidence(tmp_path):
    # Key matches but value does not match model_pattern or provider name
    env_content = "OPENAI_MODEL=unrelated-model-name\n"
    env_file = tmp_path / ".env"
    env_file.write_text(env_content, encoding="utf-8")
    
    collected = collect_config(env_file)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    ev_list = detect_config(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 0

def test_config_generic_mentions_no_evidence(tmp_path):
    yaml_content = """app:
  ai_enabled: true
  description: "Using OpenAI products"
  gpt_version: 4
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    
    collected = collect_config(yaml_file)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    ev_list = detect_config(collected["content"], collected["source_path"], "test-app", signatures)
    assert len(ev_list) == 0

def test_config_unreadable_graceful_handling():
    # Pass invalid structure to detect_config
    ev_list = detect_config("invalid JSON / YAML content", "config.json", "test-app", [])
    assert ev_list == []
