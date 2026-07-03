import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines.always_clarify import AlwaysClarify
from src.baselines.always_resolve import AlwaysResolve
from src.baselines.degree_based import DegreeBased
from src.baselines.direct_llm import DirectLLM
from src.data.loader import load_examples
from src.evaluation.runner import run_evaluation
from src.manager.pipeline import ProposedManager


DEV_PATH = PROJECT_ROOT / "data" / "processed" / "dev_20.jsonl"
RESULTS_DIR = PROJECT_ROOT / "results"


def build_systems():
    return [
        AlwaysClarify(),
        AlwaysResolve(),
        DegreeBased(),
        DirectLLM(),
        ProposedManager(),
    ]


def ensure_dev_20() -> None:
    if DEV_PATH.exists():
        return
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_dev_20.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run evaluation on ambiguity manager systems.")
    parser.add_argument(
        "--data",
        type=str,
        default=str(DEV_PATH),
        help="Path to the JSONL dataset containing evaluation examples."
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    if data_path == DEV_PATH:
        ensure_dev_20()

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {data_path}")

    examples = load_examples(data_path)
    if data_path == DEV_PATH and len(examples) != 20:
        raise ValueError(f"Expected 20 dev examples in default split, found {len(examples)}")

    print(f"Loaded {len(examples)} examples from {data_path}")
    rows = run_evaluation(build_systems(), examples, RESULTS_DIR)
    print(f"Wrote {len(rows)} system rows to {RESULTS_DIR / 'tables' / 'table1_main_results.csv'}")


if __name__ == "__main__":
    main()
