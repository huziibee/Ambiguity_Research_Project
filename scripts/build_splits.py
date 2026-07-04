import os
import sys
import json
import random
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.schema import Example, SourceDataset, RoutingStrategy

def load_jsonl(path: Path) -> list:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def main():
    interim_dir = PROJECT_ROOT / "data" / "interim"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load manual compound examples
    manual_path = PROJECT_ROOT / "data" / "manual" / "compound_50_raw.json"
    if not manual_path.exists():
        print(f"[ERROR] Manual compound examples not found at {manual_path}")
        sys.exit(1)
        
    with open(manual_path, "r", encoding="utf-8") as f:
        manual_pool = json.load(f)
    print(f"Loaded {len(manual_pool)} manual compound examples.")
    
    # 2. Load candidates from other datasets
    ambik_pool = load_jsonl(interim_dir / "ambik_mapped.jsonl")
    sagc_pool = load_jsonl(interim_dir / "sagc_mapped.jsonl")
    ir_pool = load_jsonl(interim_dir / "indirect_requests_mapped.jsonl")
    sab_pool = load_jsonl(interim_dir / "safe_agent_bench_mapped.jsonl")
    teach_pool = load_jsonl(interim_dir / "teach_mapped.jsonl")
    
    print(f"Loaded candidate pools: AmbiK={len(ambik_pool)}, SaGC={len(sagc_pool)}, IndirectRequests={len(ir_pool)}, SafeAgentBench={len(sab_pool)}, TEACh={len(teach_pool)}")
    
    # Define target counts for each dataset (totaling 400)
    # Each target count must be divisible by 5 to ensure clean 60/20/20 splits:
    # Train = 60%, Dev = 20%, Test = 20%
    dataset_configs = {
        "manual": {"pool": manual_pool, "total": 50, "train": 30, "dev": 10, "test": 10},
        "ambik": {"pool": ambik_pool, "total": 110, "train": 66, "dev": 22, "test": 22},
        "sagc": {"pool": sagc_pool, "total": 100, "train": 60, "dev": 20, "test": 20},
        "indirect_requests": {"pool": ir_pool, "total": 70, "train": 42, "dev": 14, "test": 14},
        "safe_agent_bench": {"pool": sab_pool, "total": 45, "train": 27, "dev": 9, "test": 9},
        "teach": {"pool": teach_pool, "total": 25, "train": 15, "dev": 5, "test": 5}
    }
    
    # Stratified split lists
    train_split = []
    dev_split = []
    test_split = []
    
    # Tracking subset selections for dev_20
    dev_20_manual = []
    dev_20_non_manual = []
    
    # Fixed random seed for reproducibility
    random.seed(42)
    
    for name, cfg in dataset_configs.items():
        pool = cfg["pool"]
        total = cfg["total"]
        train_count = cfg["train"]
        dev_count = cfg["dev"]
        test_count = cfg["test"]
        
        if len(pool) < total:
            print(f"[ERROR] Pool for {name} has only {len(pool)} items, but target total is {total}")
            sys.exit(1)
            
        # Sample total required from pool (keep manual ordering intact to keep first 20 as dev_20 candidates if needed)
        if name == "manual":
            # For manual, keep the pool in original sequence order (don't random sample)
            selected = pool[:total]
        else:
            selected = random.sample(pool, total)
            
        # Split selected into Train (60%), Dev (20%), Test (20%)
        # For manual:
        # First 30 go to Train, next 10 go to Dev, last 10 go to Test.
        # This means the 10 manual Dev items will be manual_031 to manual_040 (or similar depending on pool order).
        # We will put all 10 of these manual Dev items into dev_20.
        train_items = selected[:train_count]
        dev_items = selected[train_count:train_count+dev_count]
        test_items = selected[train_count+dev_count:]
        
        train_split.extend(train_items)
        dev_split.extend(dev_items)
        test_split.extend(test_items)
        
        # Select candidates for dev_20 (which is a subset of dev split)
        if name == "manual":
            # All 10 manual Dev items go into dev_20
            dev_20_manual.extend(dev_items)
        else:
            # 2 random items from the Dev split of each non-manual dataset go to dev_20
            dev_20_non_manual.extend(random.sample(dev_items, 2))
            
    # Combine dev_20
    dev_20 = dev_20_manual + dev_20_non_manual
    
    print(f"Constructed splits:")
    print(f"  - Train: {len(train_split)} examples")
    print(f"  - Dev (dev_80): {len(dev_split)} examples")
    print(f"  - Test: {len(test_split)} examples")
    print(f"  - dev_20 subset: {len(dev_20)} examples")
    
    # Set split attribute on each record and validate through Example schema
    def prepare_and_write(examples_list, split_name, output_path):
        validated_examples = []
        for i, ex_dict in enumerate(examples_list):
            ex_dict["split"] = split_name
            # Re-generate unique ID if needed, or keep original
            if ex_dict["source_dataset"] != "manual":
                ex_dict["example_id"] = f"{split_name}_{ex_dict['source_dataset']}_{ex_dict['source_id']}"
            else:
                ex_dict["example_id"] = f"{split_name}_manual_{ex_dict['example_id'].split('_')[-1]}"
                
            try:
                ex = Example(**ex_dict)
                validated_examples.append(ex.model_dump())
            except Exception as e:
                print(f"[ERROR] Validation failed for {ex_dict.get('example_id')}: {e}")
                raise e
                
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validated_examples, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(validated_examples)} validated examples to {output_path}")
        
    prepare_and_write(dev_20, "dev_20", processed_dir / "dev_20.json")
    prepare_and_write(dev_split, "dev_80", processed_dir / "dev_80.json")
    prepare_and_write(train_split, "train", processed_dir / "train.json")
    prepare_and_write(test_split, "test", processed_dir / "test.json")
    
    # 5. Write manifest.json
    manifest = {
        "frozen_date": "2026-07-04",
        "random_seed": 42,
        "split_sizes": {
            "dev_20": len(dev_20),
            "dev_80": len(dev_split),
            "train": len(train_split),
            "test": len(test_split)
        },
        "source_dataset_counts": {
            "dev_80": {name: cfg["dev"] for name, cfg in dataset_configs.items()},
            "train": {name: cfg["train"] for name, cfg in dataset_configs.items()},
            "test": {name: cfg["test"] for name, cfg in dataset_configs.items()}
        }
    }
    
    with open(processed_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Wrote manifest.json")
    
    # 6. Generate data selection log summary (Table 7)
    print("\n--- Stratified Data Selection Summary ---")
    for dataset in dataset_configs.keys():
        included = dataset_configs[dataset]["total"]
        print(f"Dataset: {dataset:<20} | Included: {included:<3} (Train={dataset_configs[dataset]['train']}, Dev={dataset_configs[dataset]['dev']}, Test={dataset_configs[dataset]['test']})")

if __name__ == "__main__":
    main()
