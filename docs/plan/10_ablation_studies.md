---
title: "Ablation Studies"
section: 10
description: "Required ablations that isolate type, risk, and capability contributions."
---

## 10. Ablation Studies

Ablations are mandatory. Without them, the report can only say the full system worked or failed; it cannot say which signal mattered.

## Required Ablations

| System | Removed | Keeps | What it tests |
|--------|---------|-------|---------------|
| Full proposed | nothing | type + risk + capability | main system |
| `no_type` | ambiguity type semantics | ambiguity degree + risk + capability | whether type-awareness helps |
| `no_risk` | risk signal | type + capability | whether risk-awareness prevents unsafe routing |
| `no_capability` | capability context | type + risk | whether capability checking matters |

All ablations reuse cached extractor outputs where possible. They must not make extra Gemini calls unless a pre-declared diagnostic requires it.

## Table 2 Metrics

Report at minimum:

- routing accuracy
- compound routing accuracy
- high-risk routing accuracy
- clarification F1
- unsafe silent-resolution rate
- safe rejection rate

## Interpretation Rules

- Full vs `no_type`: evidence for or against type-awareness.
- Full vs `no_risk`: evidence for or against risk-awareness.
- Full vs `no_capability`: evidence for or against capability checks.
- If ablations match the full system, say so honestly and discuss redundancy or underpowered data.

## Coding LLM Checklist

- [ ] Implement all three required ablations.
- [ ] Ensure ablations use the same cached predictions/extractor signals as the full system.
- [ ] Ensure `no_type` does not inspect ambiguity-type labels.
- [ ] Ensure `no_risk` cannot use gold or predicted risk.
- [ ] Generate `results/tables/table2_ablations.csv`.

## Human Checklist

- [ ] Confirm each ablation removes exactly the intended signal.
- [ ] Review whether Table 2 actually supports the claimed contribution.
- [ ] Check unsafe silent-resolution changes manually for high/critical examples.
- [ ] Confirm non-improving ablations are reported honestly.
- [ ] Use ablation results in the report interpretation, not just as extra numbers.

---
**Previous:** [Proposed Router - Core Contribution](09_proposed_router.md) | **Next:** [Statistical Significance Testing](11_statistical_testing.md)
