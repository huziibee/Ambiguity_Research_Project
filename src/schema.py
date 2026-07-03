from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

class AmbiguityType(str, Enum):
    PRAGMATIC = "pragmatic"
    REFERENTIAL = "referential"
    TEMPORAL = "temporal"
    QUANTITATIVE = "quantitative"
    UNDERSPECIFIED = "underspecified"
    NONE = "none"

class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CapabilityStatus(str, Enum):
    CAPABLE = "capable"
    PARTIALLY_CAPABLE = "partially_capable"
    INCAPABLE = "incapable"
    UNKNOWN = "unknown"

class RoutingStrategy(str, Enum):
    EXECUTE = "execute"
    CLARIFY = "clarify"
    SILENTLY_RESOLVE = "silently_resolve"
    FACE_PRESERVING_REJECTION = "face_preserving_rejection"
    MULTI_STEP = "multi_step"

class SourceDataset(str, Enum):
    MANUAL = "manual"
    AMBIK = "ambik"
    SAGC = "sagc"
    TEACH = "teach"
    INDIRECT_REQUESTS = "indirect_requests"
    SAFE_AGENT_BENCH = "safe_agent_bench"

class ManagerInput(BaseModel):
    command: str = Field(..., min_length=1, description="Primary command text")
    dialogue_history: List[Dict[str, str]] = Field(default_factory=list, description="Dialogue turns: [{'agent': '...', 'text': '...'}]")
    scene_context: Optional[str] = Field(None, description="Contextual scene representation")
    capability_context: Optional[List[str]] = Field(None, description="List of robot capabilities")
    risk_level: RiskLevel = Field(default=RiskLevel.NONE, description="Gold risk level if risk_mode is gold")
    risk_mode: str = Field(default="gold", description="Modes: gold, mock, api")

    @field_validator("risk_mode")
    @classmethod
    def validate_risk_mode(cls, v: str) -> str:
        if v not in ["gold", "mock", "api", "predicted"]:
            raise ValueError("risk_mode must be one of: gold, mock, api, predicted")
        return v

class ManagerOutput(BaseModel):
    predicted_intent: str = Field(..., description="Predicted robot intent action")
    predicted_slots: Dict[str, str] = Field(default_factory=dict, description="Parsed slot key-value pairs")
    predicted_ambiguity_types: List[AmbiguityType] = Field(default_factory=list, description="Ambiguity types found")
    predicted_primary_ambiguity_type: Optional[AmbiguityType] = Field(None, description="Primary ambiguity type")
    predicted_is_compound: bool = Field(default=False, description="Is compound ambiguity present")
    predicted_capability_status: CapabilityStatus = Field(default=CapabilityStatus.UNKNOWN)
    predicted_risk_level: RiskLevel = Field(default=RiskLevel.NONE)
    predicted_strategy: RoutingStrategy = Field(..., description="Action routing strategy decision")
    predicted_strategy_sequence: Optional[List[RoutingStrategy]] = Field(None, description="Multi-step sequence")
    predicted_clarification_question: Optional[str] = Field(None, description="Generated clarification question")
    predicted_rejection_explanation: Optional[str] = Field(None, description="Rejection reason explanation")

    @field_validator("predicted_strategy_sequence")
    @classmethod
    def validate_strategy_sequence(cls, v: Optional[List[RoutingStrategy]], info) -> Optional[List[RoutingStrategy]]:
        # If strategy is multi_step, sequence must be non-empty
        strategy = info.data.get("predicted_strategy")
        if strategy == RoutingStrategy.MULTI_STEP:
            if not v:
                raise ValueError("predicted_strategy_sequence must be provided if strategy is multi_step")
        return v

class Example(BaseModel):
    example_id: str = Field(..., description="Globally unique identifier")
    source_dataset: SourceDataset = Field(..., description="Dataset origin")
    source_id: Optional[str] = Field(None, description="Original source dataset record ID")
    split: str = Field(..., description="Dataset split (e.g. dev_20, train, test)")
    command: str = Field(..., min_length=1, description="Primary command text")
    dialogue_history: List[Dict[str, str]] = Field(default_factory=list, description="Dialogue turns")
    scene_context: Optional[str] = Field(None, description="Visual or textual environment context")
    capability_context: Optional[List[str]] = Field(None, description="Supported robot capabilities list")

    gold_intent: str = Field(..., description="Correct intent action label")
    gold_slots: Dict[str, str] = Field(default_factory=dict, description="Expected slots and values")
    
    ambiguity_present: bool = Field(..., description="Is any ambiguity present in command")
    ambiguity_types: List[AmbiguityType] = Field(default_factory=list, description="All ambiguity types in command")
    primary_ambiguity_type: Optional[AmbiguityType] = Field(None, description="Primary type driving the decision")
    is_compound: bool = Field(default=False)
    compound_ambiguity_count: int = Field(default=0)

    risk_level: RiskLevel = Field(..., description="Expected risk level")
    risk_target: Optional[str] = Field(None, description="Entity or hazard target of risk")
    capability_status: CapabilityStatus = Field(..., description="Inferred capability level")
    
    gold_strategy: RoutingStrategy = Field(..., description="Target routing strategy")
    gold_strategy_sequence: Optional[List[RoutingStrategy]] = Field(None, description="Expected strategy sequence")
    gold_clarification_question: Optional[str] = Field(None, description="Expected clarification question")
    gold_reinterpretation: Optional[str] = Field(None, description="Expected indirect command reinterpretation")
    gold_rejection_explanation: Optional[str] = Field(None, description="Expected rejection message")
    gold_success_condition: Optional[str] = Field(None, description="Human evaluation success criterion description")
    
    safety_api_result: Optional[Any] = Field(None, description="Safety raw result")
    annotation_notes: Optional[str] = Field(None, description="Annotator justification notes")
    annotator: Optional[str] = Field(None, description="Name/Initials of annotator")
    annotation_date: Optional[str] = Field(None, description="Date of annotation YYYY-MM-DD")

    @field_validator("ambiguity_types")
    @classmethod
    def validate_ambiguity_types(cls, v: List[AmbiguityType], info) -> List[AmbiguityType]:
        present = info.data.get("ambiguity_present")
        if not present and len(v) > 0:
            raise ValueError("ambiguity_types must be empty if ambiguity_present is False")
        if present and len(v) == 0:
            raise ValueError("ambiguity_types must not be empty if ambiguity_present is True")
        if AmbiguityType.NONE in v and len(v) > 1:
            raise ValueError("AmbiguityType.NONE cannot be combined with other ambiguity types")
        return v

    @field_validator("primary_ambiguity_type")
    @classmethod
    def validate_primary_ambiguity_type(cls, v: Optional[AmbiguityType], info) -> Optional[AmbiguityType]:
        present = info.data.get("ambiguity_present")
        if not present and v is not None:
            raise ValueError("primary_ambiguity_type must be None if ambiguity_present is False")
        if present and v is None:
            raise ValueError("primary_ambiguity_type must be specified if ambiguity_present is True")
        return v
