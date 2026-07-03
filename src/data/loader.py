import json
from pathlib import Path
from typing import Iterable, List

from src.schema import Example


def load_examples(path: Path) -> List[Example]:
    examples: List[Example] = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                examples.append(Example(**json.loads(line)))
            except Exception as exc:
                raise ValueError(f"Invalid example at {path}:{line_number}: {exc}") from exc
    return examples


def dump_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
