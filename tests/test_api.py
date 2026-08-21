from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_scan_valid_directory(tmp_path: Path):
    # Create a temporary sample application
    sample_file = tmp_path / "app.py"

    sample_file.write_text(
        '''
from openai import OpenAI

client = OpenAI()

model = "gpt-4o"
'''
    )

    response = client.post(
        "/scan",
        json={
            "application": "test-app",
            "root_dir": str(tmp_path)
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "test-app"
    assert "scanned_file_count" in data
    assert "supported_file_count" in data
    assert "evidence_records" in data
    assert "correlated_assets" in data


def test_scan_nonexistent_directory():
    response = client.post(
        "/scan",
        json={
            "application": "test-app",
            "root_dir": "this_directory_should_not_exist_12345"
        }
    )

    assert response.status_code == 400


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "signatures_loaded" in data