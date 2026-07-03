from src.manager.pipeline import (
    build_output,
    classify_ambiguity,
    infer_capability,
    infer_intent,
    infer_risk,
)
from src.baselines.llm_client import llm_predict
from src.schema import (
    AmbiguityType,
    CapabilityStatus,
    ManagerInput,
    ManagerOutput,
    RiskLevel,
    RoutingStrategy,
)


class DirectLLM:
    name = "direct_llm"

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        output = llm_predict(input_data)
        if output is not None:
            return output
        intent = infer_intent(input_data.command)
        ambiguity = classify_ambiguity(input_data.command, input_data.scene_context)
        risk = infer_risk(input_data)
        capability = infer_capability(intent, input_data)
        types = set(ambiguity.ambiguity_types)

        if capability.status == CapabilityStatus.INCAPABLE:
            strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
        elif risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
        elif AmbiguityType.REFERENTIAL in types:
            strategy = RoutingStrategy.CLARIFY
        elif risk == RiskLevel.MEDIUM and ambiguity.ambiguity_present:
            strategy = RoutingStrategy.CLARIFY
        elif AmbiguityType.UNDERSPECIFIED in types:
            strategy = RoutingStrategy.CLARIFY
        elif ambiguity.ambiguity_present:
            strategy = RoutingStrategy.SILENTLY_RESOLVE
        else:
            strategy = RoutingStrategy.EXECUTE

        return build_output(
            input_data,
            strategy,
            ambiguity=ambiguity,
            intent=intent,
            risk_level=risk,
            capability=capability,
        )
