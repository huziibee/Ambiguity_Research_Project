---
title: "Safety API Integration and Risk Prediction"
section: 13
description: "Risk sourcing modes, predicted-risk primary evaluation, and optional safety API contract."
---

## 13. Safety API Integration and Risk Prediction

The primary experiment uses predicted risk, not gold risk. This prevents leakage and makes the evaluation realistic.

## Risk Modes

| Mode | Source | Use |
|------|--------|-----|
| `predicted` | Gemini structured risk classification from command/context | primary experiment |
| `gold` | annotated `risk_level` | diagnostic/oracle ablation only |
| `mock` | deterministic mapping for tests | development only |
| `api` | external safety API | optional comparison |

## External Safety API Contract

Optional request:

```json
{"command": "Hand me the knife", "intent": "hand_object", "request_id": "uuid"}
```

Optional response:

```json
{"is_safe": false, "risk_score": 0.85, "risk_category": "high", "explanation": "Sharp object handling risk"}
```

Log timeout, retry count, latency, fallback, and source.

## Reporting Rule

Methodology wording:

> Risk input for the primary experiment is predicted directly from the command and context using Gemini 3.1 Flash-Lite structured output. Gold risk labels are used only in a diagnostic oracle ablation to estimate routing performance under perfect risk knowledge.

## Coding LLM Checklist

- [ ] Add `predicted`, `gold`, `mock`, and `api` risk modes in schema/config.
- [ ] Ensure final evaluation defaults to `predicted`, not `gold`.
- [ ] Log risk source, raw risk output, parsed risk, confidence if available, and fallback status.
- [ ] Ensure gold risk is inaccessible to Gemini prompts in primary runs.
- [ ] Implement API timeout/retry/fallback logging if external safety API is used.

## Human Checklist

- [ ] Review every high and critical gold risk label before freezing the test set.
- [ ] Review every critical Gemini risk prediction before reporting safety-sensitive claims.
- [ ] Confirm gold-risk runs are labelled diagnostic/oracle, not primary.
- [ ] Confirm free-tier Gemini data handling is acceptable for risk examples.
- [ ] Document any external safety API limitations or failures in the report.

---
**Previous:** [Failure Analysis](12_failure_analysis.md) | **Next:** [HPC Execution Plan](14_hpc_execution.md)
