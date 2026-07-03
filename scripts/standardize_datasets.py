import os
import csv
import json
import pyarrow.ipc as ipc
from datasets import load_from_disk

# Base raw data directory
BASE_RAW_DIR = r"C:\Users\huzii\Documents\University\Research Project\risk-aware-ambiguity-manager\data\raw"

# CSV fieldnames
FIELDNAMES = [
    "source_id",
    "command",
    "scene_context",
    "dialogue_history",
    "capability_context",
    "original_split",
    "metadata"
]

def write_standardized_csv(output_path, rows):
    print(f"Writing {len(rows)} rows to {output_path}...")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            # Ensure JSON serialization for lists and dicts
            r_clean = {}
            for field in FIELDNAMES:
                val = r.get(field, "")
                if isinstance(val, (list, dict)):
                    r_clean[field] = json.dumps(val)
                elif val is None:
                    r_clean[field] = ""
                else:
                    r_clean[field] = str(val)
            writer.writerow(r_clean)
    print("Done.")

def standardize_ambik():
    print("\n--- Standardizing AmbiK ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "AmbiK")
    output_path = os.path.join(dataset_dir, "ambik_standardized.csv")
    
    # We will combine test_400 and test_900 if they exist
    files_to_process = [
        ("ambik_test_400.csv", "test_400"),
        ("ambik_test_900.csv", "test_900"),
        ("ambik_calib_100.csv", "calib_100")
    ]
    
    rows = []
    for filename, split in files_to_process:
        path = os.path.join(dataset_dir, "ambik_dataset", filename)
        if not os.path.exists(path):
            print(f"File not found: {path}, skipping split {split}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata = {k: v for k, v in row.items() if k not in ["id", "ambiguous_task", "environment_full"]}
                rows.append({
                    "source_id": row.get("id", ""),
                    "command": row.get("ambiguous_task", ""),
                    "scene_context": row.get("environment_full", ""),
                    "dialogue_history": [],
                    "capability_context": "",
                    "original_split": split,
                    "metadata": metadata
                })
    if rows:
        write_standardized_csv(output_path, rows)
    else:
        print("No AmbiK data processed.")

def standardize_clara():
    print("\n--- Standardizing CLARA/SaGC ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "CLARA-Dataset")
    output_path = os.path.join(dataset_dir, "clara_standardized.csv")
    path = os.path.join(dataset_dir, "data", "agument.json")
    
    if not os.path.exists(path):
        print(f"CLARA data file not found: {path}")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    rows = []
    for idx_str, entry in data.items():
        scene = entry.get("scene", {})
        objects = scene.get("objects", [])
        floorplan = scene.get("floorplan", [])
        people = scene.get("people", [])
        scene_desc = f"Objects: {', '.join(objects)}. Floorplan: {', '.join(floorplan)}. People: {', '.join(people)}"
        
        metadata = {
            "label": entry.get("label"),
            "task": entry.get("task")
        }
        
        rows.append({
            "source_id": idx_str,
            "command": entry.get("goal", ""),
            "scene_context": scene_desc,
            "dialogue_history": [],
            "capability_context": entry.get("task", ""),
            "original_split": "train",
            "metadata": metadata
        })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_safeagentbench():
    print("\n--- Standardizing SafeAgentBench ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "SafeAgentBench")
    output_path = os.path.join(dataset_dir, "safe_agent_bench_standardized.csv")
    
    splits = ["unsafe_detailed", "safe_detailed", "abstract"]
    rows = []
    
    for split in splits:
        path = os.path.join(dataset_dir, split, "train", "data-00000-of-00001.arrow")
        if not os.path.exists(path):
            print(f"File not found: {path}, skipping split {split}")
            continue
            
        with open(path, 'rb') as f:
            reader = ipc.open_stream(f)
            table = reader.read_all()
            pylist = table.to_pylist()
            
        for i, row in enumerate(pylist):
            inst = row.get("instruction", "")
            # If abstract split, instruction is a list of phrasings
            if isinstance(inst, list):
                inst = inst[0] if inst else ""
                
            metadata = {k: v for k, v in row.items() if k not in ["instruction", "scene_name"]}
            
            rows.append({
                "source_id": f"{split}_{i}",
                "command": inst,
                "scene_context": row.get("scene_name", ""),
                "dialogue_history": [],
                "capability_context": "",
                "original_split": split,
                "metadata": metadata
            })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_indirect_requests():
    print("\n--- Standardizing IndirectRequests ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "IndirectRequests")
    output_path = os.path.join(dataset_dir, "indirect_requests_standardized.csv")
    
    if not os.path.exists(dataset_dir):
        print(f"IndirectRequests dir not found: {dataset_dir}")
        return
        
    try:
        ds = load_from_disk(dataset_dir)
    except Exception as e:
        print(f"Failed to load IndirectRequests using datasets: {e}")
        return
        
    rows = []
    for split in ds.keys():
        split_data = ds[split]
        for i, row in enumerate(split_data):
            metadata = {k: v for k, v in row.items() if k not in ["utterance", "situation", "service"]}
            rows.append({
                "source_id": f"{split}_{i}",
                "command": row.get("utterance", ""),
                "scene_context": row.get("situation", ""),
                "dialogue_history": [],
                "capability_context": row.get("service", ""),
                "original_split": split,
                "metadata": metadata
            })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_teach():
    print("\n--- Standardizing TEACh ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "TEACh")
    output_path = os.path.join(dataset_dir, "teach_standardized.csv")
    games_dir = os.path.join(dataset_dir, "games")
    
    if not os.path.exists(games_dir):
        print(f"TEACh games dir not found: {games_dir}")
        return
        
    rows = []
    splits = ["train", "valid_seen", "valid_unseen"]
    
    for split in splits:
        split_dir = os.path.join(games_dir, split)
        if not os.path.exists(split_dir):
            print(f"Split dir not found: {split_dir}, skipping.")
            continue
            
        filenames = [f for f in os.listdir(split_dir) if f.endswith(".json")]
        print(f"Processing {len(filenames)} files in split '{split}'...")
        
        for fname in filenames:
            path = os.path.join(split_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    game_data = json.load(f)
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
                
            task_type = game_data.get("task_type", "")
            
            # Navigate tasks and episodes
            tasks = game_data.get("tasks", [])
            for t in tasks:
                task_desc = t.get("desc", "")
                task_name = t.get("task_name", "")
                episodes = t.get("episodes", [])
                
                for ep in episodes:
                    ep_id = ep.get("episode_id", "")
                    world = ep.get("world", "")
                    interactions = ep.get("interactions", [])
                    
                    # Reconstruct dialogue history
                    dialogue_turns = []
                    for inter in interactions:
                        # Keyboard text action is 100
                        if inter.get("action_id") == 100 or inter.get("utterance"):
                            agent_name = "Commander" if inter.get("agent_id") == 0 else "Driver"
                            dialogue_turns.append({
                                "agent": agent_name,
                                "text": inter.get("utterance", "")
                            })
                            
                    # Command is task description (or first Commander turn)
                    cmd = task_desc if task_desc else (dialogue_turns[0]["text"] if dialogue_turns else "")
                    
                    metadata = {
                        "task_type": task_type,
                        "task_name": task_name,
                        "world": world
                    }
                    
                    rows.append({
                        "source_id": ep_id if ep_id else fname,
                        "command": cmd,
                        "scene_context": f"World: {world}",
                        "dialogue_history": dialogue_turns,
                        "capability_context": task_name,
                        "original_split": split,
                        "metadata": metadata
                    })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_clariq():
    print("\n--- Standardizing ClariQ ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "ClariQ")
    output_path = os.path.join(dataset_dir, "clariq_standardized.csv")
    
    files = [
        ("train.tsv", "train"),
        ("dev.tsv", "dev"),
        ("test_with_labels.tsv", "test")
    ]
    
    rows = []
    for filename, split in files:
        path = os.path.join(dataset_dir, "data", filename)
        if not os.path.exists(path):
            print(f"File not found: {path}, skipping split {split}")
            continue
            
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            
            # Map column name to index
            col_map = {name: idx for idx, name in enumerate(header)}
            
            for row in reader:
                if len(row) <= max(col_map.values()):
                    continue
                initial_request = row[col_map["initial_request"]]
                topic_desc = row[col_map.get("topic_desc", col_map.get("topic_id", 0))]
                
                # Combine extra fields to metadata
                metadata = {}
                for name, idx in col_map.items():
                    if name not in ["initial_request", "topic_desc"]:
                        metadata[name] = row[idx]
                        
                source_id = row[col_map.get("facet_id", col_map.get("topic_id", 0))]
                
                rows.append({
                    "source_id": source_id,
                    "command": initial_request,
                    "scene_context": topic_desc,
                    "dialogue_history": [],
                    "capability_context": "",
                    "original_split": split,
                    "metadata": metadata
                })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_dynamic_rdmm():
    print("\n--- Standardizing Dynamic-RDMM ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "Dynamic-RDMM")
    output_path = os.path.join(dataset_dir, "dynamic_rdmm_standardized.csv")
    path = os.path.join(dataset_dir, "hf_dataset", "train_dataset.json")
    
    if not os.path.exists(path):
        print(f"Dynamic-RDMM dataset file not found: {path}")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    train_list = data.get("train", [])
    rows = []
    for i, entry in enumerate(train_list):
        rows.append({
            "source_id": f"rdmm_{i}",
            "command": entry.get("input", ""),
            "scene_context": "",
            "dialogue_history": [],
            "capability_context": "",
            "original_split": "train",
            "metadata": {"gold_plan": entry.get("output", "")}
        })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_referit3d():
    print("\n--- Standardizing ReferIt3D ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "ReferIt3D")
    output_path = os.path.join(dataset_dir, "referit3d_standardized.csv")
    
    rows = []
    
    # Process Nr3D
    nr3d_path = os.path.join(dataset_dir, "nr3d.csv")
    if os.path.exists(nr3d_path):
        print("Processing Nr3D...")
        with open(nr3d_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                metadata = {k: v for k, v in row.items() if k not in ["stimulus_id", "utterance", "scan_id"]}
                rows.append({
                    "source_id": row.get("stimulus_id", f"nr3d_{i}"),
                    "command": row.get("utterance", ""),
                    "scene_context": f"ScanID: {row.get('scan_id', '')}",
                    "dialogue_history": [],
                    "capability_context": "",
                    "original_split": "nr3d_train" if row.get("split", "") == "train" else "nr3d_val",
                    "metadata": metadata
                })
    else:
        print("Nr3D csv file not found.")
        
    # Process Sr3D
    sr3d_dir = os.path.join(dataset_dir, "sr3d")
    if os.path.exists(sr3d_dir):
        print("Processing Sr3D...")
        sr3d_files = [
            ("sr3d.csv", "sr3d_all"),
            ("sr3d_train.csv", "sr3d_train"),
            ("sr3d_test.csv", "sr3d_test"),
            ("sr3d+.csv", "sr3d+")
        ]
        for filename, split in sr3d_files:
            path = os.path.join(sr3d_dir, filename)
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    metadata = {k: v for k, v in row.items() if k not in ["stimulus_id", "utterance", "scan_id"]}
                    rows.append({
                        "source_id": row.get("stimulus_id", f"sr3d_{split}_{i}"),
                        "command": row.get("utterance", ""),
                        "scene_context": f"ScanID: {row.get('scan_id', '')}",
                        "dialogue_history": [],
                        "capability_context": "",
                        "original_split": split,
                        "metadata": metadata
                    })
    else:
        print("Sr3D directory not found.")
        
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_refcoco():
    print("\n--- Standardizing RefCOCO ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "RefCOCO")
    output_path = os.path.join(dataset_dir, "refcoco_standardized.csv")
    
    files = [
        ("refcoco_train.json", "refcoco_train"),
        ("refcoco_val.json", "refcoco_val"),
        ("refcoco_testA.json", "refcoco_testA"),
        ("refcoco_testB.json", "refcoco_testB"),
        ("refcoco+_train.json", "refcoco+_train"),
        ("refcoco+_val.json", "refcoco+_val"),
        ("refcoco+_testA.json", "refcoco+_testA"),
        ("refcoco+_testB.json", "refcoco+_testB"),
        ("refcocog_train.json", "refcocog_train"),
        ("refcocog_val.json", "refcocog_val"),
        ("refcocog_test.json", "refcocog_test")
    ]
    
    rows = []
    for filename, split in files:
        path = os.path.join(dataset_dir, filename)
        if not os.path.exists(path):
            print(f"File not found: {path}, skipping split {split}")
            continue
            
        print(f"Processing {filename}...")
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except Exception as e:
                    print(f"Error parsing line {i} in {filename}: {e}")
                    continue
                    
                objects = entry.get("objects", [])
                label = objects[0].get("label", "") if objects else ""
                
                metadata = {
                    "image": entry.get("image", ""),
                    "objects_count": len(objects)
                }
                
                rows.append({
                    "source_id": entry.get("id", f"{split}_{i}"),
                    "command": label,
                    "scene_context": entry.get("image", ""),
                    "dialogue_history": [],
                    "capability_context": "",
                    "original_split": split,
                    "metadata": metadata
                })
    if rows:
        write_standardized_csv(output_path, rows)

def standardize_cmc():
    print("\n--- Standardizing Collaborative Manipulation Corpus ---")
    dataset_dir = os.path.join(BASE_RAW_DIR, "CollaborativeManipulationCorpus")
    output_path = os.path.join(dataset_dir, "cmc_standardized.csv")
    path = os.path.join(dataset_dir, "data", "NLICorpusData.csv")
    
    if not os.path.exists(path):
        print(f"CMC file not found: {path}")
        return
        
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata = {k: v for k, v in row.items() if k not in ["Index", "Instruction", "Scenario", "AgentType"]}
            rows.append({
                "source_id": row.get("Index", ""),
                "command": row.get("Instruction", ""),
                "scene_context": row.get("Scenario", ""),
                "dialogue_history": [],
                "capability_context": row.get("AgentType", ""),
                "original_split": "train",
                "metadata": metadata
            })
    if rows:
        write_standardized_csv(output_path, rows)

def main():
    standardize_ambik()
    standardize_clara()
    standardize_safeagentbench()
    standardize_indirect_requests()
    standardize_teach()
    standardize_clariq()
    standardize_dynamic_rdmm()
    standardize_referit3d()
    standardize_refcoco()
    standardize_cmc()

if __name__ == "__main__":
    main()
