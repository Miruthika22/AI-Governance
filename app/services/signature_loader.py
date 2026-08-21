import yaml
from typing import List, Literal, Optional
from pathlib import Path
from pydantic import BaseModel, Field

class Signature(BaseModel):
    id: str
    provider: str
    model_pattern: str
    ai_type: str
    specificity: Literal["low", "medium", "high"]
    confidence_weight: float = Field(ge=0.0, le=1.0)
    applicable_source_types: List[str]
    config_key_patterns: Optional[List[str]] = None
    iac_resource_patterns: Optional[List[str]] = None

def load_signatures_from_yaml(file_path: Path) -> List[Signature]:
    """Loads and validates signatures from a YAML file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Signatures file not found at: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    if data is None:
        return []
        
    if not isinstance(data, list):
        raise ValueError("Signatures YAML must be a list of signature objects")
        
    return [Signature(**item) for item in data]
