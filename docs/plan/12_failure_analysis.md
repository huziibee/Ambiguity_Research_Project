---
title: "Failure Analysis"
section: 12
description: "Error taxonomy, analysis dimensions, representative cases, and required outputs."
---

## 12. Failure Analysis

Failure analysis is required. It is how the author demonstrates understanding of the results and discusses limitations.

## Error Layers

| Layer | Categories |
|-------|------------|
| Schema/API | invalid JSON, schema failure, retry exhaustion, rate-limit failure |
| Intent/slot | wrong intent, missing slot, wrong slot value, hallucinated slot |
| Ambiguity | missed type, extra type, wrong primary, missed compound, false compound |
| Risk | mismatch, high-risk underestimated, false high-risk escalation, hazard type wrong |
| Capability | wrong capability, false capable, false incapable, partial capability mishandled |
| Context/history | ignored dialogue history, ignored scene context, stale referent |
| Routing | over-clarify, under-clarify, missed rejection, false rejection, unsafe silent resolution, wrong multi-step sequence |
| Output quality | vague clarification, wrong target, poor rejection explanation |
| Data/gold issue | ambiguous gold label, mapping error, manual example artifact |

Each representative failure needs one primary root cause and optional secondary tags.

## Analysis Dimensions

Break failures down by:

- ambiguity type
- compound vs non-compound
- risk level
- source dataset
- gold strategy
- predicted strategy
- system

## Required Outputs

| Output | Contents |
|--------|----------|
| `results/tables/failure_analysis.csv` | counts by error layer/category |
| `results/failure_cases/representative_errors.json` | 8-12 human-interpreted cases |
| Table 10 | report-ready summary |

Representative cases must include command, source, gold labels, prediction, root cause, and human-written explanation.

## Coding LLM Checklist

- [ ] Implement automatic error tagging where deterministic.
- [ ] Output failure counts by layer, category, source, risk, strategy, and compound status.
- [ ] Include raw prediction references for every representative failure.
- [ ] Separate upstream classification failures from downstream routing-policy failures.
- [ ] Generate Table 10 from saved failure artifacts.

## Human Checklist

- [ ] Select 8-12 representative failures manually.
- [ ] Write or approve the explanation for every representative failure.
- [ ] Check whether any failure is actually a gold-label/data issue.
- [ ] Use failure analysis to write limitations and future work.
- [ ] Confirm the discussion explains why systems behaved differently.

---
**Previous:** [Statistical Significance Testing](11_statistical_testing.md) | **Next:** [Safety API Integration](13_safety_api.md)
