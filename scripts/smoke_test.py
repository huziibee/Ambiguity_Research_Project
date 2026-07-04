import csv
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_evaluation import build_systems, main as run_main
from src.data.loader import load_examples
from src.evaluation.runner import build_manager_input, run_system
from src.schema import ManagerOutput, RoutingStrategy


DEV_PATH = PROJECT_ROOT / "data" / "processed" / "dev_20.json"
TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table1_main_results.csv"


def main() -> None:
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_dev_20.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )

    examples = load_examples(DEV_PATH)
    assert len(examples) == 20, len(examples)

    systems = build_systems()
    for system in systems:
        one = system.predict(build_manager_input(examples[0], risk_mode="gold"))
        ManagerOutput(**one.model_dump())
        full = run_system(system, examples)
        assert len(full) == 20

    proposed = systems[-1].predict(build_manager_input(next(ex for ex in examples if ex.is_compound), risk_mode="gold"))
    assert proposed.predicted_strategy == RoutingStrategy.MULTI_STEP
    assert proposed.predicted_strategy_sequence

    run_main()
    with TABLE_PATH.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    for row in rows:
        for key, value in row.items():
            assert value != "", (key, row)

    print("Smoke test passed")


if __name__ == "__main__":
    main()
