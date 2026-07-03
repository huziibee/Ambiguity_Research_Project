import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pick and prepare a local Ollama model.")
    parser.add_argument("--pull", action="store_true", help="Run `ollama pull` for the selected model.")
    args = parser.parse_args()

    model, reason = choose_model()
    print(f"Selected model: {model}")
    print(reason)

    if not command_ok(["ollama", "--version"]):
        print("Ollama is not installed or not on PATH.")
        print("Install Ollama, then run: ollama pull " + model)
        sys.exit(1)

    if args.pull:
        subprocess.run(["ollama", "pull", model], cwd=PROJECT_ROOT, check=True)

    print(
        "Use with: $env:DIRECT_LLM_BACKEND='ollama'; "
        "$env:LOCAL_LLM_MODEL='" + model + "'; python scripts/run_evaluation.py"
    )


def choose_model() -> tuple[str, str]:
    vram_mb = detect_nvidia_vram_mb()
    if vram_mb >= 60000:
        return "gpt-oss:120b", "Cookbook fit: at least 60 GB VRAM/unified memory."
    if vram_mb >= 16000:
        return "gpt-oss:20b", "Cookbook fit: at least 16 GB VRAM/unified memory."
    if vram_mb >= 6000:
        return (
            "qwen2.5:7b",
            f"Detected {vram_mb // 1024} GB VRAM; using a 7B model instead of gpt-oss:20b.",
        )
    return "qwen2.5:3b", "Low/unknown VRAM; using a smaller model."


def detect_nvidia_vram_mb() -> int:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return 0
    match = re.search(r"\d+", result.stdout)
    return int(match.group(0)) if match else 0


def command_ok(command: list[str]) -> bool:
    try:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


if __name__ == "__main__":
    main()
