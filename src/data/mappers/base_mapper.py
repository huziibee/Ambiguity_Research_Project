import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.schema import Example, SourceDataset

class BaseMapper(ABC):
    """
    Abstract base class for all dataset mappers.
    Handles logging of decisions to data/interim/filtering_log.jsonl
    and writing candidate mapped records to data/interim/<dataset>_mapped.jsonl.
    """
    def __init__(self, source_dataset: SourceDataset):
        self.source_dataset = source_dataset
        self.project_root = Path(__file__).resolve().parents[3]
        self.interim_dir = self.project_root / "data" / "interim"
        self.interim_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.interim_dir / "filtering_log.jsonl"
        
    def log_decision(
        self,
        source_id: str,
        decision: str,
        reason: str,
        mapper_stage: str,
        human_approval_status: str = "pending",
        provenance: str = "Original command and metadata retained"
    ):
        log_entry = {
            "source_dataset": self.source_dataset.value,
            "source_id": source_id,
            "decision": decision,
            "reason": reason,
            "mapper_stage": mapper_stage,
            "human_approval_status": human_approval_status,
            "provenance": provenance
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def write_candidates(self, candidates: List[Dict[str, Any]], output_name: str):
        output_path = self.interim_dir / f"{output_name}_mapped.jsonl"
        print(f"Writing {len(candidates)} candidates to {output_path}...")
        with open(output_path, "w", encoding="utf-8") as f:
            for item in candidates:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print("Candidates written successfully.")

    @abstractmethod
    def map_dataset(self) -> List[Dict[str, Any]]:
        """
        Maps the raw dataset to a list of dicts that conform to the candidate schema.
        Also logs exclusions and inclusions.
        """
        pass
