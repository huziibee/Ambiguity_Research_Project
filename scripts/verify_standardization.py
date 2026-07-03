import os
import csv
import json

BASE_RAW_DIR = r"C:\Users\huzii\Documents\University\Research Project\risk-aware-ambiguity-manager\data\raw"

DATASETS = {
    "AmbiK": "AmbiK/ambik_standardized.csv",
    "CLARA-Dataset": "CLARA-Dataset/clara_standardized.csv",
    "SafeAgentBench": "SafeAgentBench/safe_agent_bench_standardized.csv",
    "IndirectRequests": "IndirectRequests/indirect_requests_standardized.csv",
    "TEACh": "TEACh/teach_standardized.csv",
    "ClariQ": "ClariQ/clariq_standardized.csv",
    "Dynamic-RDMM": "Dynamic-RDMM/dynamic_rdmm_standardized.csv",
    "ReferIt3D": "ReferIt3D/referit3d_standardized.csv",
    "RefCOCO": "RefCOCO/refcoco_standardized.csv",
    "CollaborativeManipulationCorpus": "CollaborativeManipulationCorpus/cmc_standardized.csv"
}

EXPECTED_FIELDS = [
    "source_id",
    "command",
    "scene_context",
    "dialogue_history",
    "capability_context",
    "original_split",
    "metadata"
]

def main():
    all_valid = True
    print("=== Verification of Dataset Standardization ===")
    for name, relative_path in DATASETS.items():
        path = os.path.join(BASE_RAW_DIR, relative_path)
        if not os.path.exists(path):
            print(f"[ERROR] {name}: File not found at {path}")
            all_valid = False
            continue
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Check headers
                if headers != EXPECTED_FIELDS:
                    print(f"[ERROR] {name}: Invalid headers. Expected {EXPECTED_FIELDS}, got {headers}")
                    all_valid = False
                    continue
                    
                # Read rows to check formatting and count
                row_count = 0
                for i, row in enumerate(reader):
                    row_count += 1
                    # Verify fields are present
                    for field in EXPECTED_FIELDS:
                        if field not in row:
                            print(f"[ERROR] {name}: Missing field '{field}' at row {i}")
                            all_valid = False
                            break
                    if i < 1:
                        # Print sample command and scene context for verification
                        print(f"[INFO] {name} Sample:")
                        print(f"  - Command: {row['command']}")
                        print(f"  - Context: {row['scene_context']}")
                        
                print(f"[SUCCESS] {name}: {row_count} rows successfully verified.\n")
        except Exception as e:
            print(f"[ERROR] {name}: Failed to read/verify: {e}")
            all_valid = False
            
    if all_valid:
        print("=== ALL DATASETS VERIFIED SUCCESSFULLY ===")
    else:
        print("=== VERIFICATION FAILED ===")

if __name__ == "__main__":
    main()
