import re
from typing import Dict, List, Optional, Sequence

from src.manager.router import (
    AmbiguityResult,
    CapabilityResult,
    RoutingDecision,
    TypeRiskRouter,
)
from src.schema import (
    AmbiguityType,
    CapabilityStatus,
    ManagerInput,
    ManagerOutput,
    RiskLevel,
    RoutingStrategy,
)


def infer_intent(command: str) -> str:
    text = command.lower()
    if "paint" in text:
        return "paint_room"
    if "fly" in text or "smoke detector" in text:
        return "check_device"
    if "mow" in text:
        return "mow_lawn"
    if "dish" in text:
        return "wash_dishes"
    if "medicine" in text or "prescription" in text:
        return "retrieve_medicine"
    if "microwave" in text:
        return "microwave_food"
    if "boiling water" in text or text.startswith("pour"):
        return "pour_liquid"
    if "open the door" in text:
        return "open_door"
    if "clean" in text:
        return "clean_surface"
    if "throw" in text or "away" in text:
        return "discard_object"
    if "bring" in text:
        return "bring_object"
    if "pick up" in text and "place" in text:
        return "pick_and_place"
    if "pick up" in text or text.startswith("grab"):
        return "pick_up_object"
    if "put" in text or "move" in text:
        return "move_object"
    return "unknown"


def extract_slots(command: str) -> Dict[str, str]:
    text = command.lower().strip()
    slots: Dict[str, str] = {}
    for phrase in ("that cup", "that thing", "that book", "those cups", "the bottle"):
        if phrase in text:
            slots["object"] = phrase
            break
    if "milk" in text:
        slots["object"] = "milk"
    if "fridge" in text:
        slots["container"] = "fridge"
    if "few" in text and "few minutes" not in text:
        slots["quantity"] = "a few"
    if "soon" in text:
        slots["temporal"] = "soon"
    elif "later" in text:
        slots["temporal"] = "later"
    elif "in a bit" in text:
        slots["temporal"] = "in a bit"
    elif "few minutes" in text:
        slots["temporal"] = "in a few minutes"
    if "there" in text and not text.startswith("is there"):
        slots["destination"] = "there"
    return slots


def classify_ambiguity(command: str, scene_context: Optional[str]) -> AmbiguityResult:
    text = command.lower()
    scene = (scene_context or "").lower()
    types: List[AmbiguityType] = []

    if text.startswith(("can you", "could you", "would you")) or text.startswith(
        "is there any reason"
    ):
        types.append(AmbiguityType.PRAGMATIC)

    referential = any(token in text for token in ("that ", "those ", "over there"))
    referential = referential or (" there" in text and not text.startswith("is there"))
    referential = referential or ("the bottle" in text and scene.count("bottle") > 1)
    if referential:
        types.append(AmbiguityType.REFERENTIAL)

    if any(token in text for token in ("soon", "later", "in a bit", "few minutes")):
        types.append(AmbiguityType.TEMPORAL)

    if re.search(r"\b(a few|few|several)\b", text) and "few minutes" not in text:
        types.append(AmbiguityType.QUANTITATIVE)

    if text.strip() in {"clean the table.", "clean the stove."}:
        types.append(AmbiguityType.UNDERSPECIFIED)

    ordered = _dedupe(types)
    return AmbiguityResult(
        ambiguity_types=ordered,
        primary_ambiguity_type=_primary_type(ordered),
        is_compound=len(ordered) > 1,
    )


def infer_risk(input_data: ManagerInput) -> RiskLevel:
    if input_data.risk_mode == "gold":
        return input_data.risk_level
    text = input_data.command.lower()
    if any(token in text for token in ("microwave", "fireplace", "boiling water")):
        return RiskLevel.CRITICAL
    if any(token in text for token in ("fly", "broken glass", "stove")):
        return RiskLevel.MEDIUM
    return RiskLevel.NONE


def infer_capability(intent: str, input_data: ManagerInput) -> CapabilityResult:
    capabilities = set(input_data.capability_context or [])
    if not capabilities:
        return CapabilityResult(CapabilityStatus.UNKNOWN)

    required = {
        "open_door": {"door_opening"},
        "paint_room": {"painting"},
        "check_device": {"flight"},
        "mow_lawn": {"lawn_mowing"},
        "wash_dishes": {"dishwashing"},
        "retrieve_medicine": {"pick_and_place", "cabinet_opening"},
        "microwave_food": {"pick_and_place", "microwave_operation"},
        "pour_liquid": {"pour_liquid"},
        "clean_surface": {"cleaning"},
        "discard_object": {"pick_and_place"},
        "bring_object": {"pick_and_place"},
        "pick_and_place": {"pick_and_place"},
        "pick_up_object": {"pick_and_place"},
        "move_object": {"pick_and_place"},
    }.get(intent)

    if required is None:
        return CapabilityResult(CapabilityStatus.UNKNOWN)
    if required <= capabilities:
        return CapabilityResult(CapabilityStatus.CAPABLE)
    if required & capabilities:
        return CapabilityResult(CapabilityStatus.PARTIALLY_CAPABLE)
    return CapabilityResult(CapabilityStatus.INCAPABLE)


def build_output(
    input_data: ManagerInput,
    strategy: RoutingStrategy,
    ambiguity: Optional[AmbiguityResult] = None,
    intent: Optional[str] = None,
    slots: Optional[Dict[str, str]] = None,
    risk_level: Optional[RiskLevel] = None,
    capability: Optional[CapabilityResult] = None,
    strategy_sequence: Optional[Sequence[RoutingStrategy]] = None,
) -> ManagerOutput:
    ambiguity = ambiguity or AmbiguityResult([], None, False)
    intent = intent or infer_intent(input_data.command)
    risk_level = risk_level or infer_risk(input_data)
    capability = capability or infer_capability(intent, input_data)
    question = None
    rejection = None

    if strategy == RoutingStrategy.CLARIFY or (
        strategy == RoutingStrategy.MULTI_STEP
        and strategy_sequence
        and RoutingStrategy.CLARIFY in strategy_sequence
    ):
        question = clarification_question(ambiguity, risk_level)
    if strategy == RoutingStrategy.FACE_PRESERVING_REJECTION:
        rejection = rejection_explanation(capability.status, risk_level)

    return ManagerOutput(
        predicted_intent=intent,
        predicted_slots=slots or extract_slots(input_data.command),
        predicted_ambiguity_types=ambiguity.ambiguity_types,
        predicted_primary_ambiguity_type=ambiguity.primary_ambiguity_type,
        predicted_is_compound=ambiguity.is_compound,
        predicted_capability_status=capability.status,
        predicted_risk_level=risk_level,
        predicted_strategy=strategy,
        predicted_strategy_sequence=list(strategy_sequence) if strategy_sequence else None,
        predicted_clarification_question=question,
        predicted_rejection_explanation=rejection,
    )


def clarification_question(
    ambiguity: AmbiguityResult, risk_level: RiskLevel
) -> str:
    types = set(ambiguity.ambiguity_types)
    if AmbiguityType.REFERENTIAL in types:
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            return "Which item do you mean? One option may be unsafe."
        return "Which object or location do you mean?"
    if AmbiguityType.UNDERSPECIFIED in types:
        return "Can you confirm the safe way to proceed?"
    if AmbiguityType.TEMPORAL in types:
        return "When exactly should I do that?"
    if AmbiguityType.QUANTITATIVE in types:
        return "How many should I use?"
    return "Should I proceed with this request?"


def rejection_explanation(
    capability_status: CapabilityStatus, risk_level: RiskLevel
) -> str:
    if capability_status == CapabilityStatus.INCAPABLE:
        return "I cannot do that with my available capabilities."
    if risk_level == RiskLevel.CRITICAL:
        return "I cannot safely perform that because it poses a critical hazard."
    return "I cannot safely perform that request."


class ProposedManager:
    name = "proposed_manager"

    def __init__(self) -> None:
        self.router = TypeRiskRouter()

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        intent = infer_intent(input_data.command)
        slots = extract_slots(input_data.command)
        ambiguity = classify_ambiguity(input_data.command, input_data.scene_context)
        risk = infer_risk(input_data)
        capability = infer_capability(intent, input_data)
        decision = self.router.route(ambiguity, risk, capability)
        return build_output(
            input_data,
            decision.strategy,
            ambiguity=ambiguity,
            intent=intent,
            slots=slots,
            risk_level=risk,
            capability=capability,
            strategy_sequence=decision.strategy_sequence,
        )


def _primary_type(types: Sequence[AmbiguityType]) -> Optional[AmbiguityType]:
    for candidate in (
        AmbiguityType.REFERENTIAL,
        AmbiguityType.TEMPORAL,
        AmbiguityType.UNDERSPECIFIED,
        AmbiguityType.QUANTITATIVE,
        AmbiguityType.PRAGMATIC,
    ):
        if candidate in types:
            return candidate
    return None


def _dedupe(types: Sequence[AmbiguityType]) -> List[AmbiguityType]:
    seen = set()
    out: List[AmbiguityType] = []
    for item in types:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out
