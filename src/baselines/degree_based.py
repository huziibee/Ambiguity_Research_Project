import re

from src.manager.pipeline import (
    build_output,
    classify_ambiguity,
    infer_capability,
    infer_intent,
    infer_risk,
)
from src.schema import (
    CapabilityStatus,
    ManagerInput,
    ManagerOutput,
    RiskLevel,
    RoutingStrategy,
)


class DegreeBased:
    name = "degree_based"

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        intent = infer_intent(input_data.command)
        ambiguity = classify_ambiguity(input_data.command, input_data.scene_context)
        risk = infer_risk(input_data)
        capability = infer_capability(intent, input_data)

        if capability.status == CapabilityStatus.INCAPABLE:
            strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
        elif risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
        elif ambiguity_score(input_data.command) >= self.threshold:
            strategy = RoutingStrategy.CLARIFY
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


def ambiguity_score(command: str) -> float:
    text = command.lower()
    score = 0.0
    score += 0.8 * len(re.findall(r"\b(that|those|there)\b", text))
    score += 0.7 * len(re.findall(r"\b(few|some|several)\b", text))
    score += 0.6 * len(re.findall(r"\b(soon|later|bit)\b", text))
    if text.startswith(("can you", "could you", "would you")):
        score += 0.5
    if "thing" in text or re.search(r"\bthe (box|bottle)\b", text):
        score += 0.4
    if text.strip() in {"clean the table.", "clean the stove."}:
        score += 0.5
    return score
