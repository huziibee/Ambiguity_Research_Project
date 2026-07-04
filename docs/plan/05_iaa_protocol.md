---
title: "Inter-Annotator Agreement Protocol"
section: 5
description: "Double-annotation subset design, IAA metrics, interpretation guidance, scripts, and disagreement resolution."
---

## 5. Inter-Annotator Agreement Protocol

> [!IMPORTANT]
> IAA is mandatory for annotation credibility. It supports the claim that the 400 examples are human-labelled and that the labels are reliable enough for final evaluation.

IAA evaluates the gold labels. It does not change the final-evaluation rule: systems are evaluated with predicted risk, while gold risk is used to score and diagnose those predictions.

### 5.1 Double-Annotation Subset

Select 30 examples for double annotation. Prefer examples drawn from the candidate `test` split before freeze, with enough coverage to stress the hardest label decisions.

| Category | Count | Why |
|----------|-------|-----|
| Compound ambiguity with 2+ types | 10 | Hardest labelling task; likely disagreement point |
| Single ambiguity | 8 | Baseline difficulty calibration |
| Unsafe/infeasible or rejection-relevant | 6 | Risk and rejection labels are subjective |
| Clear/unambiguous execute cases | 6 | Sanity check for near-perfect agreement |

The second annotator can be a colleague, supervisor, or trained independent reviewer. Provide them with:

- The 30 examples with command, context, capabilities, and provenance only.
- The annotation guidelines and decision rules.
- A blank annotation template.
- No gold labels from the first annotator.

### 5.2 Metrics to Compute

| Field | Agreement Metric | Why This Metric |
|-------|------------------|-----------------|
| `primary_ambiguity_type` | Cohen's kappa | Single-label categorical; corrects for chance agreement |
| `risk_level` | Cohen's kappa | Single-label ordinal treated as categorical |
| `gold_strategy` | Cohen's kappa | Single-label categorical |
| `ambiguity_types` | Average Jaccard similarity | Multi-label set agreement with partial overlap |

Also compute exact agreement percentages for readability.

### 5.3 Interpretation Guidance

| Kappa Range | Interpretation |
|-------------|----------------|
| 0.81-1.00 | Almost perfect |
| 0.61-0.80 | Substantial; acceptable for this project |
| 0.41-0.60 | Moderate; report and discuss |
| <= 0.40 | Weak; revise guidelines, re-annotate, or report as a serious limitation |

Target: Cohen's kappa >= 0.75 for `primary_ambiguity_type`, `risk_level`, and `gold_strategy`. If below target, revise the guideline language, resolve disagreements, and re-annotate disagreement cases before freezing the test set.

### 5.4 Blind Manual Validation of Drafted Examples

Manual and LLM-assisted examples need additional protection against researcher bias:

1. A neutral reviewer validates drafted examples without seeing the intended gold labels.
2. The reviewer checks ambiguity types, primary type, risk level, strategy, and provenance plausibility.
3. An example is included only if disagreements are resolved by applying the operational rules.
4. Any rewritten example must be re-validated before inclusion.

This validation is human approval. LLM-only consensus is not enough for a gold label.

### 5.5 Scripts and Outputs

| Script | Purpose | Output |
|--------|---------|--------|
| `scripts/compute_iaa.py` | Takes annotator A and annotator B JSONL files and computes agreement metrics | `results/annotation/iaa_results.json` |
| `scripts/compute_iaa.py` | Generates a summary table | `results/tables/iaa_summary.csv` |

The script must not use Gemini, HPC, or any LLM. IAA is a deterministic analysis of human annotation files.

### 5.6 Disagreement Resolution

After computing IAA:

1. Identify all disagreement cases.
2. For each case, apply the operational rules from the gold label protocol.
3. If rules resolve the disagreement, use the rule-consistent label.
4. If rules remain ambiguous, discuss with a supervisor or second reviewer and document the decision.
5. Update the annotation guidelines if a new edge case is discovered.
6. Do not freeze `test.json` until disagreement resolution is complete.

## Coding LLM Checklist

- [ ] Implement deterministic IAA computation without LLM calls.
- [ ] Compute Cohen's kappa for `primary_ambiguity_type`, `risk_level`, and `gold_strategy`.
- [ ] Compute average Jaccard similarity for `ambiguity_types`.
- [ ] Export both machine-readable JSON and table-ready CSV outputs.
- [ ] Add checks that the double-annotation file omits first-pass gold labels from the second annotator view.

## Human Checklist

- [ ] Select 30 double-annotation examples that cover compound, single ambiguity, unsafe/rejection, and clear cases.
- [ ] Ensure the second annotator receives no first-annotator labels.
- [ ] Review every disagreement and document the final human-approved resolution.
- [ ] Confirm that below-target agreement triggers guideline revision or a clearly reported limitation.
- [ ] Verify that `test.json` is not frozen until IAA and disagreement resolution are complete.

---

**<- Previous:** [Gold Label Protocol](04_gold_label_protocol.md) | **Next ->** [Data Selection Logging](06_data_selection_logging.md)
