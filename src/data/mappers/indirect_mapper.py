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

class IndirectMapper(BaseMapper):
    def __init__(self):
        super().__init__(SourceDataset.INDIRECT_REQUESTS)
        
    def map_dataset(self) -> List[Dict[str, Any]]:
        dataset_dir = self.project_root / "data" / "raw" / "IndirectRequests"
        csv_path = dataset_dir / "indirect_requests_standardized.csv"
        
        candidates = []
        if not csv_path.exists():
            print(f"IndirectRequests standardized file not found: {csv_path}")
            return candidates
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                source_id = row.get("source_id", f"ir_{idx}")
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
                    
                target_slot_value = metadata.get("target_slot_value", "")
                slot_description = metadata.get("slot_description", "")
                possible_slot_values = metadata.get("possible_slot_values", "")
                
                # Exclusion checks
                if not command:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing command text",
                        mapper_stage="indirect_mapper"
                    )
                    continue
                    
                # Map target slot ambiguity to strategy
                strategy = RoutingStrategy.SILENTLY_RESOLVE
                if target_slot_value == "<ambiguous>":
                    strategy = RoutingStrategy.CLARIFY
                
                # Set slots
                gold_slots = {}
                if slot_description:
                    gold_slots[slot_description] = target_slot_value
                
                candidate = {
                    "example_id": f"indirect_requests_{source_id}",
                    "source_dataset": self.source_dataset.value,
                    "source_id": source_id,
                    "split": "pending",
                    "command": command,
                    "dialogue_history": [],
                    "scene_context": scene_context or None,
                    "capability_context": [capability_context_raw] if capability_context_raw else None,
                    "gold_intent": "find_service",
                    "gold_slots": gold_slots,
                    "ambiguity_present": True,
                    "ambiguity_types": [AmbiguityType.PRAGMATIC.value],
                    "primary_ambiguity_type": AmbiguityType.PRAGMATIC.value,
                    "is_compound": False,
                    "compound_ambiguity_count": 1,
                    "risk_level": RiskLevel.NONE.value,
                    "risk_target": None,
                    "capability_status": CapabilityStatus.CAPABLE.value,
                    "gold_strategy": strategy.value,
                    "gold_strategy_sequence": None,
                    "gold_clarification_question": f"Which {slot_description.lower()} do you prefer?" if strategy == RoutingStrategy.CLARIFY else None,
                    "gold_reinterpretation": f"User is asking to find a service with details: {slot_description} = {target_slot_value}",
                    "gold_rejection_explanation": None,
                    "gold_success_condition": None,
                    "safety_api_result": None,
                    "annotation_notes": f"Mapped from IndirectRequests: target slot value is {target_slot_value}, slot description is {slot_description}",
                    "annotator": "indirect_mapper",
                    "annotation_date": None
                }
                
                candidates.append(candidate)
                self.log_decision(
                    source_id=source_id,
                    decision="included_candidate",
                    reason="Meets schema requirements; has clear indirect pragmatic command",
                    mapper_stage="indirect_mapper"
                )
                
        self.write_candidates(candidates, "indirect_requests")
        return candidates

if __name__ == "__main__":
    mapper = IndirectMapper()
    mapper.map_dataset()
