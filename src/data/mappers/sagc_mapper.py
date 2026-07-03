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

class SAGCMapper(BaseMapper):
    def __init__(self):
        super().__init__(SourceDataset.SAGC)
        
    def map_dataset(self) -> List[Dict[str, Any]]:
        dataset_dir = self.project_root / "data" / "raw" / "CLARA-Dataset"
        csv_path = dataset_dir / "clara_standardized.csv"
        
        candidates = []
        if not csv_path.exists():
            print(f"CLARA standardized file not found: {csv_path}")
            return candidates
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                source_id = row.get("source_id", f"clara_{idx}")
                command = row.get("command", "").strip()
                scene_context = row.get("scene_context", "").strip()
                capability_context_raw = row.get("capability_context", "").strip()
                original_split = row.get("original_split", "").strip()
                
                # Parse metadata JSON
                metadata_str = row.get("metadata", "{}")
                try:
                    metadata = json.loads(metadata_str)
                except Exception as e:
                    metadata = {}
                    
                label = metadata.get("label")
                task = metadata.get("task", "")
                
                # Exclusion checks
                if not command:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing command text",
                        mapper_stage="sagc_mapper"
                    )
                    continue
                    
                # Exclude label = 3 (ignore/out of scope)
                if label == 3:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Label 3 marked as out of scope",
                        mapper_stage="sagc_mapper"
                    )
                    continue
                
                # Map label to strategy and capability
                strategy = RoutingStrategy.EXECUTE
                capability_status = CapabilityStatus.CAPABLE
                ambiguity_present = False
                amb_types = []
                primary_amb = None
                risk_lvl = RiskLevel.NONE
                
                if label == 0:
                    strategy = RoutingStrategy.EXECUTE
                    capability_status = CapabilityStatus.CAPABLE
                    ambiguity_present = False
                    risk_lvl = RiskLevel.NONE
                elif label == 1:
                    strategy = RoutingStrategy.CLARIFY
                    capability_status = CapabilityStatus.CAPABLE
                    ambiguity_present = True
                    amb_types = [AmbiguityType.UNDERSPECIFIED]
                    primary_amb = AmbiguityType.UNDERSPECIFIED
                    risk_lvl = RiskLevel.LOW
                elif label == 2:
                    strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
                    capability_status = CapabilityStatus.INCAPABLE
                    ambiguity_present = False
                    risk_lvl = RiskLevel.MEDIUM
                else:
                    # Fallback or unknown
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason=f"Unknown label value: {label}",
                        mapper_stage="sagc_mapper"
                    )
                    continue
                
                # Set capability context if available
                cap_context = [task] if task else []
                
                candidate = {
                    "example_id": f"sagc_{source_id}",
                    "source_dataset": self.source_dataset.value,
                    "source_id": source_id,
                    "split": "pending",
                    "command": command,
                    "dialogue_history": [],
                    "scene_context": scene_context,
                    "capability_context": cap_context,
                    "gold_intent": task or "unknown",
                    "gold_slots": {},
                    "ambiguity_present": ambiguity_present,
                    "ambiguity_types": [t.value for t in amb_types],
                    "primary_ambiguity_type": primary_amb.value if primary_amb else None,
                    "is_compound": False,
                    "compound_ambiguity_count": len(amb_types),
                    "risk_level": risk_lvl.value,
                    "risk_target": "infeasible_action" if label == 2 else None,
                    "capability_status": capability_status.value,
                    "gold_strategy": strategy.value,
                    "gold_strategy_sequence": None,
                    "gold_clarification_question": None,
                    "gold_reinterpretation": None,
                    "gold_rejection_explanation": "I cannot perform this task as it is infeasible with my configuration." if label == 2 else None,
                    "gold_success_condition": None,
                    "safety_api_result": None,
                    "annotation_notes": f"Mapped from SaGC label: {label}, task: {task}",
                    "annotator": "sagc_mapper",
                    "annotation_date": None
                }
                
                candidates.append(candidate)
                self.log_decision(
                    source_id=source_id,
                    decision="included_candidate",
                    reason="Meets schema requirements; has routing-relevant clear/ambiguous/infeasible status",
                    mapper_stage="sagc_mapper"
                )
                
        self.write_candidates(candidates, "sagc")
        return candidates

if __name__ == "__main__":
    mapper = SAGCMapper()
    mapper.map_dataset()
