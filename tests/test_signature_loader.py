from app.config import settings
from app.services.signature_loader import load_signatures_from_yaml, Signature

def test_load_signatures_success():
    # Verify the actual signatures.yaml loads successfully
    signatures = load_signatures_from_yaml(settings.signatures_path)
    assert isinstance(signatures, list)
    assert len(signatures) > 0
    
    # Verify loaded signatures conform to the expected schema and required fields are present
    for sig in signatures:
        assert isinstance(sig, Signature)
        assert isinstance(sig.id, str) and len(sig.id) > 0
        assert isinstance(sig.provider, str) and len(sig.provider) > 0
        assert isinstance(sig.model_pattern, str) and len(sig.model_pattern) > 0
        assert isinstance(sig.ai_type, str) and len(sig.ai_type) > 0
        assert sig.specificity in ("low", "medium", "high")
        assert 0.0 <= sig.confidence_weight <= 1.0
        assert isinstance(sig.applicable_source_types, list)
        for source_type in sig.applicable_source_types:
            assert isinstance(source_type, str) and len(source_type) > 0
