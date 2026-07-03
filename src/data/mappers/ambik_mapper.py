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

class AmbiKMapper(BaseMapper):
    def __init__(self):
        super().__init__(SourceDataset.AMBIK)
        
    def map_dataset(self) -> List[Dict[str, Any]]:
        dataset_dir = self.project_root / "data" / "raw" / "AmbiK"
        csv_path = dataset_dir / "ambik_standardized.csv"
        
        candidates = []
        if not csv_path.exists():
            print(f"AmbiK standardized file not found: {csv_path}")
            return candidates
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                source_id = row.get("source_id", f"ambik_{idx}")
                command = row.get("command", "").strip()
                scene_context = row.get("scene_context", "").strip()
                original_split = row.get("original_split", "").strip()
                
                # Parse metadata JSON
                metadata_str = row.get("metadata", "{}")
                try:
                    metadata = json.loads(metadata_str)
                except Exception as e:
                    print(f"[Warning] Failed to parse metadata JSON for source_id {source_id}: {e}")
                    metadata = {}
                
                ambiguity_type_raw = metadata.get("ambiguity_type", "").strip()
                question = metadata.get("question", "").strip()
                unambiguous_direct = metadata.get("unambiguous_direct", "").strip()
                user_intent = metadata.get("user_intent", "").strip()
                
                # Exclusion checks
                if not command:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing command text",
                        mapper_stage="ambik_mapper"
                    )
                    continue
                    
                # Mapping ambiguity types based on AmbiK metadata
                amb_types = []
                primary_amb = None
                strategy = RoutingStrategy.CLARIFY
                risk_lvl = RiskLevel.NONE
                
                if ambiguity_type_raw == "preferences":
                    amb_types = [AmbiguityType.UNDERSPECIFIED]
                    primary_amb = AmbiguityType.UNDERSPECIFIED
                    strategy = RoutingStrategy.CLARIFY
                    risk_lvl = RiskLevel.LOW
                elif ambiguity_type_raw == "common_sense_knowledge":
                    amb_types = [AmbiguityType.PRAGMATIC]
                    primary_amb = AmbiguityType.PRAGMATIC
                    strategy = RoutingStrategy.SILENTLY_RESOLVE
                    risk_lvl = RiskLevel.NONE
                elif ambiguity_type_raw == "safety":
                    amb_types = [AmbiguityType.UNDERSPECIFIED]
                    primary_amb = AmbiguityType.UNDERSPECIFIED
                    strategy = RoutingStrategy.CLARIFY
                    risk_lvl = RiskLevel.MEDIUM
                else:
                    amb_types = [AmbiguityType.UNDERSPECIFIED]
                    primary_amb = AmbiguityType.UNDERSPECIFIED
                    strategy = RoutingStrategy.CLARIFY
                    risk_lvl = RiskLevel.NONE
                
                # Setup candidate dictionary conforming to Example fields
                candidate = {
                    "example_id": f"ambik_{source_id}",
                    "source_dataset": self.source_dataset.value,
                    "source_id": source_id,
                    "split": "pending",
                    "command": command,
                    "dialogue_history": [],
                    "scene_context": scene_context,
                    "capability_context": None,
                    "gold_intent": "unknown", 
                    "gold_slots": {"user_intent": user_intent} if user_intent else {},
                    "ambiguity_present": True,
                    "ambiguity_types": [t.value for t in amb_types],
                    "primary_ambiguity_type": primary_amb.value if primary_amb else None,
                    "is_compound": False,
                    "compound_ambiguity_count": len(amb_types),
                    "risk_level": risk_lvl.value,
                    "risk_target": "safety_precaution" if ambiguity_type_raw == "safety" else None,
                    "capability_status": CapabilityStatus.UNKNOWN.value,
                    "gold_strategy": strategy.value,
                    "gold_strategy_sequence": None,
                    "gold_clarification_question": question or None,
                    "gold_reinterpretation": None,
                    "gold_rejection_explanation": None,
                    "gold_success_condition": unambiguous_direct or None,
                    "safety_api_result": None,
                    "annotation_notes": f"Mapped from AmbiK ambiguity_type: {ambiguity_type_raw}",
                    "annotator": "ambik_mapper",
                    "annotation_date": None
                }
                
                candidates.append(candidate)
                self.log_decision(
                    source_id=source_id,
                    decision="included_candidate",
                    reason="Meets schema requirements; has routing-relevant ambiguity signal",
                    mapper_stage="ambik_mapper"
                )
                
        self.write_candidates(candidates, "ambik")
        return candidates

if __name__ == "__main__":
    mapper = AmbiKMapper()
    mapper.map_dataset()
