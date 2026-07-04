---
title: "Systems Under Comparison"
section: 8
description: "All systems, baseline definitions, fairness requirements, and final-evaluation constraints."
---

## 8. Systems Under Comparison

All systems consume the same `ManagerInput` and produce validated `ManagerOutput`. Final results use the frozen `test.jsonl`, predicted risk, cached predictions, and identical metric functions.

## Systems

| System | Final definition | Gemini calls |
|--------|------------------|-------------:|
| `always_clarify` | Always predicts `clarify`; no parser/classifier advantage | 0 |
| `always_resolve` | Always predicts `silently_resolve`; exposes unsafe guessing | 0 |
| `degree_based` | Routes from scalar ambiguity degree plus predicted risk/capability; no type semantics | limited/configured |
| `direct_gemini` | Gemini 3.1 Flash-Lite maps input directly to full `ManagerOutput` | 1 per example |
| `proposed_manager` | Gemini structured extraction plus deterministic type/risk/capability router | 1 per example for extractor |

Final `direct_gemini` must not silently fall back to heuristics. Failed calls are logged and handled by the pre-declared fallback policy.

## Degree-Based Baseline

The degree baseline must be serious, not a strawman. It may use predicted risk and capability to reject unsafe or impossible commands, but it must not inspect ambiguity type labels.

Preferred ambiguity degree:

- Use N=5 slot-filling samples at temperature 0.7 if Gemini quota allows.
- Compute mean pairwise Jaccard distance over predicted slot sets.
- Tune thresholds only on `dev_80`.

Quota-aware fallback:

- If Gemini throttles, use one structured extractor confidence/uncertainty field or deterministic scalar heuristic.
- Label the fallback clearly in the report and limitations.

## Fairness Requirements

- Same frozen examples.
- Same visible input fields.
- Same output schema.
- Same primary model path for Gemini-backed systems.
- Same predicted-risk policy in primary runs.
- No gold risk, gold strategy, source ambiguity labels, or clarification answers in final model prompts.
- Fixed seeds for sampling, splitting, bootstrapping, and synthetic robustness if used.

## Coding LLM Checklist

- [ ] Ensure uniform baselines do not inherit proposed-manager parsing unless labelled as common-upstream diagnostics.
- [ ] Ensure direct Gemini has no heuristic fallback in final evaluation.
- [ ] Ensure proposed and direct Gemini use the same model ID and schema.
- [ ] Implement degree-based routing without ambiguity-type semantics.
- [ ] Log prediction source, fallback status, prompt hash, and validation result for every output.

## Human Checklist

- [ ] Audit every baseline for fairness before final evaluation.
- [ ] Confirm no system receives hidden gold labels or label-leaking metadata.
- [ ] Confirm degree-based routing is strong enough not to be a strawman.
- [ ] Confirm the comparison is about routing policy, not model-family differences.
- [ ] Confirm failed Gemini calls are handled according to the pre-declared policy.

---
**Previous:** [Dataset Construction Plan](07_dataset_construction.md) | **Next:** [Proposed Router - Core Contribution](09_proposed_router.md)
