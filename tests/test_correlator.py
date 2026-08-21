import pytest
from app.models import Evidence, SourceType, Specificity, SignalType, AssetStatus
from app.correlator import correlate_evidence

def test_one_weak_evidence_signal():
    ev = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.3,
        specificity=Specificity.LOW,
        signal_type=SignalType.USAGE
    )
    assets = correlate_evidence([ev])
    assert len(assets) == 1
    asset = assets[0]
    assert asset.status == AssetStatus.PENDING_REVIEW
    assert asset.confidence == 0.3
    assert "insufficient confidence" in asset.confidence_rationale.lower()
    assert "insufficient independent source types" in asset.confidence_rationale.lower()
    assert "no high-specificity evidence" in asset.confidence_rationale.lower()

def test_three_source_types_low_medium_specificity():
    ev1 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.MEDIUM,
        signal_type=SignalType.USAGE
    )
    ev2 = Evidence(
        application="app1",
        source_type=SourceType.CONFIG,
        source_path="config.json",
        line_number=None,
        log_ref="key:openai",
        matched_signature="sig2",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.LOW,
        signal_type=SignalType.EXISTENCE
    )
    ev3 = Evidence(
        application="app1",
        source_type=SourceType.IAC,
        source_path="main.tf",
        line_number=10,
        matched_signature="sig3",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.MEDIUM,
        signal_type=SignalType.EXISTENCE
    )
    
    assets = correlate_evidence([ev1, ev2, ev3])
    assert len(assets) == 1
    asset = assets[0]
    assert asset.status == AssetStatus.PENDING_REVIEW
    assert asset.confidence == 0.8
    assert "no high-specificity evidence" in asset.confidence_rationale.lower()
    assert "insufficient" not in asset.confidence_rationale.lower()

def test_high_specificity_insufficient_source_types():
    ev1 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    ev2 = Evidence(
        application="app1",
        source_type=SourceType.CONFIG,
        source_path="config.json",
        line_number=None,
        log_ref="key:openai",
        matched_signature="sig2",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.EXISTENCE
    )
    assets = correlate_evidence([ev1, ev2])
    assert len(assets) == 1
    asset = assets[0]
    assert asset.status == AssetStatus.PENDING_REVIEW
    assert asset.confidence == 0.9
    assert "insufficient independent source types" in asset.confidence_rationale.lower()

def test_valid_asset_discovery():
    ev1 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    ev2 = Evidence(
        application="app1",
        source_type=SourceType.CONFIG,
        source_path="config.json",
        line_number=None,
        log_ref="key:openai",
        matched_signature="sig2",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.7,
        specificity=Specificity.LOW,
        signal_type=SignalType.EXISTENCE
    )
    ev3 = Evidence(
        application="app1",
        source_type=SourceType.IAC,
        source_path="main.tf",
        line_number=10,
        matched_signature="sig3",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.MEDIUM,
        signal_type=SignalType.EXISTENCE
    )
    
    assets = correlate_evidence([ev1, ev2, ev3])
    assert len(assets) == 1
    asset = assets[0]
    assert asset.status == AssetStatus.DISCOVERED
    assert asset.confidence == 0.8
    assert "discovered" in asset.confidence_rationale.lower()

def test_call_relationship_exclusion():
    ev1 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    ev2 = Evidence(
        application="app1",
        source_type=SourceType.CALL_RELATIONSHIP,
        source_path="main.py",
        line_number=None,
        log_ref=None,
        matched_signature="sig2",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    assets = correlate_evidence([ev1, ev2])
    assert len(assets) == 1
    asset = assets[0]
    assert asset.status == AssetStatus.PENDING_REVIEW
    assert "found 1" in asset.confidence_rationale.lower()

def test_grouping_consistency_and_segregation():
    ev1 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=1,
        matched_signature="sig1",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    ev2 = Evidence(
        application="app1",
        source_type=SourceType.CONFIG,
        source_path="config.json",
        line_number=None,
        log_ref="key:openai",
        matched_signature="sig2",
        provider="openai",
        ai_type="llm",
        confidence_weight=0.8,
        specificity=Specificity.LOW,
        signal_type=SignalType.EXISTENCE
    )
    ev3 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=5,
        matched_signature="sig3",
        provider="anthropic",
        ai_type="llm",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    ev4 = Evidence(
        application="app1",
        source_type=SourceType.SOURCE_CODE,
        source_path="main.py",
        line_number=6,
        matched_signature="sig4",
        provider="openai",
        ai_type="image",
        confidence_weight=0.9,
        specificity=Specificity.HIGH,
        signal_type=SignalType.USAGE
    )
    
    assets = correlate_evidence([ev1, ev2, ev3, ev4])
    assert len(assets) == 3
    
    openai_llm = [a for a in assets if a.provider == "openai" and a.ai_type == "llm"][0]
    anthropic_llm = [a for a in assets if a.provider == "anthropic" and a.ai_type == "llm"][0]
    openai_image = [a for a in assets if a.provider == "openai" and a.ai_type == "image"][0]
    
    assert len(openai_llm.evidence_ids) == 2
    assert len(anthropic_llm.evidence_ids) == 1
    assert len(openai_image.evidence_ids) == 1

def test_asset_model_resolution():
    ev1 = Evidence(
        application="app1", source_type=SourceType.SOURCE_CODE, source_path="a.py", line_number=1,
        matched_signature="sig1", provider="openai", ai_type="llm", confidence_weight=0.8,
        specificity=Specificity.HIGH, signal_type=SignalType.USAGE, model="gpt-4"
    )
    ev2 = Evidence(
        application="app1", source_type=SourceType.CONFIG, source_path="b.py", line_number=2,
        matched_signature="sig2", provider="openai", ai_type="llm", confidence_weight=0.8,
        specificity=Specificity.HIGH, signal_type=SignalType.USAGE, model="gpt-4"
    )
    assets = correlate_evidence([ev1, ev2])
    assert assets[0].model == "gpt-4"
    
    ev3 = Evidence(
        application="app1", source_type=SourceType.CONFIG, source_path="c.py", line_number=3,
        matched_signature="sig3", provider="openai", ai_type="llm", confidence_weight=0.8,
        specificity=Specificity.HIGH, signal_type=SignalType.USAGE, model="gpt-3.5"
    )
    assets = correlate_evidence([ev1, ev2, ev3])
    assert assets[0].model is None
    
    ev4 = Evidence(
        application="app1", source_type=SourceType.SOURCE_CODE, source_path="a.py", line_number=1,
        matched_signature="sig1", provider="openai", ai_type="llm", confidence_weight=0.8,
        specificity=Specificity.HIGH, signal_type=SignalType.USAGE, model=None
    )
    assets = correlate_evidence([ev4])
    assert assets[0].model is None
