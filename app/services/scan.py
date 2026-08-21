from pathlib import Path
from typing import List, Union
from pydantic import BaseModel
from app.config import settings
from app.models import Evidence, AIAsset
from app.services.signature_loader import load_signatures_from_yaml
from app.collectors.source_code import collect_source_code
from app.detectors.source_code import detect_source_code
from app.collectors.config import collect_config
from app.detectors.config import detect_config
from app.collectors.iac import collect_iac
from app.detectors.iac import detect_iac
from app.correlator.correlator import correlate_evidence

class ScanResult(BaseModel):
    application: str
    scanned_file_count: int
    supported_file_count: int
    evidence_records: List[Evidence]
    correlated_assets: List[AIAsset]

def run_discovery_scan(application: str, root_dir: Union[str, Path]) -> ScanResult:
    """Orchestrates recursive directory walking, collector/detector routing, and correlation."""
    root_path = Path(root_dir)
    if not root_path.exists():
        raise FileNotFoundError(f"Root directory not found: {root_dir}")
        
    signatures = load_signatures_from_yaml(settings.signatures_path)
    
    scanned_file_count = 0
    supported_file_count = 0
    evidence_records: List[Evidence] = []
    
    # Supported file mappings to collector & detector
    supported_extensions = {
        '.py': (collect_source_code, detect_source_code),
        '.yaml': (collect_config, detect_config),
        '.yml': (collect_config, detect_config),
        '.json': (collect_config, detect_config),
        '.env': (collect_config, detect_config),
        '.tf': (collect_iac, detect_iac)
    }
    
    for p in root_path.rglob('*'):
        if p.is_file():
            scanned_file_count += 1
            ext = p.suffix.lower()
            if p.name.lower() == '.env':
                ext = '.env'
                
            if ext in supported_extensions:
                supported_file_count += 1
                collector, detector = supported_extensions[ext]
                
                try:
                    collected = collector(p)
                    file_evidence = detector(
                        content=collected["content"],
                        source_path=collected["source_path"],
                        application=application,
                        signatures=signatures
                    )
                    evidence_records.extend(file_evidence)
                except Exception as e:
                    # Gracefully skip failures for individual files
                    print(f"Warning: Skipping file {p} due to processing error: {e}")
                    
    correlated_assets = correlate_evidence(evidence_records)
    
    return ScanResult(
        application=application,
        scanned_file_count=scanned_file_count,
        supported_file_count=supported_file_count,
        evidence_records=evidence_records,
        correlated_assets=correlated_assets
    )

class EnvironmentScanResult(BaseModel):
    root_dir: str
    application_count: int
    scanned_file_count: int
    supported_file_count: int
    evidence_records: List[Evidence]
    correlated_assets: List[AIAsset]
    application_results: List[ScanResult]

def run_environment_scan(root_dir: Union[str, Path]) -> EnvironmentScanResult:
    """
    Scans a parent environment directory containing multiple application
    subdirectories. Each immediate subdirectory is treated as one application
    and scanned via the existing run_discovery_scan (unchanged), then results
    are merged into a single EnvironmentScanResult.
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        raise FileNotFoundError(f"Root directory not found: {root_dir}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root_dir}")

    application_dirs = sorted(
        [p for p in root_path.iterdir() if p.is_dir()],
        key=lambda p: p.name
    )

    if not application_dirs:
        raise FileNotFoundError(
            f"No application subdirectories found under: {root_dir}"
        )

    application_results: List[ScanResult] = []
    all_evidence: List[Evidence] = []
    all_assets: List[AIAsset] = []
    total_scanned = 0
    total_supported = 0

    for app_dir in application_dirs:
        result = run_discovery_scan(application=app_dir.name, root_dir=app_dir)
        application_results.append(result)
        all_evidence.extend(result.evidence_records)
        all_assets.extend(result.correlated_assets)
        total_scanned += result.scanned_file_count
        total_supported += result.supported_file_count

    return EnvironmentScanResult(
        root_dir=str(root_path),
        application_count=len(application_results),
        scanned_file_count=total_scanned,
        supported_file_count=total_supported,
        evidence_records=all_evidence,
        correlated_assets=all_assets,
        application_results=application_results
    )