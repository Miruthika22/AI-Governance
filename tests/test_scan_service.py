import pytest
from pathlib import Path
from app.services.scan import run_discovery_scan
from app.models import SourceType, Specificity, SignalType, AssetStatus

def test_end_to_end_discovery_scan(tmp_path):
    # 1. Setup python file with valid AI source signals
    py_code = """import openai
client = openai.OpenAI()
model = "gpt-4o"
"""
    py_file = tmp_path / "app.py"
    py_file.write_text(py_code, encoding="utf-8")

    # 2. Setup JSON config with valid AI config signals
    json_content = """{
        "services": {
            "openai": {
                "provider": "openai"
            }
        }
    }"""
    json_file = tmp_path / "config.json"
    json_file.write_text(json_content, encoding="utf-8")

    # 3. Setup Terraform file with valid AI infrastructure resources
    tf_content = """provider "openai" {}

resource "openai_model_deployment" "gpt" {
  name = "gpt-deployment"
}
"""
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(tf_content, encoding="utf-8")

    # 4. Setup unsupported file (should be skipped)
    readme_file = tmp_path / "README.md"
    readme_file.write_text("This is documentation, not discovery target", encoding="utf-8")

    # 5. Setup invalid file that fails parsing (should not stop scan)
    bad_py_code = """import openai
def invalid_syntax(
"""
    bad_py_file = tmp_path / "bad.py"
    bad_py_file.write_text(bad_py_code, encoding="utf-8")

    # Execute end-to-end scanner
    result = run_discovery_scan("e2e-app", tmp_path)

    # Asserts file counts (5 files total: app.py, config.json, main.tf, README.md, bad.py)
    assert result.scanned_file_count == 5
    # 4 supported file types (.py, .json, .tf, .py) - README.md is skipped
    assert result.supported_file_count == 4

    # Asserts evidence mapping
    assert len(result.evidence_records) == 3  # app.py (1 match), config.json (1 match), main.tf (1 match)
    
    # Assert all evidence is associated with the app name
    for ev in result.evidence_records:
        assert ev.application == "e2e-app"
        assert ev.provider == "openai"
        assert ev.ai_type == "llm"

    # Verify sources mapped
    sources = {ev.source_type for ev in result.evidence_records}
    assert SourceType.SOURCE_CODE in sources
    assert SourceType.CONFIG in sources
    assert SourceType.IAC in sources

    # Assert correlator received evidence and created DISCOVERED asset
    assert len(result.correlated_assets) == 1
    asset = result.correlated_assets[0]
    
    assert asset.application == "e2e-app"
    assert asset.provider == "openai"
    assert asset.ai_type == "llm"
    assert asset.status == AssetStatus.DISCOVERED
    assert asset.confidence == round((0.9 + 0.6 + 0.85) / 3, 2)  # Average of 0.9, 0.6, 0.85 = 0.78
    assert "discovered" in asset.confidence_rationale.lower()
    assert "config" in asset.confidence_rationale.lower()
    assert "iac" in asset.confidence_rationale.lower()
    assert "source_code" in asset.confidence_rationale.lower()
    assert len(asset.evidence_ids) == 3
