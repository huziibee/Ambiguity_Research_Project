---
title: "Minimum Viable Experiment"
section: 2
description: "Phase 1 deliverables, non-goals, and definition of done for the first smoke test."
---

## 2. Minimum Viable Experiment

Phase 1 produces a working smoke-test experiment on 20 examples. This must be built first because it proves the schema, systems, prediction writing, metric computation, and table generation all work.

`dev_20` is not final evidence. It is a plumbing check. The final research question is answered only by the frozen held-out `test` split of 150 human-approved examples.

`dev_20` must be a subset of `dev_100`, not a separate source of 20 additional examples. The smoke test should use **Gemini 3.1 Flash-Lite free-tier first** for LLM-backed calls. HPC, SFT, and local model training must not be introduced to complete the MVE.

## Phase 1 Deliverables

| Deliverable | Concrete requirement |
|-------------|----------------------|
| `src/schema.py` | Pydantic v2 models for `Example`, `ManagerInput`, and `ManagerOutput`, including `risk_mode="predicted"` |
| `data/processed/dev_100.jsonl` | 100 human-approved development examples |
| `data/processed/dev_20.jsonl` | 20-example subset of `dev_100`, validated against schema and covering all five routing strategies |
| 4 baselines | `always_clarify`, `always_resolve`, `degree_based`, `direct_llm` each produce valid `ManagerOutput` |
| Proposed router | Gemini 3.1 Flash-Lite-compatible staged pipeline and deterministic router produce valid `ManagerOutput` |
| `src/evaluation/metrics.py` | Computes strict primary and supporting metrics |
| Smoke table | Smoke-test CSV for 5 systems x metrics on `dev_20`; not a final Table 1 result |

## Phase 1 Non-Goals

| Excluded | Why |
|----------|-----|
| TEACh mapping | Dataset mapping belongs to Phase 2 |
| Fine-tuning / SFT | Optional fallback/extension only; not core to the primary experiment |
| Safety API dependency | Primary path uses predicted risk or deterministic mock for smoke tests |
| HPC jobs | Phase 1 must run locally unless Gemini throttling blocks progress and fallback is explicitly logged |
| Final claims | `dev_20` is too small and development-facing |

## Phase 1 Definition of Done

```powershell
python scripts/run_evaluation.py --config configs/dev_20.yaml
```

The command must produce:

- `results/smoke/dev_20/predictions/{always_clarify,always_resolve,degree_based,direct_llm,proposed_manager}.jsonl`
- `results/smoke/dev_20/metrics/{always_clarify,always_resolve,degree_based,direct_llm,proposed_manager}.json`
- `results/smoke/dev_20/tables/table1_smoke_dev_20.csv`
- zero schema validation errors
- numbers in every Table 1 cell
- explicit logs for any Gemini failure or fallback
- `risk_mode="predicted"` unless a run is explicitly marked diagnostic

Heuristic fallback is allowed for smoke testing only. It is forbidden in final `direct_llm` evaluation.

## Coding LLM Checklist

- [ ] Ensure `dev_20` loads through `Example` with zero validation errors.
- [ ] Generate `dev_20` from `dev_100`, not as an independent split.
- [ ] Ensure every system returns valid `ManagerOutput`.
- [ ] Add or preserve `risk_mode="predicted"` support before any final-style run.
- [ ] Cache and log Gemini 3.1 Flash-Lite calls if Gemini is used in the smoke test.
- [ ] Label generated `dev_20` tables as smoke-test outputs, not final results.

## Human Checklist

- [ ] Read all 20 examples and confirm every gold strategy is reasonable.
- [ ] Verify every risk label is defensible by the annotation rules.
- [ ] Verify all five routing strategies appear at least once.
- [ ] Confirm all 20 smoke examples are included in `dev_100`.
- [ ] Confirm no `dev_20` number is used as evidence in the final report.
- [ ] Confirm any Gemini free-tier call contains no sensitive/private data.

---
**Previous:** [Target Outputs](01_target_outputs.md) | **Next:** [Data and Schema Plan](03_data_schema.md)
