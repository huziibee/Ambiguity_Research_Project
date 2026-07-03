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

class SafetyBenchMapper(BaseMapper):
    def __init__(self):
        super().__init__(SourceDataset.SAFE_AGENT_BENCH)
        
    def _map_risk_level(self, risk_category: str) -> RiskLevel:
        cat = risk_category.lower()
        if any(keyword in cat for keyword in ("fire", "explosion", "electrical shock", "shock")):
            return RiskLevel.CRITICAL
        if any(keyword in cat for keyword in ("harm", "injury", "cut", "sharp", "knife", "blade")):
            return RiskLevel.HIGH
        if any(keyword in cat for keyword in ("break", "damage", "spill", "liquid", "misuse")):
            return RiskLevel.MEDIUM
        if any(keyword in cat for keyword in ("slip", "stain", "loss")):
            return RiskLevel.LOW
        return RiskLevel.MEDIUM

    def map_dataset(self) -> List[Dict[str, Any]]:
        dataset_dir = self.project_root / "data" / "raw" / "SafeAgentBench"
        csv_path = dataset_dir / "safe_agent_bench_standardized.csv"
        
        candidates = []
        if not csv_path.exists():
            print(f"SafeAgentBench standardized file not found: {csv_path}")
            return candidates
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                source_id = row.get("source_id", f"sab_{idx}")
                command = row.get("command", "").strip()
                scene_context = row.get("scene_context", "").strip()
                original_split = row.get("original_split", "").strip()
                
                # Parse metadata JSON
                metadata_str = row.get("metadata", "{}")
                try:
                    metadata = json.loads(metadata_str)
                except Exception as e:
                    metadata = {}
                    
                risk_category = metadata.get("risk_category", "")
                
                # Exclusion checks
                if not command:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason="Missing command text",
                        mapper_stage="safety_bench_mapper"
                    )
                    continue
                    
                # Map based on split
                strategy = RoutingStrategy.EXECUTE
                risk_lvl = RiskLevel.NONE
                ambiguity_present = False
                amb_types = []
                primary_amb = None
                
                if original_split == "unsafe_detailed":
                    strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
                    risk_lvl = self._map_risk_level(risk_category)
                    ambiguity_present = False
                elif original_split == "safe_detailed":
                    strategy = RoutingStrategy.EXECUTE
                    risk_lvl = RiskLevel.LOW if risk_category else RiskLevel.NONE
                    ambiguity_present = False
                elif original_split == "abstract":
                    strategy = RoutingStrategy.FACE_PRESERVING_REJECTION
                    risk_lvl = self._map_risk_level(risk_category)
                    ambiguity_present = True
                    amb_types = [AmbiguityType.PRAGMATIC]
                    primary_amb = AmbiguityType.PRAGMATIC
                else:
                    self.log_decision(
                        source_id=source_id,
                        decision="excluded",
                        reason=f"Unknown original split: {original_split}",
                        mapper_stage="safety_bench_mapper"
                    )
                    continue
                    
                candidate = {
                    "example_id": f"safe_agent_bench_{source_id}",
                    "source_dataset": self.source_dataset.value,
                    "source_id": source_id,
                    "split": "pending",
                    "command": command,
                    "dialogue_history": [],
                    "scene_context": f"Floorplan: {scene_context}" if scene_context else None,
                    "capability_context": None,
                    "gold_intent": "unknown",
                    "gold_slots": {},
                    "ambiguity_present": ambiguity_present,
                    "ambiguity_types": [t.value for t in amb_types],
                    "primary_ambiguity_type": primary_amb.value if primary_amb else None,
                    "is_compound": False,
                    "compound_ambiguity_count": len(amb_types),
                    "risk_level": risk_lvl.value,
                    "risk_target": risk_category or None,
                    "capability_status": CapabilityStatus.CAPABLE.value,
                    "gold_strategy": strategy.value,
                    "gold_strategy_sequence": None,
                    "gold_clarification_question": None,
                    "gold_reinterpretation": None,
                    "gold_rejection_explanation": f"I cannot execute this request as it violates safety guidelines due to {risk_category.lower()}." if original_split == "unsafe_detailed" else None,
                    "gold_success_condition": None,
                    "safety_api_result": None,
                    "annotation_notes": f"Mapped from SafeAgentBench: {original_split}, risk category: {risk_category}",
                    "annotator": "safety_bench_mapper",
                    "annotation_date": None
                }
                
                candidates.append(candidate)
                self.log_decision(
                    source_id=source_id,
                    decision="included_candidate",
                    reason="Meets schema requirements; provides clear safety/rejection cases",
                    mapper_stage="safety_bench_mapper"
                )
                
        self.write_candidates(candidates, "safe_agent_bench")
        return candidates

if __name__ == "__main__":
    mapper = SafetyBenchMapper()
    mapper.map_dataset()
