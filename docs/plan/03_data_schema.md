---
title: "Data and Schema Plan"
section: 3
description: "Shared JSONL schema, enum definitions, and system input/output contracts."
---

## 3. Data and Schema Plan

The schema is the single source of truth. Every example, system input, and system output must validate before it can be used in metrics.

## Example Record

Every `.jsonl` line must contain:

- identity: `example_id`, `source_dataset`, `source_id`, `split`
- input: `command`, `dialogue_history`, `scene_context`, `capability_context`
- gold interpretation: `gold_intent`, `gold_slots`
- gold ambiguity: `ambiguity_present`, `ambiguity_types`, `primary_ambiguity_type`, `is_compound`, `compound_ambiguity_count`
- gold risk/capability: `risk_level`, `risk_target`, `capability_status`
- gold routing: `gold_strategy`, `gold_strategy_sequence`, clarification/reinterpretation/rejection fields
- provenance: `annotation_notes`, `annotator`, `annotation_date`

## Required Enums

| Enum | Values |
|------|--------|
| `AmbiguityType` | `pragmatic`, `referential`, `temporal`, `quantitative`, `underspecified`, `none` |
| `RiskLevel` | `none`, `low`, `medium`, `high`, `critical` |
| `CapabilityStatus` | `capable`, `partially_capable`, `incapable`, `unknown` |
| `RoutingStrategy` | `execute`, `clarify`, `silently_resolve`, `face_preserving_rejection`, `multi_step` |
| `SourceDataset` | `manual`, `ambik`, `sagc`, `teach`, `indirect_requests`, `safe_agent_bench` |

## Validation Rules

- If `ambiguity_present == false`, then `ambiguity_types == []` and `primary_ambiguity_type == null`.
- `"none"` must not appear alongside other ambiguity types.
- `is_compound == (len(ambiguity_types) >= 2)`.
- `compound_ambiguity_count == len(ambiguity_types)`.
- `gold_strategy_sequence` is required when `gold_strategy == "multi_step"`.
- `annotation_notes` are required for compound, medium/high/critical risk, and rejection cases.

## Manager Input Contract

`ManagerInput` contains only information available to a real system:

- `command`
- `dialogue_history`
- `scene_context`
- `capability_context`
- `risk_mode`

`risk_mode` must support:

- `predicted`: primary experiment; predict risk from command/context
- `gold`: diagnostic/oracle ablation only
- `mock`: development tests only
- `api`: optional external safety API

Primary final evaluation must not pass gold `risk_level` to systems except in `gold` diagnostic runs.

## Manager Output Contract

Every system returns validated `ManagerOutput`:

- `predicted_intent`
- `predicted_slots`
- `predicted_ambiguity_types`
- `predicted_primary_ambiguity_type`
- `predicted_is_compound`
- `predicted_capability_status`
- `predicted_risk_level`
- `predicted_strategy`
- `predicted_strategy_sequence`
- `predicted_clarification_question`
- `predicted_rejection_explanation`

## Coding LLM Checklist

- [ ] Update `src/schema.py` to match this document exactly.
- [ ] Generate JSON schemas into `schemas/`.
- [ ] Add validation for required annotation notes and multi-step sequences.
- [ ] Ensure final runner uses `risk_mode="predicted"` by default.
- [ ] Strip source metadata and gold labels from model prompts.

## Human Checklist

- [ ] Review schema fields before large annotation begins.
- [ ] Confirm every enum value is sufficient and not overlapping.
- [ ] Confirm `risk_mode="gold"` is only used for diagnostics.
- [ ] Check sampled JSONL rows manually for schema and label sanity.
- [ ] Approve schema freeze before final test split freeze.

---
**Previous:** [Minimum Viable Experiment](02_minimum_viable_experiment.md) | **Next:** [Gold Label Protocol](04_gold_label_protocol.md)
