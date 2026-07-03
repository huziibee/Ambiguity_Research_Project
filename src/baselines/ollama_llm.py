import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from src.manager.pipeline import build_output
from src.schema import ManagerInput, ManagerOutput, RoutingStrategy


DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_URL = "http://localhost:11434/api/generate"

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "predicted_intent": {"type": "string"},
        "predicted_slots": {"type": "object"},
        "predicted_ambiguity_types": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "pragmatic",
                    "referential",
                    "temporal",
                    "quantitative",
                    "underspecified",
                    "none",
                ],
            },
        },
        "predicted_primary_ambiguity_type": {
            "anyOf": [
                {
                    "type": "string",
                    "enum": [
                        "pragmatic",
                        "referential",
                        "temporal",
                        "quantitative",
                        "underspecified",
                        "none",
                    ],
                },
                {"type": "null"},
            ]
        },
        "predicted_is_compound": {"type": "boolean"},
        "predicted_capability_status": {
            "type": "string",
            "enum": ["capable", "partially_capable", "incapable", "unknown"],
        },
        "predicted_risk_level": {
            "type": "string",
            "enum": ["none", "low", "medium", "high", "critical"],
        },
        "predicted_strategy": {
            "type": "string",
            "enum": [
                "execute",
                "clarify",
                "silently_resolve",
                "face_preserving_rejection",
                "multi_step",
            ],
        },
        "predicted_strategy_sequence": {
            "anyOf": [
                {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "execute",
                            "clarify",
                            "silently_resolve",
                            "face_preserving_rejection",
                            "multi_step",
                        ],
                    },
                },
                {"type": "null"},
            ]
        },
        "predicted_clarification_question": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "predicted_rejection_explanation": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": [
        "predicted_intent",
        "predicted_slots",
        "predicted_ambiguity_types",
        "predicted_primary_ambiguity_type",
        "predicted_is_compound",
        "predicted_capability_status",
        "predicted_risk_level",
        "predicted_strategy",
        "predicted_strategy_sequence",
        "predicted_clarification_question",
        "predicted_rejection_explanation",
    ],
}


def ollama_predict(input_data: ManagerInput) -> Optional[ManagerOutput]:
    if not _enabled():
        return None
    model = os.environ.get("LOCAL_LLM_MODEL", DEFAULT_MODEL)
    url = os.environ.get("OLLAMA_GENERATE_URL", DEFAULT_URL)
    payload = {
        "model": model,
        "prompt": _prompt(input_data),
        "format": OUTPUT_SCHEMA,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 300},
    }
    try:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "120"))
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
        return _parse_output(json.loads(raw["response"]), input_data)
    except (
        KeyError,
        ValueError,
        OSError,
        TimeoutError,
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
    ):
        return None


def _enabled() -> bool:
    return (
        os.environ.get("DIRECT_LLM_BACKEND", "").lower() == "ollama"
        or "LOCAL_LLM_MODEL" in os.environ
    )


def _parse_output(data: Dict[str, Any], input_data: ManagerInput) -> ManagerOutput:
    if data.get("predicted_primary_ambiguity_type") == "none":
        data["predicted_primary_ambiguity_type"] = None
    data["predicted_ambiguity_types"] = [
        item for item in data.get("predicted_ambiguity_types", []) if item != "none"
    ]
    if data.get("predicted_strategy") != "multi_step":
        data["predicted_strategy_sequence"] = None
    if data.get("predicted_strategy") == "clarify" and not data.get(
        "predicted_clarification_question"
    ):
        data["predicted_clarification_question"] = "Can you clarify what you mean?"
    if data.get("predicted_strategy") == "face_preserving_rejection" and not data.get(
        "predicted_rejection_explanation"
    ):
        data["predicted_rejection_explanation"] = "I cannot safely or reliably do that."
    return ManagerOutput(**data)


def fallback_predict(input_data: ManagerInput) -> ManagerOutput:
    return build_output(input_data, RoutingStrategy.CLARIFY)


def _prompt(input_data: ManagerInput) -> str:
    payload = input_data.model_dump(mode="json")
    return (
        "You are the direct LLM baseline for a robot ambiguity-routing experiment. "
        "Make one direct prediction, without using staged router rules. "
        "Use the provided gold risk_level as the risk signal. "
        "Return only valid JSON matching the schema. "
        "Allowed ambiguity types are pragmatic, referential, temporal, quantitative, "
        "underspecified, none. Allowed strategies are execute, clarify, silently_resolve, "
        "face_preserving_rejection, multi_step. If there is no ambiguity, use an empty "
        "predicted_ambiguity_types array and null primary type. Input:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
