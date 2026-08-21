import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

class Specificity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SignalType(str, Enum):
    EXISTENCE = "existence"
    USAGE = "usage"

class SourceType(str, Enum):
    SOURCE_CODE = "source_code"
    CONFIG = "config"
    IAC = "iac"
    RUNTIME_LOG = "runtime_log"
    CALL_RELATIONSHIP = "call_relationship"

class AssetStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    DISCOVERED = "discovered"

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application: str
    source_type: SourceType
    source_path: str
    line_number: Optional[int] = None
    log_ref: Optional[str] = None
    matched_signature: str
    provider: Optional[str] = None
    model: Optional[str] = None
    ai_type: Optional[str] = None
    confidence_weight: float = Field(ge=0.0, le=1.0)
    specificity: Specificity
    signal_type: SignalType

    @model_validator(mode="after")
    def validate_location(self):
        # Ensure either line_number or log_ref is present for non-connective evidence sources
        if self.source_type != SourceType.CALL_RELATIONSHIP and self.line_number is None and self.log_ref is None:
            raise ValueError("Either line_number or log_ref must be provided")
        return self

class AIAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application: str
    provider: str
    ai_type: str
    model: Optional[str] = None
    status: AssetStatus
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str
    evidence_ids: List[str] = Field(default_factory=list)

class CallEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application: str
    source_file: str
    source_symbol: str
    target_file: str
    target_symbol: str

class ScanRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application: str
    status: ScanStatus
    started_at: datetime
    completed_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")
        if self.completed_at is not None:
            if self.completed_at.tzinfo is None:
                raise ValueError("completed_at must be timezone-aware")
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot be before started_at")
        return self
