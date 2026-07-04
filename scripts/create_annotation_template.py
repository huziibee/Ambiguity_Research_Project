import os
import sys
import json
import random
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def load_json(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    processed_dir = PROJECT_ROOT / "data" / "processed"
    annotation_dir = PROJECT_ROOT / "data" / "annotation"
    annotation_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load splits
    dev_split = load_json(processed_dir / "dev_80.json")
    train_split = load_json(processed_dir / "train.json")
    test_split = load_json(processed_dir / "test.json")
    
    all_examples = dev_split + train_split + test_split
    
    # 2. Define our 4 target buckets for a balanced 60-example IAA test:
    # Bucket 1: Compound Ambiguities (20 examples)
    compound_cases = [e for e in all_examples if e.get("is_compound") is True]
    
    # Bucket 2: Unsafe/Safety Stress cases (20 examples)
    unsafe_cases = [e for e in all_examples if e.get("risk_level") in ["medium", "high", "critical"]]
    
    # Bucket 3: Incapable/Complex cases (10 examples)
    incapable_cases = [e for e in all_examples if e.get("capability_status") == "incapable"]
    
    # Bucket 4: Clear/Unambiguous Execute cases (10 examples)
    clear_cases = [
        e for e in all_examples 
        if e.get("ambiguity_present") is False 
        and e.get("risk_level") in ["none", "low"]
        and e.get("capability_status") == "capable"
        and e.get("gold_strategy") == "execute"
    ]
    
    print(f"Candidate pools:")
    print(f"  - Compound: {len(compound_cases)}")
    print(f"  - Unsafe:   {len(unsafe_cases)}")
    print(f"  - Incapable:{len(incapable_cases)}")
    print(f"  - Clear:    {len(clear_cases)}")
    
    selected_set = set()
    random.seed(42)
    
    # Bucket 1: 20 Compound Ambiguities (drawn first from manual compound templates)
    manual_compounds = [e for e in compound_cases if e.get("source_dataset") == "manual"]
    for e in random.sample(manual_compounds, min(len(manual_compounds), 20)):
        selected_set.add(e["example_id"])
        
    # Bucket 2: 20 Unsafe/Safety Stress cases
    for e in random.sample(unsafe_cases, min(len(unsafe_cases), 20)):
        selected_set.add(e["example_id"])
        
    # Bucket 3: 10 Incapable/Complex cases
    for e in random.sample(incapable_cases, min(len(incapable_cases), 10)):
        selected_set.add(e["example_id"])
        
    # Bucket 4: 10 Clear/Unambiguous Execute cases
    for e in random.sample(clear_cases, min(len(clear_cases), 10)):
        selected_set.add(e["example_id"])
        
    # Fill remaining to exactly 60 from all examples if needed
    remaining_pool = [e for e in all_examples if e["example_id"] not in selected_set]
    while len(selected_set) < 60 and remaining_pool:
        e = random.choice(remaining_pool)
        selected_set.add(e["example_id"])
        remaining_pool.remove(e)
        
    # Convert back to list of dicts
    selected_examples = [e for e in all_examples if e["example_id"] in selected_set]
    # Ensure exactly 60
    selected_examples = selected_examples[:60]
    
    print(f"Selected exactly {len(selected_examples)} examples for double annotation.")
    
    # 3. Create gold reference file for these 60 examples
    with open(annotation_dir / "annotator_a.json", "w", encoding="utf-8") as f:
        json.dump(selected_examples, f, indent=2, ensure_ascii=False)
    print("Wrote annotator_a.json (gold reference labels)")
    
    # 4. Create blank template file (stripping all gold annotations) for Annotator B (the second annotator)
    blank_template = []
    for ex in selected_examples:
        blank_ex = {
            "example_id": ex["example_id"],
            "source_dataset": ex["source_dataset"],
            "source_id": ex["source_id"],
            "split": ex["split"],
            "command": ex["command"],
            "dialogue_history": ex["dialogue_history"],
            "scene_context": ex["scene_context"],
            "capability_context": ex["capability_context"],
            
            # Blank targets to be filled in by Annotator B:
            "gold_intent": "",
            "gold_slots": {},
            "ambiguity_present": False,
            "ambiguity_types": [],
            "primary_ambiguity_type": None,
            "is_compound": False,
            "compound_ambiguity_count": 0,
            "risk_level": "none",
            "risk_target": None,
            "capability_status": "capable",
            "gold_strategy": "",
            "gold_strategy_sequence": [],
            "gold_clarification_question": "",
            "gold_reinterpretation": "",
            "gold_rejection_explanation": "",
            "gold_success_condition": "",
            "annotation_notes": "",
            "annotator": "Annotator_B",
            "annotation_date": ""
        }
        blank_template.append(blank_ex)
        
    with open(annotation_dir / "blank_template_60.json", "w", encoding="utf-8") as f:
        json.dump(blank_template, f, indent=2, ensure_ascii=False)
    print("Wrote blank_template_60.json (empty target schemas for Annotator B)")

if __name__ == "__main__":
    main()
