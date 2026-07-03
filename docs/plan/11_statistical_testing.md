---
title: "Statistical Significance Testing"
section: 11
description: "McNemar test, bootstrap CIs, and optional synthetic robustness analysis."
---

## 11. Statistical Significance Testing

Flat accuracy numbers are not enough. The final report must quantify uncertainty and paired system differences.

## McNemar Test

Primary comparison: proposed manager vs best-performing baseline on frozen-test strict routing correctness.

Use:

- exact McNemar if discordant pairs are small
- continuity-corrected chi-square McNemar otherwise
- alpha = 0.05
- report `b`, `c`, statistic, p-value, and accuracy difference

TEACh turns from the same episode are correlated. Collapse to the first ambiguous turn per episode for significance testing.

## Bootstrap Confidence Intervals

Use paired bootstrap with seed 42 and 10,000 resamples for:

- overall routing accuracy
- paired routing accuracy difference
- compound routing accuracy
- high-risk routing accuracy
- unsafe silent-resolution rate

If zero unsafe events are observed, report an exact/binomial upper confidence bound. Do not claim the system is safe from zero observed events alone.

## Optional Synthetic Robustness Set

Synthetic rewrites are optional robustness analysis, not the basis of the primary statistical claim.

If used:

- keep rewrites separate from the human-labelled frozen test set
- validate semantic preservation
- report results separately
- use cluster bootstrap by parent example if inferential statistics are shown
- do not claim inflated power from correlated rewrites

## Coding LLM Checklist

- [ ] Implement strict routing correctness: `predicted_strategy == gold_strategy`.
- [ ] Implement exact/continuity-corrected McNemar as appropriate.
- [ ] Bootstrap paired differences with seed 42.
- [ ] Keep synthetic robustness statistics separate from primary statistics.
- [ ] Save `b`, `c`, p-value, confidence intervals, and sample counts.

## Human Checklist

- [ ] Confirm the best baseline is selected before interpreting McNemar.
- [ ] Confirm TEACh correlated turns are collapsed for significance testing.
- [ ] Confirm synthetic rewrites are not described as independent evidence.
- [ ] Interpret non-significant results honestly as inconclusive or mixed.
- [ ] Check that statistical claims directly answer the research question.

---
**Previous:** [Ablation Studies](10_ablation_studies.md) | **Next:** [Failure Analysis](12_failure_analysis.md)
