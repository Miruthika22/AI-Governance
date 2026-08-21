import json
import yaml
import fnmatch
from typing import List, Dict, Any, Tuple
from app.models import Evidence, SourceType, Specificity, SignalType
from app.services.signature_loader import Signature

def flatten_dict(d: Any, prefix: str = "") -> List[Tuple[str, Any]]:
    """Flattens a nested dictionary to a list of (key_path, value) tuples."""
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            items.extend(flatten_dict(v, new_key))
    elif isinstance(d, list):
        for idx, val in enumerate(d):
            new_key = f"{prefix}[{idx}]"
            items.extend(flatten_dict(val, new_key))
    else:
        items.append((prefix, d))
    return items

def parse_env_file(content: str) -> List[Tuple[str, Any, int]]:
    """Parses .env file content line by line, capturing line numbers."""
    pairs = []
    for idx, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            parts = line.split('=', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            # Strip quotes if present
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            pairs.append((k, v, idx))
    return pairs

def detect_config(
    content: str,
    source_path: str,
    application: str,
    signatures: List[Signature]
) -> List[Evidence]:
    """Detects AI evidence in configuration files (.json, .yaml, .yml, .env)."""
    path_lower = source_path.lower()
    pairs: List[Tuple[str, Any, Any]] = []
    
    # 1. Parse content based on file type
    try:
        if path_lower.endswith(('.yaml', '.yml')):
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                for k, v in flatten_dict(data):
                    pairs.append((k, v, None))
        elif path_lower.endswith('.json'):
            data = json.loads(content)
            if isinstance(data, dict):
                for k, v in flatten_dict(data):
                    pairs.append((k, v, None))
        elif path_lower.endswith('.env') or path_lower.endswith('env'):
            for k, v, lineno in parse_env_file(content):
                pairs.append((k, v, lineno))
        else:
            return []
    except Exception:
        # Gracefully handle unparseable configuration files
        return []

    evidence_list = []
    seen_evidence = set()

    # 2. Signature matching
    for sig in signatures:
        if "config" not in sig.applicable_source_types:
            continue
        if not sig.config_key_patterns:
            continue

        for k, v, lineno in pairs:
            val_str = str(v)
            
            # Check if key (or final key segment) matches any pattern
            key_matched = False
            for kp in sig.config_key_patterns:
                if fnmatch.fnmatch(k.lower(), kp.lower()) or fnmatch.fnmatch(k.split('.')[-1].lower(), kp.lower()):
                    key_matched = True
                    break
            
            if not key_matched:
                continue

            # Must match value as well: either specific model pattern or provider name
            val_matched = False
            is_model_specific = sig.model_pattern != "*"
            
            if is_model_specific:
                if fnmatch.fnmatch(val_str.lower(), sig.model_pattern.lower()):
                    val_matched = True
            else:
                if val_str.lower() == sig.provider.lower():
                    val_matched = True

            if not val_matched:
                continue

            # Build Evidence (SignalType.USAGE for model specific, SignalType.EXISTENCE for generic)
            sig_type = SignalType.USAGE if is_model_specific else SignalType.EXISTENCE
            model_val = val_str if is_model_specific else None
            evidence_log_ref = f"key:{k}" if lineno is None else None

            evidence_key = (sig.id, lineno, model_val)
            if evidence_key not in seen_evidence:
                seen_evidence.add(evidence_key)
                evidence_list.append(
                    Evidence(
                        application=application,
                        source_type=SourceType.CONFIG,
                        source_path=source_path,
                        line_number=lineno,
                        log_ref=evidence_log_ref,
                        matched_signature=sig.id,
                        provider=sig.provider,
                        model=model_val,
                        ai_type=sig.ai_type,
                        confidence_weight=sig.confidence_weight,
                        specificity=Specificity(sig.specificity),
                        signal_type=sig_type
                    )
                )

    return evidence_list
