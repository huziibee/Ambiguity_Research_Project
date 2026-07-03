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
        manual_examples = json.load(f)
    print(f"Loaded {len(manual_examples)} manual compound examples.")
    
    # Split manual examples:
    # First 20 are the MVE dev_20 examples
    manual_mve = manual_examples[:20]
    # Next 30 are other manual compound examples
    manual_other = manual_examples[20:]
    
    # 2. Load candidates from other datasets
    ambik_candidates = load_jsonl(interim_dir / "ambik_mapped.jsonl")
    sagc_candidates = load_jsonl(interim_dir / "sagc_mapped.jsonl")
    ir_candidates = load_jsonl(interim_dir / "indirect_requests_mapped.jsonl")
    sab_candidates = load_jsonl(interim_dir / "safe_agent_bench_mapped.jsonl")
    teach_candidates = load_jsonl(interim_dir / "teach_mapped.jsonl")
    
    print(f"Loaded candidates: AmbiK={len(ambik_candidates)}, SaGC={len(sagc_candidates)}, IndirectRequests={len(ir_candidates)}, SafeAgentBench={len(sab_candidates)}, TEACh={len(teach_candidates)}")
    
    # Select target counts per dataset:
    # AmbiK: 80
    # SaGC: 70
    # IndirectRequests: 50
    # SafeAgentBench: 35
    # TEACh: 25
    random.seed(42)
    
    selected_ambik = random.sample(ambik_candidates, 80)
    selected_sagc = random.sample(sagc_candidates, 70)
    selected_ir = random.sample(ir_candidates, 50)
    selected_sab = random.sample(sab_candidates, 35)
    selected_teach = random.sample(teach_candidates, 25)
    
    # 3. Combine non-manual candidates and shuffle deterministically
    non_manual_pool = selected_ambik + selected_sagc + selected_ir + selected_sab + selected_teach
    random.shuffle(non_manual_pool)
    print(f"Total non-manual pool: {len(non_manual_pool)}")
    
    # 4. Construct splits
    # Target sizes:
    # dev_100: 100 total (20 manual MVE + 30 manual other + 50 non-manual)
    # train: 60 total (all non-manual)
    # test: 150 total (all non-manual)
    
    dev_100_non_manual = non_manual_pool[:50]
    train_pool = non_manual_pool[50:110]
    test_pool = non_manual_pool[110:260]
    
    dev_100 = manual_mve + manual_other + dev_100_non_manual
    dev_20 = manual_mve
    train = train_pool
    test = test_pool
    
    print(f"Split sizes: dev_20={len(dev_20)}, dev_100={len(dev_100)}, train={len(train)}, test={len(test)}")
    
    # Set split attribute on each record and validate through Example schema
    def prepare_and_write(examples_list, split_name, output_path):
        validated_lines = []
        for i, ex_dict in enumerate(examples_list):
            ex_dict["split"] = split_name
            # Re-generate unique ID if needed, or keep original
            if ex_dict["source_dataset"] != "manual":
                ex_dict["example_id"] = f"{split_name}_{ex_dict['source_dataset']}_{ex_dict['source_id']}"
            else:
                ex_dict["example_id"] = f"{split_name}_manual_{ex_dict['example_id'].split('_')[-1]}"
                
            try:
                ex = Example(**ex_dict)
                validated_lines.append(ex.model_dump_json())
            except Exception as e:
                print(f"[ERROR] Validation failed for {ex_dict.get('example_id')}: {e}")
                raise e
                
        with open(output_path, "w", encoding="utf-8") as f:
            for line in validated_lines:
                f.write(line + "\n")
        print(f"Wrote {len(validated_lines)} validated examples to {output_path}")
        
    prepare_and_write(dev_20, "dev_20", processed_dir / "dev_20.jsonl")
    prepare_and_write(dev_100, "dev_100", processed_dir / "dev_100.jsonl")
    prepare_and_write(train, "train", processed_dir / "train.jsonl")
    prepare_and_write(test, "test", processed_dir / "test.jsonl")
    
    # 5. Write manifest.json
    manifest = {
        "frozen_date": "2026-07-03",
        "random_seed": 42,
        "split_sizes": {
            "dev_20": len(dev_20),
            "dev_100": len(dev_100),
            "train": len(train),
            "test": len(test)
        },
        "source_dataset_counts": {
            "dev_100": {
                "manual": len(manual_examples),
                "ambik": sum(1 for x in dev_100_non_manual if x["source_dataset"] == "ambik"),
                "sagc": sum(1 for x in dev_100_non_manual if x["source_dataset"] == "sagc"),
                "indirect_requests": sum(1 for x in dev_100_non_manual if x["source_dataset"] == "indirect_requests"),
                "safe_agent_bench": sum(1 for x in dev_100_non_manual if x["source_dataset"] == "safe_agent_bench"),
                "teach": sum(1 for x in dev_100_non_manual if x["source_dataset"] == "teach")
            },
            "train": {
                "ambik": sum(1 for x in train if x["source_dataset"] == "ambik"),
                "sagc": sum(1 for x in train if x["source_dataset"] == "sagc"),
                "indirect_requests": sum(1 for x in train if x["source_dataset"] == "indirect_requests"),
                "safe_agent_bench": sum(1 for x in train if x["source_dataset"] == "safe_agent_bench"),
                "teach": sum(1 for x in train if x["source_dataset"] == "teach")
            },
            "test": {
                "ambik": sum(1 for x in test if x["source_dataset"] == "ambik"),
                "sagc": sum(1 for x in test if x["source_dataset"] == "sagc"),
                "indirect_requests": sum(1 for x in test if x["source_dataset"] == "indirect_requests"),
                "safe_agent_bench": sum(1 for x in test if x["source_dataset"] == "safe_agent_bench"),
                "teach": sum(1 for x in test if x["source_dataset"] == "teach")
            }
        }
    }
    
    with open(processed_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Wrote manifest.json")
    
    # 6. Generate data selection log summary (Table 7)
    # Write summary statistics to console
    print("\n--- Data Selection Summary ---")
    for dataset in ["manual", "ambik", "sagc", "indirect_requests", "safe_agent_bench", "teach"]:
        included = manifest["source_dataset_counts"]["dev_100"].get(dataset, 0) + \
                   manifest["source_dataset_counts"]["train"].get(dataset, 0) + \
                   manifest["source_dataset_counts"]["test"].get(dataset, 0)
        print(f"Dataset: {dataset:<20} | Included: {included}")

if __name__ == "__main__":
    main()
