import os
import sys
import json
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_json(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    annotation_dir = PROJECT_ROOT / "data" / "annotation"
    annotation_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all three split files
    dev_split = load_json(processed_dir / "dev_80.json")
    train_split = load_json(processed_dir / "train.json")
    test_split = load_json(processed_dir / "test.json")
    
    # Combine into a single list of 400 records
    all_400 = dev_split + train_split + test_split
    
    # Sort them by split and dataset for cleaner reading
    all_400.sort(key=lambda x: (x.get("split", ""), x.get("source_dataset", ""), x.get("example_id", "")))
    
    output_path = annotation_dir / "user_review_400.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_400, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully combined and wrote all {len(all_400)} examples to {output_path} for your review!")

if __name__ == "__main__":
    main()
