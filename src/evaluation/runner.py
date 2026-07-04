import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from src.baselines.base import System
from src.evaluation.metrics import Prediction, compute_metrics, table_row
from src.schema import Example, ManagerInput, ManagerOutput, RiskLevel, RoutingStrategy, CapabilityStatus

TABLE_FIELDS = [
    "system",
    "n",
    "routing_accuracy",
    "compound_routing_accuracy",
    "clarification_precision",
    "clarification_recall",
    "clarification_f1",
    "unsafe_silent_resolution_rate",
    "ambiguity_exact_match",
    "primary_type_accuracy",
    "risk_accuracy",
    "capability_accuracy",
    "intent_accuracy",
    "slot_accuracy",
    "ambiguity_micro_f1",
    "ambiguity_macro_f1",
    "safe_rejection_rate",
    "multistep_sequence_exact_match",
    "multistep_sequence_jaccard",
]


def build_manager_input(ex: Example, risk_mode: str = "predicted") -> ManagerInput:
    """
    Strips all gold labels (gold_intent, gold_slots, gold_strategy, etc.) from the
    Example record to prevent data leakage before prompt formatting or LLM execution.
    Only allows gold risk if risk_mode is explicitly set to 'gold'.
    """
    # Safeguard: strip risk if not explicitly in gold mode
    gold_risk = ex.risk_level if risk_mode == "gold" else RiskLevel.NONE
    return ManagerInput(
        command=ex.command,
        dialogue_history=ex.dialogue_history,
        scene_context=ex.scene_context,
        capability_context=ex.capability_context,
        risk_level=gold_risk,
        risk_mode=risk_mode,
    )


def run_system(system: System, examples: Iterable[Example]) -> List[Prediction]:
    predictions: List[Prediction] = []
    # If the system has a custom risk_mode set it, default to "predicted" to avoid leakage
    risk_mode = getattr(system, "risk_mode", "predicted")
    
    for example in examples:
        manager_input = build_manager_input(example, risk_mode=risk_mode)
        try:
            output = system.predict(manager_input)
            if output is None:
                raise ValueError("System predict returned None")
        except Exception as e:
            # Handle permanent API failures (timeouts, rate limits exceeded, safety blocks)
            # and return a specific failure ManagerOutput object to keep metrics aligned
            print(f"[SYSTEM FAILURE] {system.name} failed on example {example.example_id}: {e}")
            output = ManagerOutput(
                predicted_intent="unknown",
                predicted_slots={},
                predicted_ambiguity_types=[],
                predicted_primary_ambiguity_type=None,
                predicted_is_compound=False,
                predicted_capability_status=CapabilityStatus.UNKNOWN,
                predicted_risk_level=RiskLevel.UNKNOWN,
                predicted_strategy=RoutingStrategy.CLARIFY,
                predicted_strategy_sequence=None,
                predicted_clarification_question="An internal error occurred. Can you please repeat or clarify the request?",
                predicted_rejection_explanation=f"System failed to parse request due to API timeout or safety block: {e}"
            )
            
        predictions.append((example, ManagerOutput(**output.model_dump())))
    return predictions


def write_predictions(path: Path, predictions: List[Prediction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    rows = []
    for example, output in predictions:
        rows.append({
            "example_id": example.example_id,
            "gold_strategy": example.gold_strategy.value,
            "prediction": output.model_dump(mode="json"),
            "generated_at": timestamp
        })
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def write_metrics(path: Path, metrics: Dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    metrics_copy = dict(metrics)
    metrics_copy["generated_at"] = timestamp
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics_copy, f, indent=2, sort_keys=True)
        f.write("\n")


def write_table(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TABLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_evaluation(
    systems: Iterable[System],
    examples: List[Example],
    results_dir: Path,
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for system in systems:
        predictions = run_system(system, examples)
        metrics = compute_metrics(predictions)
        # Output prediction logs as formatted JSON arrays (.json) instead of JSONL
        write_predictions(results_dir / "predictions" / f"{system.name}.json", predictions)
        write_metrics(results_dir / "metrics" / f"{system.name}.json", metrics)
        rows.append(table_row(system.name, metrics))
    write_table(results_dir / "tables" / "table1_main_results.csv", rows)
    return rows
