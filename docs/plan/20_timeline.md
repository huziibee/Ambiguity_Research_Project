---
title: "Timeline"
section: 20
description: "Phase-by-phase timeline, fallback plan, and minimum viable submission checklist."
---

## 20. Timeline

## Phase 1: Schema and Smoke Test

| Deliverable | Done when |
|-------------|-----------|
| schema/config support | `risk_mode="predicted"` exists |
| `dev_20` | validates and covers all strategies |
| baseline/proposed smoke run | predictions, metrics, draft Table 1 exist |

## Phase 2: Dataset and Annotation

Goal: 400 labelled examples if feasible, frozen 80-example test set minimum.

| Deliverable | Done when |
|-------------|-----------|
| `compound_50.jsonl` | human validated |
| source mappers | interim files and filtering log exist |
| split files | `dev_80`, `train`, `test`, manifest exist |
| IAA | kappa/Jaccard computed and adjudicated |

## Phase 3: Gemini Prompting and Baseline Refinement

| Deliverable | Done when |
|-------------|-----------|
| Gemini structured prompts | validate on `dev_80` |
| predicted-risk path | primary config uses `predicted` |
| baseline audit | no gold leakage |
| HPC fallback scripts | available if Gemini throttles |

## Phase 4: Final Evaluation and Ablations

| Deliverable | Done when |
|-------------|-----------|
| all systems on frozen test | cached predictions exist |
| ablations | Table 2 exists |
| stats | McNemar and bootstrap CIs exist |
| subgroup tables | Tables 3-6 exist |

## Phase 5: Failure Analysis and Figures

| Deliverable | Done when |
|-------------|-----------|
| failure analysis | Table 10 and representative errors exist |
| figures | Figures 1-8 exist |
| source/IAA tables | Tables 7-8 exist |

## Phase 6: Optional Extensions

Only after primary results are reproducible:

- external safety API
- rule-only manager
- synthetic robustness set
- local LLM/SFT on HPC

## Phase 7: Report Integration

| Deliverable | Done when |
|-------------|-----------|
| methodology | matches code and artifacts |
| results | tables/figures interpreted |
| limitations | explicit and honest |
| reproducibility | one-command cached run works |

## Minimum Viable Submission

- [ ] frozen test set with at least 80 examples
- [ ] all five systems evaluated
- [ ] Table 1
- [ ] at least no-type and no-risk ablations
- [ ] McNemar or clear note why underpowered
- [ ] IAA reported
- [ ] representative failures
- [ ] limitations
- [ ] cached reproduction

## Coding LLM Checklist

- [ ] Keep phases ordered: data and labels before final system claims.
- [ ] Do not start optional SFT/local-LLM work before Gemini-first evaluation is reproducible.
- [ ] Produce cached predictions before statistics and figures.
- [ ] Ensure every phase has concrete artifacts.
- [ ] Keep fallback scope documented if the 400-example target is reduced.

## Human Checklist

- [ ] Approve any fallback from 400 examples to a smaller dataset.
- [ ] Check IAA and label quality before final prediction runs.
- [ ] Confirm no prompt tuning happens after test freeze.
- [ ] Review all final tables before writing interpretation.
- [ ] Confirm limitations are written before final conclusion polish.

---
**Previous:** [Quality Gates](19_quality_gates.md) | **Next:** [Report Alignment](21_report_alignment.md)
