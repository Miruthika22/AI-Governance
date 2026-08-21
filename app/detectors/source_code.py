import ast
import fnmatch
from typing import List
from app.models import Evidence, SourceType, Specificity, SignalType
from app.services.signature_loader import Signature

def detect_source_code(
    content: str, 
    source_path: str, 
    application: str, 
    signatures: List[Signature]
) -> List[Evidence]:
    """Parses Python source using AST and matches signatures to generate Evidence."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # Invalid syntax must return no evidence and handle gracefully
        return []
    
    # 1. Extract imports and string constants from AST
    imported_packages = {}
    string_constants = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                pkg_name = name.name.split('.')[0].lower()
                if pkg_name not in imported_packages:
                    imported_packages[pkg_name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkg_name = node.module.split('.')[0].lower()
                if pkg_name not in imported_packages:
                    imported_packages[pkg_name] = node.lineno
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                string_constants.append((node.value, node.lineno))
    
    evidence_list = []
    seen_evidence = set()  # To avoid duplicate evidence records (signature_id, line_number, model)
    
    # 2. Match with registry signatures
    for sig in signatures:
        if "source_code" not in sig.applicable_source_types:
            continue
        
        # Check if provider name or signature ID contains any imported module name
        matched_pkg = None
        for pkg in imported_packages:
            if pkg in sig.id.lower() or pkg in sig.provider.lower():
                matched_pkg = pkg
                break
        
        if not matched_pkg:
            continue
        
        import_lineno = imported_packages[matched_pkg]
        
        if sig.model_pattern == "*":
            # Existence signal
            key = (sig.id, import_lineno, None)
            if key not in seen_evidence:
                seen_evidence.add(key)
                evidence_list.append(
                    Evidence(
                        application=application,
                        source_type=SourceType.SOURCE_CODE,
                        source_path=source_path,
                        line_number=import_lineno,
                        matched_signature=sig.id,
                        provider=sig.provider,
                        model=None,
                        ai_type=sig.ai_type,
                        confidence_weight=sig.confidence_weight,
                        specificity=Specificity(sig.specificity),
                        signal_type=SignalType.EXISTENCE
                    )
                )
        else:
            # Usage signal: search for string literal matching model pattern
            for val, lineno in string_constants:
                if fnmatch.fnmatch(val.lower(), sig.model_pattern.lower()):
                    key = (sig.id, lineno, val)
                    if key not in seen_evidence:
                        seen_evidence.add(key)
                        evidence_list.append(
                            Evidence(
                                application=application,
                                source_type=SourceType.SOURCE_CODE,
                                source_path=source_path,
                                line_number=lineno,
                                matched_signature=sig.id,
                                provider=sig.provider,
                                model=val,
                                ai_type=sig.ai_type,
                                confidence_weight=sig.confidence_weight,
                                specificity=Specificity(sig.specificity),
                                signal_type=SignalType.USAGE
                            )
                        )
                        
    return evidence_list
