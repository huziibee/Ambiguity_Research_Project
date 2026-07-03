from dataclasses import dataclass
from typing import List, Optional

from src.schema import AmbiguityType, CapabilityStatus, RiskLevel, RoutingStrategy


@dataclass(frozen=True)
class AmbiguityResult:
    ambiguity_types: List[AmbiguityType]
    primary_ambiguity_type: Optional[AmbiguityType]
    is_compound: bool

    @property
    def ambiguity_present(self) -> bool:
        return bool(self.ambiguity_types)


@dataclass(frozen=True)
class CapabilityResult:
    status: CapabilityStatus


@dataclass(frozen=True)
class RoutingDecision:
    strategy: RoutingStrategy
    reason: str
    strategy_sequence: Optional[List[RoutingStrategy]] = None


class TypeRiskRouter:
    """Explicit type/risk/capability router from the Phase 1 plan."""

    def route(
        self,
        ambiguity: AmbiguityResult,
        risk_level: RiskLevel,
        capability: CapabilityResult,
    ) -> RoutingDecision:
        if capability.status == CapabilityStatus.INCAPABLE:
            return RoutingDecision(
                RoutingStrategy.FACE_PRESERVING_REJECTION,
                "Robot lacks required capabilities",
            )

        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) and self._is_unsafe(
            ambiguity
        ):
            return RoutingDecision(
                RoutingStrategy.FACE_PRESERVING_REJECTION,
                "High risk: unsafe to proceed without confirmation",
            )

        if not ambiguity.ambiguity_present:
            return RoutingDecision(RoutingStrategy.EXECUTE, "Clear, safe, capable command")

        if ambiguity.is_compound:
            return RoutingDecision(
                RoutingStrategy.MULTI_STEP,
                "Compound ambiguity: ordered resolution needed",
                self._build_strategy_sequence(ambiguity, risk_level),
            )

        primary = ambiguity.primary_ambiguity_type
        if primary in (AmbiguityType.REFERENTIAL, AmbiguityType.UNDERSPECIFIED):
            return RoutingDecision(
                RoutingStrategy.CLARIFY,
                f"{primary.value}: missing critical information",
            )

        if primary in (AmbiguityType.TEMPORAL, AmbiguityType.QUANTITATIVE):
            if risk_level in (RiskLevel.NONE, RiskLevel.LOW):
                return RoutingDecision(
                    RoutingStrategy.SILENTLY_RESOLVE,
                    f"{primary.value}, low risk: ground internally",
                )
            return RoutingDecision(
                RoutingStrategy.CLARIFY,
                f"{primary.value}, elevated risk: ask user",
            )

        if primary == AmbiguityType.PRAGMATIC:
            if risk_level in (RiskLevel.NONE, RiskLevel.LOW):
                return RoutingDecision(
                    RoutingStrategy.SILENTLY_RESOLVE,
                    "ISA, low risk: reinterpret pragmatically",
                )
            return RoutingDecision(
                RoutingStrategy.CLARIFY,
                "ISA, elevated risk: confirm interpretation",
            )

        return RoutingDecision(RoutingStrategy.CLARIFY, "Uncertain: default to clarification")

    def _is_unsafe(self, ambiguity: AmbiguityResult) -> bool:
        # ponytail: referential high-risk cases can be clarified to avoid the unsafe option.
        return not ambiguity.ambiguity_present or (
            AmbiguityType.REFERENTIAL not in ambiguity.ambiguity_types
        )

    def _build_strategy_sequence(
        self, ambiguity: AmbiguityResult, risk_level: RiskLevel
    ) -> List[RoutingStrategy]:
        sequence: List[RoutingStrategy] = []
        types = set(ambiguity.ambiguity_types)
        if AmbiguityType.PRAGMATIC in types:
            sequence.append(RoutingStrategy.SILENTLY_RESOLVE)
        if AmbiguityType.REFERENTIAL in types or AmbiguityType.UNDERSPECIFIED in types:
            sequence.append(RoutingStrategy.CLARIFY)
        if AmbiguityType.TEMPORAL in types or AmbiguityType.QUANTITATIVE in types:
            if risk_level in (RiskLevel.NONE, RiskLevel.LOW):
                sequence.append(RoutingStrategy.SILENTLY_RESOLVE)
            else:
                sequence.append(RoutingStrategy.CLARIFY)
        return sequence or [RoutingStrategy.CLARIFY]
