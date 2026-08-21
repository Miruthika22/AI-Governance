import pytest
from app.collectors.source_code import collect_source_code
from app.detectors.source_code import detect_source_code
from app.services.signature_loader import load_signatures_from_yaml
from app.config import settings
from app.models import SourceType, Specificity, SignalType

def test_valid_ai_source_code_signals(tmp_path):
    code = """import openai

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o"
)
"""
    file_path = tmp_path / "valid_ai_usage.py"
    file_path.write_text(code, encoding="utf-8")
    
    # 1. Verify Collector
    collected = collect_source_code(file_path)
    assert collected["content"] == code
    assert collected["source_path"] == str(file_path)
    
    # Load registry signatures
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    # 2. Verify Detector & Evidence properties
    evidence_list = detect_source_code(
        content=collected["content"],
        source_path=collected["source_path"],
        application="test-app",
        signatures=signatures
    )
    
    assert len(evidence_list) == 1
    ev = evidence_list[0]
    
    assert ev.application == "test-app"
    assert ev.source_type == SourceType.SOURCE_CODE
    assert ev.source_path == str(file_path)
    assert ev.line_number == 5  # line number of "gpt-4o"
    assert ev.matched_signature == "openai-gpt4-sdk"
    assert ev.provider == "openai"
    assert ev.model == "gpt-4o"
    assert ev.ai_type == "llm"
    assert ev.confidence_weight == 0.9
    assert ev.specificity == Specificity.HIGH
    assert ev.signal_type == SignalType.USAGE

def test_false_positives_in_comments_only(tmp_path):
    code = """# We mention OpenAI and GPT in documentation comments here.
# But we never import or invoke anything in python.
def run():
    # using gpt-4 model
    return "ok"
"""
    file_path = tmp_path / "comments_only.py"
    file_path.write_text(code, encoding="utf-8")
    
    collected = collect_source_code(file_path)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    evidence_list = detect_source_code(
        content=collected["content"],
        source_path=collected["source_path"],
        application="test-app",
        signatures=signatures
    )
    
    # Should yield zero evidence
    assert len(evidence_list) == 0

def test_invalid_syntax_handled_gracefully(tmp_path):
    code = """import openai
def bad_syntax(
    print("unclosed parenthesis"
"""
    file_path = tmp_path / "bad_syntax.py"
    file_path.write_text(code, encoding="utf-8")
    
    collected = collect_source_code(file_path)
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    evidence_list = detect_source_code(
        content=collected["content"],
        source_path=collected["source_path"],
        application="test-app",
        signatures=signatures
    )
    
    # Should catch SyntaxError and return an empty list gracefully
    assert evidence_list == []
