import json
from pathlib import Path
from typing import Iterable, List

from src.schema import Example


def load_examples(path: Path) -> List[Example]:
    """
    Loads examples from a file. Automatically detects whether the file is a
    standard JSON array (starts with '[') or a JSON Lines (JSONL) file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Example file not found: {path}")
        
    with path.open("r", encoding="utf-8") as f:
        content = f.read().strip()
        
    if not content:
        return []
        
    if content.startswith("["):
        # Parse as standard JSON array
        try:
            data = json.loads(content)
            return [Example(**item) for item in data]
        except Exception as exc:
            raise ValueError(f"Invalid JSON array at {path}: {exc}") from exc
    else:
        # Parse as JSON Lines (JSONL)
        examples: List[Example] = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                examples.append(Example(**json.loads(line)))
            except Exception as exc:
                raise ValueError(f"Invalid example line at {path}:{line_number}: {exc}") from exc
        return examples


def dump_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
