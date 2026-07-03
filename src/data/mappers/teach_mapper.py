import os
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.schema import SourceDataset, AmbiguityType, RiskLevel, RoutingStrategy, CapabilityStatus
from src.data.mappers.base_mapper import BaseMapper

class TEAChMapper(BaseMapper):
    def __init__(self):
        super().__init__(SourceDataset.TEACH)
        
    def map_dataset(self) -> List[Dict[str, Any]]:
        dataset_dir = self.project_root / "data" / "raw" / "TEACh"
        csv_path = dataset_dir / "teach_standardized.csv"
        
        candidates = []
        if not csv_path.exists():
            print(f"TEACh standardized file not found: {csv_path}")
            return candidates
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                source_id = row.get("source_id", f"teach_{idx}")
                command = row.get("command", "").strip()
                scene_context = row.get("scene_context", "").strip()
                capability_context_raw = row.get("capability_context", "").strip()
                original_split = row.get("original_split", "").strip()
                
                # Parse dialogue_history
                dialogue_history_str = row.get("dialogue_history", "[]")
                try:
                    dialogue_history = json.loads(dialogue_history_str)
                except Exception as e:
                    dialogue_history = []
                
                # Parse metadata JSON
                metadata_str = row.get("metadata", "{}")
                try:
                    metadata = json.loads(metadata_str)
                except Exception as e:
                    metadata = {}
                    
                task_name = metadata.get("task_name", "")
                
                # Exclusion checks
                if not command:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing command text",
                        mapper_stage="teach_mapper"
                    )
                    continue
                    
                # Exclude if dialogue history is completely empty (no context)
                if not dialogue_history:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing dialogue history context",
                        mapper_stage="teach_mapper"
                    )
                    continue
                
                # TEACh commands are high-level tasks like "Prepare breakfast", "Make tea"
                # which are highly underspecified.
                amb_types = [AmbiguityType.UNDERSPECIFIED]
                primary_amb = AmbiguityType.UNDERSPECIFIED
                strategy = RoutingStrategy.MULTI_STEP
                risk_lvl = RiskLevel.MEDIUM  # Involves kitchen tools, boiling water, toaster, etc.
                
                candidate = {
                    "example_id": f"teach_{source_id}",
                    "source_dataset": self.source_dataset.value,
                    "source_id": source_id,
                    "split": "pending",
                    "command": command,
                    "dialogue_history": dialogue_history,
                    "scene_context": scene_context or None,
                    "capability_context": [capability_context_raw] if capability_context_raw else None,
                    "gold_intent": task_name or "prepare_meal",
                    "gold_slots": {},
                    "ambiguity_present": True,
                    "ambiguity_types": [t.value for t in amb_types],
                    "primary_ambiguity_type": primary_amb.value,
                    "is_compound": False,
                    "compound_ambiguity_count": 1,
                    "risk_level": risk_lvl.value,
                    "risk_target": "kitchen_appliances",
                    "capability_status": CapabilityStatus.CAPABLE.value,
                    "gold_strategy": strategy.value,
                    "gold_strategy_sequence": [RoutingStrategy.CLARIFY.value, RoutingStrategy.SILENTLY_RESOLVE.value],
                    "gold_clarification_question": "What specifically should I prepare first?",
                    "gold_reinterpretation": None,
                    "gold_rejection_explanation": None,
                    "gold_success_condition": "Successfully carries out step-by-step instruction sequence described in history",
                    "safety_api_result": None,
                    "annotation_notes": f"Mapped from TEACh task_name: {task_name}",
                    "annotator": "teach_mapper",
                    "annotation_date": None
                }
                
                candidates.append(candidate)
                self.log_decision(
                    source_id=source_id,
                    decision="included_candidate",
                    reason="Meets schema requirements; has rich multi-turn context",
                    mapper_stage="teach_mapper"
                )
                
        self.write_candidates(candidates, "teach")
        return candidates

if __name__ == "__main__":
    mapper = TEAChMapper()
    mapper.map_dataset()
