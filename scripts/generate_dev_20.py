import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.schema import Example

INPUT_PATH = os.path.join(BASE_DIR, "data", "manual", "dev_20_raw.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "dev_20.jsonl")

def main():
    print(f"Creating output directory: {OUTPUT_DIR}...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(INPUT_PATH):
        print(f"[ERROR] Manual dev_20 raw data not found at {INPUT_PATH}")
        sys.exit(1)
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        examples_data = json.load(f)
        
    print(f"Validating and writing {len(examples_data)} examples to {OUTPUT_PATH}...")
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for ex_dict in examples_data:
            # Pydantic v2 validation
            try:
                ex = Example(**ex_dict)
            except Exception as e:
                print(f"[ERROR] Example {ex_dict['example_id']} failed validation: {e}")
                raise e
            
            # Write JSON-serialized string per line
            f.write(ex.model_dump_json() + "\n")
            
    print("MVE dev_20 dataset generated successfully!")

if __name__ == "__main__":
    main()
