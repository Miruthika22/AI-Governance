import pytest
import uuid
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.models import (
    Evidence,
    AIAsset,
    CallEdge,
    ScanRun,
    Specificity,
    SignalType,
    SourceType,
    AssetStatus,
    ScanStatus,
)

def test_valid_evidence_creation():
    evidence = Evidence(
        application="test-app",
        source_type=SourceType.SOURCE_CODE,
        source_path="app/main.py",
        line_number=10,
        matched_signature="openai-gpt4-sdk",
        provider="openai",
        confidence_weight=0.8,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    assert evidence.application == "test-app"
    assert evidence.confidence_weight == 0.8
    assert evidence.specificity == Specificity.HIGH
    assert evidence.id is not None
    assert evidence.line_number == 10
    assert evidence.log_ref is None

def test_invalid_confidence_weight_rejected():
    with pytest.raises(ValidationError):
        Evidence(
            application="test-app",
            source_type=SourceType.SOURCE_CODE,
            source_path="app/main.py",
            line_number=10,
            matched_signature="openai-gpt4-sdk",
            confidence_weight=1.5,
            specificity=Specificity.HIGH,
            signal_type=SignalType.USAGE
        )
    with pytest.raises(ValidationError):
        Evidence(
            application="test-app",
            source_type=SourceType.SOURCE_CODE,
            source_path="app/main.py",
            line_number=10,
            matched_signature="openai-gpt4-sdk",
            confidence_weight=-0.1,
            specificity=Specificity.HIGH,
            signal_type=SignalType.USAGE
        )

def test_invalid_specificity_rejected():
    with pytest.raises(ValidationError):
        Evidence(
            application="test-app",
            source_type=SourceType.SOURCE_CODE,
            source_path="app/main.py",
            line_number=10,
            matched_signature="openai-gpt4-sdk",
            confidence_weight=0.5,
            specificity="invalid_spec",
            signal_type=SignalType.USAGE
        )

def test_valid_ai_asset_creation():
    asset = AIAsset(
        application="test-app",
        provider="openai",
        ai_type="llm",
        model="gpt-4",
        status=AssetStatus.DISCOVERED,
        confidence=0.9,
        confidence_rationale="Spans 3 source types with high specificity evidence",
        evidence_ids=["id1", "id2"]
    )
    assert asset.application == "test-app"
    assert asset.status == AssetStatus.DISCOVERED
    assert asset.confidence == 0.9

def test_invalid_asset_status_rejected():
    with pytest.raises(ValidationError):
        AIAsset(
            application="test-app",
            provider="openai",
            ai_type="llm",
            status="invalid_status",
            confidence=0.5,
            confidence_rationale="Reason",
            evidence_ids=[]
        )

def test_valid_call_edge_creation():
    edge = CallEdge(
        application="test-app",
        source_file="app/main.py",
        source_symbol="main",
        target_file="app/services.py",
        target_symbol="call_ai"
    )
    assert edge.source_symbol == "main"
    assert edge.target_symbol == "call_ai"
    assert edge.id is not None

def test_valid_scan_run_creation():
    now = datetime.now(timezone.utc)
    run = ScanRun(
        application="test-app",
        status=ScanStatus.RUNNING,
        started_at=now
    )
    assert run.status == ScanStatus.RUNNING
    assert run.started_at == now
    assert run.completed_at is None

    run.completed_at = now + timedelta(minutes=5)
    assert run.completed_at > run.started_at

def test_scan_run_invalid_timestamps():
    naive_dt = datetime.now()
    with pytest.raises(ValidationError):
        ScanRun(
            application="test-app",
            status=ScanStatus.PENDING,
            started_at=naive_dt
        )

    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        ScanRun(
            application="test-app",
            status=ScanStatus.COMPLETED,
            started_at=now,
            completed_at=now - timedelta(seconds=1)
        )

def test_automatic_uuid_generation():
    evidence = Evidence(
        application="test-app",
        source_type=SourceType.SOURCE_CODE,
        source_path="app/main.py",
        line_number=10,
        matched_signature="sig",
        confidence_weight=0.5,
        specificity=Specificity.LOW,
        signal_type=SignalType.USAGE
    )
    asset = AIAsset(
        application="test-app",
        provider="openai",
        ai_type="llm",
        status=AssetStatus.PENDING_REVIEW,
        confidence=0.5,
        confidence_rationale="Reason"
    )
    edge = CallEdge(
        application="test-app",
        source_file="a.py",
        source_symbol="a",
        target_file="b.py",
        target_symbol="b"
    )
    run = ScanRun(
        application="test-app",
        status=ScanStatus.PENDING,
        started_at=datetime.now(timezone.utc)
    )

    for obj in (evidence, asset, edge, run):
        assert isinstance(obj.id, str)
        val = uuid.UUID(obj.id)
        assert val.version == 4
