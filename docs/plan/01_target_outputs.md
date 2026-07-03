---
title: "Target Outputs"
section: 1
description: "Required tables, figures, statistics, and saved artefacts that define done."
---

## 1. Target Outputs

The project is done only when final frozen-test evidence can answer the research question. The primary experiment uses **Gemini 3.1 Flash-Lite free-tier first** for LLM-backed systems. HPC is only a fallback/accelerator if Gemini throttles or later optional larger runs are explicitly approved.

All final main-result metrics must be computed on the frozen `test` split of **150 human-approved examples** using **predicted risk**. Gold risk may appear only in diagnostic tables, annotation summaries, and optional ablations.

`dev_20` outputs are smoke-test artifacts and must not be presented as final empirical evidence. `dev_20` is a subset of `dev_100`, not an additional dataset split.

## Required Tables

| Table | Contents | Purpose |
|-------|----------|---------|
| Table 1 | Main results: all systems x primary metrics on frozen `test` with predicted risk | Directly answer the research question |
| Table 2 | Ablations: full vs no-type vs no-risk vs no-capability | Show which routing signals matter |
| Table 3 | Compound vs non-compound performance | Test the compound ambiguity claim |
| Table 4 | Routing accuracy by predicted risk level, with gold-risk diagnostic comparison if needed | Test risk-awareness under realistic inference |
| Table 5 | Routing accuracy by ambiguity type | Test type-awareness |
| Table 6 | Strategy confusion matrix for proposed manager | Reveal routing error patterns |
| Table 7 | Data selection summary | Show raw -> excluded -> 310 human-approved included counts |
| Table 8 | IAA summary | Defend annotation reliability |
| Table 9 | McNemar test and bootstrap 95% CIs | Support statistical interpretation |
| Table 10 | Failure analysis summary with representative cases | Demonstrate understanding and limitations |

## Required Figures

| Figure | Type | Purpose |
|--------|------|---------|
| Fig 1 | Architecture diagram | Explain the method |
| Fig 2 | Routing accuracy bar chart | Main visual result |
| Fig 3 | Compound vs non-compound grouped bars | Compound ambiguity evidence |
| Fig 4 | Strategy confusion matrix heatmap | Error pattern evidence |
| Fig 5 | Routing accuracy by predicted risk level | Risk-awareness evidence under realistic inference |
| Fig 6 | Ablation comparison | Signal contribution evidence |
| Fig 7 | Error type distribution | Failure analysis evidence |
| Fig 8 | Bootstrap CI error bars | Uncertainty evidence |

## Required Statistics

- McNemar's test: proposed manager vs best-performing baseline on strict routing correctness.
- Bootstrap 95% CIs for routing accuracy, paired routing difference, compound-routing accuracy, high-risk routing accuracy, and unsafe silent-resolution rate.
- Cohen's kappa for `primary_ambiguity_type`, `risk_level`, and `gold_strategy`.
- Jaccard agreement for multi-label `ambiguity_types`.

## Required Saved Outputs

```text
results/
  predictions/*.jsonl
  metrics/*.json
  tables/*.csv
  figures/*.png
  statistics/significance_results.json
  statistics/bootstrap_ci.json
  annotation/iaa_results.json
  failure_cases/representative_errors.jsonl
```

Each prediction row must include the example ID, system name, parsed `ManagerOutput`, raw LLM output when relevant, model ID, prompt hash, temperature, retry count, cache key, schema version, and fallback status.

Smoke-test outputs should be saved under a clearly labelled path such as `results/smoke/dev_20/`. They may mirror final output formats, but they are not final evidence.

## Coding LLM Checklist

- [ ] Generate every required table as CSV from saved predictions.
- [ ] Generate every required figure from saved metrics/tables.
- [ ] Save raw and parsed Gemini 3.1 Flash-Lite responses for all LLM-backed primary runs.
- [ ] Keep synthetic robustness, HPC fallback, and gold-risk diagnostic outputs separate from primary frozen-test outputs.
- [ ] Ensure Table 1 uses predicted-risk strict routing correctness on the frozen `test` set.
- [ ] Store `dev_20` outputs under a smoke-test path and label them as non-final.

## Human Checklist

- [ ] Confirm Table 1 answers the research question directly.
- [ ] Confirm Tables 2-6 explain where the result comes from.
- [ ] Confirm Tables 7-8 make the 310-example human-approved dataset and labels credible.
- [ ] Confirm Table 10 and limitations honestly discuss failures.
- [ ] Confirm no smoke-test or synthetic-only result is presented as the main result.
- [ ] Confirm final risk claims are based on predicted risk, with gold risk only diagnostic.

---
**Previous:** [Overview](00_overview.md) | **Next:** [Minimum Viable Experiment](02_minimum_viable_experiment.md)
