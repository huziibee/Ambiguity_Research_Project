---
title: "Proposed Router - Core Contribution"
section: 9
description: "Gemini structured extraction, deterministic type/risk/capability routing, and trace requirements."
---

## 9. Proposed Router - Core Contribution

The proposed manager is not a black-box learned router in the primary experiment. It is:

1. Gemini 3.1 Flash-Lite structured extraction of intent, slots, ambiguity, risk, and capability signals.
2. Deterministic routing rules over those signals.
3. Generated clarification or rejection text when needed.

## Pipeline

```text
ManagerInput
  -> Stage 1: parse intent and slots
  -> Stage 2: classify ambiguity types, primary type, compound status
  -> Stage 3: predict risk level from command/context
  -> Stage 4: check capability against available action repertoire
  -> Stage 5: route using explicit rules
  -> Stage 6: generate clarification/rejection text
  -> ManagerOutput
```

Stages 1-4 may be one compact Gemini structured call for quota efficiency. Stage 5 must remain deterministic and auditable.

## Routing Rules

Apply in order:

| Priority | Condition | Strategy |
|----------|-----------|----------|
| 1 | incapable | `face_preserving_rejection` |
| 2 | high/critical and unsafe to proceed | `face_preserving_rejection` |
| 3 | unambiguous, safe, capable | `execute` |
| 4 | compound ambiguity needing ordered handling | `multi_step` |
| 5 | referential or underspecified primary ambiguity | `clarify` |
| 6 | temporal/quantitative and none/low risk | `silently_resolve` |
| 7 | temporal/quantitative and medium+ risk | `clarify` |
| 8 | pragmatic and none/low risk | `silently_resolve` |
| 9 | pragmatic and medium+ risk | `clarify` |
| 10 | uncertainty/failure | clarify if low risk, reject or clarify conservatively if elevated risk |

## Multi-Step Sequence Rule

If compound:

1. Pragmatic reinterpretation first: `silently_resolve`.
2. Referential or underspecified gaps: `clarify`.
3. Temporal/quantitative low-risk gaps: `silently_resolve`.
4. Temporal/quantitative medium+ risk gaps: `clarify`.

## Context Sampling

Context sampling is optional for the primary run because Gemini free-tier throttling is possible. If enabled, use it only with a fixed call budget and tune thresholds on `dev_100`. If disabled, report this as a limitation and use single-pass structured output confidence/uncertainty fields.

## Coding LLM Checklist

- [ ] Keep routing rules deterministic and unit-testable.
- [ ] Implement primary risk prediction without reading gold `risk_level`.
- [ ] Cache every Gemini response with model ID, prompt hash, temperature, retry count, and schema version.
- [ ] Make context sampling configurable and off by default if quota is tight.
- [ ] Emit route reason strings for failure analysis.

## Human Checklist

- [ ] Approve the high-risk policy: reject vs clarify for recoverable ambiguity.
- [ ] Approve the policy for `unknown` and `partially_capable`.
- [ ] Review router traces for all five strategies before final evaluation.
- [ ] Confirm router policy matches the gold-label protocol.
- [ ] Confirm any disabled context-sampling feature is documented as a limitation.

---
**Previous:** [Systems Under Comparison](08_systems_under_comparison.md) | **Next:** [Ablation Studies](10_ablation_studies.md)
