import os
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Set of extensions we want to capture
TEXT_EXTENSIONS = {'.py', '.md', '.txt', '.json', '.yml', '.yaml', '.toml', '.ini', '.gitignore'}

# Directories we absolutely want to exclude
EXCLUDE_DIRS = {
    '.git',
    '__pycache__',
    '.pytest_cache',
    '.agents',
    'cache',
    'results',  # Exclude evaluation results
    'data/raw',  # Exclude heavy raw datasets
    'data/interim',  # Exclude candidate logs
}

def should_exclude(path: Path) -> bool:
    # Check if any parent or the path itself is in EXCLUDE_DIRS
    relative = path.relative_to(PROJECT_ROOT)
    for part in relative.parts:
        if part in EXCLUDE_DIRS:
            return True
        # Check combined paths like data/raw
        for ex in EXCLUDE_DIRS:
            if str(relative).startswith(ex + os.sep) or str(relative) == ex:
                return True
    return False

def main():
    output_file = PROJECT_ROOT / "codebase_combined.txt"
    print(f"Combining codebase files into {output_file}...")

    # We collect files and sort them to have a consistent order
    collected_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Modify dirs in-place to avoid traversing excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in files:
            file_path = Path(root) / file
            if should_exclude(file_path):
                continue
            
            # Skip the output file itself
            if file_path == output_file:
                continue
                
            if file_path.suffix.lower() in TEXT_EXTENSIONS:
                collected_files.append(file_path)

    collected_files.sort(key=lambda p: str(p.relative_to(PROJECT_ROOT)))

    with open(output_file, "w", encoding="utf-8") as out:
        for file_path in collected_files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel_path.as_posix()}\n")
            out.write("=" * 80 + "\n")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"[ERROR READING FILE]: {e}\n")
            out.write("\n\n")

    print(f"Codebase combined successfully! Total files combined: {len(collected_files)}")

if __name__ == "__main__":
    main()
