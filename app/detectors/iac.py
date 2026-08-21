import re
import fnmatch
from typing import List
from app.models import Evidence, SourceType, Specificity, SignalType
from app.services.signature_loader import Signature

# Matches 'resource "aws_bedrock_agent" "example"'
RESOURCE_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')

def detect_iac(
    content: str,
    source_path: str,
    application: str,
    signatures: List[Signature]
) -> List[Evidence]:
    """Detects AI resource definitions in Terraform (.tf) files."""
    if not source_path.lower().endswith('.tf'):
        return []
        
    evidence_list = []
    seen_evidence = set()
    
    try:
        for idx, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            # Ignore comments
            if line.startswith(('#', '//', '/*')):
                continue
                
            match = RESOURCE_RE.search(line)
            if match:
                resource_type = match.group(1)
                
                # Check against loaded signatures
                for sig in signatures:
                    if "iac" not in sig.applicable_source_types:
                        continue
                    if not sig.iac_resource_patterns:
                        continue
                        
                    matched = False
                    for pattern in sig.iac_resource_patterns:
                        if fnmatch.fnmatch(resource_type.lower(), pattern.lower()):
                            matched = True
                            break
                            
                    if matched:
                        evidence_key = (sig.id, idx, None)
                        if evidence_key not in seen_evidence:
                            seen_evidence.add(evidence_key)
                            evidence_list.append(
                                Evidence(
                                    application=application,
                                    source_type=SourceType.IAC,
                                    source_path=source_path,
                                    line_number=idx,
                                    matched_signature=sig.id,
                                    provider=sig.provider,
                                    model=None,
                                    ai_type=sig.ai_type,
                                    confidence_weight=sig.confidence_weight,
                                    specificity=Specificity(sig.specificity),
                                    signal_type=SignalType.EXISTENCE
                                )
                            )
    except Exception:
        # Gracefully handle unreadable or invalid content
        return []
        
    return evidence_list
