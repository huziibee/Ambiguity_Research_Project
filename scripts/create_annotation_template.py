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
    
    # 2. Select 50 representative examples heavily weighting compound, unsafe (high/critical risk), and incapable cases
    compound_cases = [e for e in all_examples if e.get("is_compound") is True]
    unsafe_cases = [e for e in all_examples if e.get("risk_level") in ["medium", "high", "critical"]]
    incapable_cases = [e for e in all_examples if e.get("capability_status") == "incapable"]
    
    print(f"Candidate pools: Compound={len(compound_cases)}, Unsafe={len(unsafe_cases)}, Incapable={len(incapable_cases)}")
    
    selected_set = set()
    
    # Deterministic sampling using random seed
    random.seed(42)
    
    # Grab manual compound cases first (up to 20)
    manual_compounds = [e for e in compound_cases if e.get("source_dataset") == "manual"]
    for e in random.sample(manual_compounds, min(len(manual_compounds), 20)):
        selected_set.add(e["example_id"])
        
    # Grab unsafe cases (up to 15)
    for e in random.sample(unsafe_cases, min(len(unsafe_cases), 15)):
        selected_set.add(e["example_id"])
        
    # Grab incapable cases (up to 15)
    for e in random.sample(incapable_cases, min(len(incapable_cases), 15)):
        selected_set.add(e["example_id"])
        
    # Fill remaining to exactly 50 from all examples if needed
    remaining_pool = [e for e in all_examples if e["example_id"] not in selected_set]
    while len(selected_set) < 50 and remaining_pool:
        e = random.choice(remaining_pool)
        selected_set.add(e["example_id"])
        remaining_pool.remove(e)
        
    # Convert back to list of dicts
    selected_examples = [e for e in all_examples if e["example_id"] in selected_set]
    # Ensure exactly 50
    selected_examples = selected_examples[:50]
    
    print(f"Selected exactly {len(selected_examples)} examples for double annotation.")
    
    # 3. Create gold reference file for these 50 examples
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
        
    with open(annotation_dir / "blank_template_50.json", "w", encoding="utf-8") as f:
        json.dump(blank_template, f, indent=2, ensure_ascii=False)
    print("Wrote blank_template_50.json (empty target schemas for Annotator B)")

if __name__ == "__main__":
    main()
