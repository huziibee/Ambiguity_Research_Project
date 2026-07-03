import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from src.baselines.base import System
from src.evaluation.metrics import Prediction, compute_metrics, table_row
from src.schema import Example, ManagerInput, ManagerOutput


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


def example_to_input(example: Example) -> ManagerInput:
    return ManagerInput(
        command=example.command,
        dialogue_history=example.dialogue_history,
        scene_context=example.scene_context,
        capability_context=example.capability_context,
        risk_level=example.risk_level,
        risk_mode="gold",
    )


def run_system(system: System, examples: Iterable[Example]) -> List[Prediction]:
    predictions: List[Prediction] = []
    for example in examples:
        output = system.predict(example_to_input(example))
        predictions.append((example, ManagerOutput(**output.model_dump())))
    return predictions


def write_predictions(path: Path, predictions: List[Prediction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for example, output in predictions:
            row = {
                "example_id": example.example_id,
                "gold_strategy": example.gold_strategy.value,
                "prediction": output.model_dump(mode="json"),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_metrics(path: Path, metrics: Dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
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
        write_predictions(results_dir / "predictions" / f"{system.name}.jsonl", predictions)
        write_metrics(results_dir / "metrics" / f"{system.name}.json", metrics)
        rows.append(table_row(system.name, metrics))
    write_table(results_dir / "tables" / "table1_main_results.csv", rows)
    return rows
