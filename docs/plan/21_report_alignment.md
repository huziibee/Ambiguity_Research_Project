---
title: "Report Alignment"
section: 21
description: "Mapping artifacts to rubric requirements and final report structure."
---

## 21. Report Alignment

The report must tell a bounded story: a Gemini-first, text-only NLU routing experiment tests whether explicit type/risk/capability routing improves routing decisions for compound ambiguous robot commands.

## Artifact to Rubric Mapping

| Artifact | Rubric support |
|----------|----------------|
| Table 1 | enough empirical results to answer RQ |
| Tables 2-6 | clear understanding of where results come from |
| Tables 7-8 | credible data and label methodology |
| Table 9 | statistical credibility |
| Table 10 | limitations and failure understanding |
| cached predictions | reproducibility |
| annotation guidelines | method rigor |
| failure cases | author interpretation |

## Results Narrative

1. Lead with Table 1 and routing accuracy.
2. Explain compound and high-risk subgroup results.
3. Use ablations to explain type/risk/capability contributions.
4. Use statistics to describe confidence, not overclaim certainty.
5. Use failure analysis to explain what still fails and why.

## Handling Negative or Mixed Results

Negative results are acceptable if the analysis is honest:

- If proposed manager loses overall, say so.
- If it only helps compound/high-risk cases, frame that as a scoped finding.
- If ablations do not change performance, discuss redundancy or weak labels.
- If classification is the bottleneck, distinguish that from routing-policy failure.

## Required Limitations

- text-only routing, not embodied execution
- gold strategy subjectivity
- hybrid dataset mapping
- manual compound examples may contain artifacts
- limited high-risk subgroup size
- Gemini free-tier volatility and privacy constraints
- no human-subject/user-trust evaluation
- synthetic robustness, if used, is correlated and secondary

## Coding LLM Checklist

- [ ] Generate report-ready CSVs and figures from reproducible scripts.
- [ ] Keep table names and metrics consistent with plan docs.
- [ ] Store representative failure cases with human-editable analysis fields.
- [ ] Do not generate final interpretation as unverified model prose.
- [ ] Ensure README links artifacts to report tables.

## Human Checklist

- [ ] Write the final result interpretation yourself or review it line by line.
- [ ] Confirm every claim points to a table, figure, or failure case.
- [ ] Confirm limitations directly follow from observed data and methodology.
- [ ] Confirm the conclusion answers the exact research question.
- [ ] Confirm AI/tool usage is declared accurately.

---
**Previous:** [Timeline](20_timeline.md) | **Next:** [Risks and Mitigations](22_risks_mitigations.md)
