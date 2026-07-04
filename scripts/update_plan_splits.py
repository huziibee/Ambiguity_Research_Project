import os
import re
from pathlib import Path

def update_text(text: str) -> str:
    # 1. Replace dev_100 references with dev_80
    text = re.sub(r'dev_100\.jsonl', 'dev_80.jsonl', text)
    text = re.sub(r'dev_100=100', 'dev_80=80', text)
    text = re.sub(r'dev_100', 'dev_80', text)
    
    # 2. Replace count statistics in split descriptions
    # original: dev_80: 100, train: 60, test: 150
    # new: dev_80: 80, train: 240, test: 80
    text = re.sub(r'dev_80\s*\|\s*100\b', 'dev_80 | 80', text)
    text = re.sub(r'train\s*\|\s*60\b', 'train | 240', text)
    text = re.sub(r'test\s*\|\s*150\b', 'test | 80', text)
    
    text = re.sub(r'dev_80\s*:\s*100', 'dev_80: 80', text)
    text = re.sub(r'train\s*:\s*60', 'train: 240', text)
    text = re.sub(r'test\s*:\s*150', 'test: 80', text)
    
    text = re.sub(r'"dev_80"\s*:\s*100', '"dev_80": 80', text)
    text = re.sub(r'"train"\s*:\s*60', '"train": 240', text)
    text = re.sub(r'"test"\s*:\s*150', '"test": 80', text)
    
    # Specific phrasing:
    text = re.sub(r'100 human-approved development examples', '80 human-approved development examples', text)
    text = re.sub(r'100 examples cover all major', '80 examples cover all major', text)
    text = re.sub(r'60 examples for optional', '240 examples for optional', text)
    text = re.sub(r'150 examples held out', '80 examples held out', text)
    text = re.sub(r'150 frozen examples for final', '80 frozen examples for final', text)
    text = re.sub(r'frozen `test` split of \*\*150 human-approved examples\*\*', 'frozen `test` split of **80 human-approved examples**', text)
    text = re.sub(r'frozen `test` split of 150 human-approved examples', 'frozen `test` split of 80 human-approved examples', text)
    text = re.sub(r'frozen test set with at least 150 examples', 'frozen test set with at least 80 examples', text)
    text = re.sub(r'frozen 150-example test set minimum', 'frozen 80-example test set minimum', text)
    text = re.sub(r'150-example test set', '80-example test set', text)
    
    # 3. Replace total counts: 310 -> 400
    text = re.sub(r'310 unique human-labelled examples', '400 unique human-labelled examples', text)
    text = re.sub(r'310 unique human-approved examples', '400 unique human-approved examples', text)
    text = re.sub(r'310 unique human-labeled examples', '400 unique human-labeled examples', text)
    text = re.sub(r'310 examples', '400 examples', text)
    text = re.sub(r'310 target', '400 target', text)
    text = re.sub(r'310 total', '400 total', text)
    text = re.sub(r'totaling 310', 'totaling 400', text)
    text = re.sub(r'exactly 310', 'exactly 400', text)
    
    # In table columns:
    text = re.sub(r'AmbiK\s*\|\s*60-80', 'AmbiK | 110', text)
    text = re.sub(r'SaGC\s*\|\s*50-70', 'SaGC | 100', text)
    text = re.sub(r'IndirectRequests\s*\|\s*30-50', 'IndirectRequests | 70', text)
    text = re.sub(r'SafeAgentBench\s*\|\s*20-35', 'SafeAgentBench | 45', text)
    text = re.sub(r'TEACh\s*\|\s*10-20', 'TEACh | 25', text)
    
    return text

def main():
    project_root = Path(__file__).resolve().parents[1]
    plan_dir = project_root / "docs" / "plan"
    
    if not plan_dir.exists():
        print(f"Directory {plan_dir} does not exist.")
        return
        
    for filename in os.listdir(plan_dir):
        if filename.endswith(".md"):
            path = plan_dir / filename
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            updated = update_text(content)
            
            if updated != content:
                print(f"Updating {filename}...")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(updated)
                    
    print("Updates complete. Combining plan...")
    # Re-run combine_plan.py to recreate docs/full_plan.md
    combine_script = project_root / "scripts" / "combine_plan.py"
    os.system(f"python \"{combine_script}\"")

if __name__ == "__main__":
    main()
