import os
import shutil

BASE_RAW_DIR = r"C:\Users\huzii\Documents\University\Research Project\risk-aware-ambiguity-manager\data\raw"

DATASETS = [
    ("AmbiK", "ambik_standardized.csv"),
    ("CLARA-Dataset", "clara_standardized.csv"),
    ("SafeAgentBench", "safe_agent_bench_standardized.csv"),
    ("IndirectRequests", "indirect_requests_standardized.csv"),
    ("TEACh", "teach_standardized.csv"),
    ("ClariQ", "clariq_standardized.csv"),
    ("Dynamic-RDMM", "dynamic_rdmm_standardized.csv"),
    ("ReferIt3D", "referit3d_standardized.csv"),
    ("RefCOCO", "refcoco_standardized.csv"),
    ("CollaborativeManipulationCorpus", "cmc_standardized.csv")
]

def main():
    print("=== Commencing Raw Dataset Cleanup ===")
    for folder, csv_filename in DATASETS:
        dir_path = os.path.join(BASE_RAW_DIR, folder)
        if not os.path.exists(dir_path):
            print(f"Folder not found: {dir_path}")
            continue
            
        print(f"Cleaning folder: {folder}...")
        # Get list of files/folders in the directory
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            # Skip if it is the standardized CSV or the README
            if item.lower() == csv_filename.lower() or item.lower() == "readme.md":
                continue
            # Keep LICENSE files if present
            if "license" in item.lower():
                print(f"  Keeping: {item}")
                continue
                
            # Otherwise, delete it
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"  Deleted folder: {item}")
                else:
                    os.remove(item_path)
                    print(f"  Deleted file: {item}")
            except Exception as e:
                print(f"  [ERROR] Failed to delete {item}: {e}")
                
        print(f"Finished cleaning {folder}.\n")
        
    print("=== Raw Dataset Cleanup Complete ===")

if __name__ == "__main__":
    main()
