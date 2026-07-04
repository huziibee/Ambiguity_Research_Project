---
title: "Implementation Plan - Overview & Navigation"
section: 0
description: "Project scope, execution priorities, and table of contents linking to all plan sections."
---

# Risk-Aware Ambiguity Manager - Dataset Standardization & Build Plan

> **Project**: A Risk-Aware Ambiguity Manager for Compound Ambiguous Robot Commands
> **Student**: Mohammed Bangie, 2610990
> **Supervisors**: Steven James & Benjamin Rosman
> **Scope**: NLU coordination/routing layer, not physical robotics
> **Primary research question**: Does a type-and-risk-aware ambiguity manager improve routing decisions for compound ambiguous robot commands compared to direct LLM interpretation and uniform or threshold-based baselines?

---

## How to Read This Plan

This plan is organised results-first. The primary goal is to produce defensible final evaluation results on a frozen human-approved test set, then build outward to ablations, statistical tests, failure analysis, and optional extensions.

The core contribution is the type-and-risk-aware routing policy. Parsing, ambiguity classification, risk prediction, dataset construction, and tooling are infrastructure for evaluating whether that routing policy works.

The primary experiment must use **Gemini 3.1 Flash-Lite on the free tier first**. HPC is not part of the core method. HPC is only a fallback or accelerator if Gemini throttles, local execution becomes impractical, or later optional larger runs are explicitly approved. Supervised fine-tuning is not core to the project unless a later document explicitly marks it as optional or fallback.

Gold labels are human-approved labels. Final evaluation uses each system's **predicted risk**. Gold risk is retained for annotation, diagnostics, error analysis, and optional ablations only.

### Binding Dataset Target

The dataset target for the main study is **400 unique human-labelled examples**:

| Split | Size | Role |
|-------|------|------|
| `dev_80` | 100 | Development, tuning, prompt iteration, and ablation debugging |
| `train` | 60 | Optional development/training split only; not required for the primary Gemini experiment |
| `test` | 150 | Frozen final evaluation split |
| `dev_20` | 20 | Smoke-test subset of `dev_80`; never reported as final evidence |

`dev_20` must be a subset of `dev_80`, not an additional split. The 400-example total is counted as `dev_80 + train + test`, with `dev_20` included inside `dev_80`.

TEACh remains included at a small count because the proposal promised it. It should be represented enough to support methodology alignment, but it must not dominate the dataset or delay the main experiment.

### Priority Classification

| Priority | Meaning | Examples |
|----------|---------|----------|
| **MUST** | Project fails without it | Shared schema, 400 human-approved examples, `dev_80`, `test`, `dev_20` smoke subset, baselines, Gemini 3.1 Flash-Lite primary run, proposed router, predicted-risk final evaluation, Table 1, data selection log, failure analysis |
| **SHOULD** | Strengthens the report significantly | Inter-annotator agreement, ablations, statistical tests, bootstrap CIs, risk and ambiguity breakdowns, TEACh small-count inclusion |
| **COULD** | Useful if time permits | HPC acceleration, larger optional runs, safety API integration, SFT/local LLM experiments, rule-only manager ablation |

### Non-Core Unless Explicitly Marked Optional

- No SFT or local-HPC model training is part of the primary experiment.
- No gold-risk final evaluation is allowed as the main result.
- No `dev_20` numbers should be presented as final findings.
- No synthetic expansion replaces human-labelled examples.

---

## Table of Contents

1. [Target Outputs](01_target_outputs.md)
2. [Minimum Viable Experiment](02_minimum_viable_experiment.md)
3. [Data and Schema Plan](03_data_schema.md)
4. [Gold Label Protocol](04_gold_label_protocol.md)
5. [Inter-Annotator Agreement Protocol](05_iaa_protocol.md)
6. [Data Selection Logging](06_data_selection_logging.md)
7. [Dataset Construction Plan](07_dataset_construction.md)
8. [Systems Under Comparison](08_systems_under_comparison.md)
9. [Proposed Router - Core Contribution](09_proposed_router.md)
10. [Ablation Studies](10_ablation_studies.md)
11. [Statistical Significance Testing](11_statistical_testing.md)
12. [Failure Analysis](12_failure_analysis.md)
13. [Safety API Integration - Optional](13_safety_api.md)
14. [HPC Execution Plan - Fallback/Optional](14_hpc_execution.md)
15. [Local LLM/SFT Guidance - Optional](15_sft_guidance.md)
16. [Tools: Required, Recommended, and Rejected](16_tools.md)
17. [Repository Structure](17_repository_structure.md)
18. [Reproducibility and Code Visibility](18_reproducibility.md)
19. [Quality Gates](19_quality_gates.md)
20. [Timeline](20_timeline.md)
21. [Report Alignment](21_report_alignment.md)
22. [Risks and Mitigations](22_risks_mitigations.md)

## Coding LLM Checklist

- [ ] Keep all implementation plans consistent with Gemini 3.1 Flash-Lite free-tier as the primary experiment backend.
- [ ] Treat HPC, SFT, local LLMs, synthetic expansion, and safety API calls as fallback or optional unless a later task explicitly changes scope.
- [ ] Implement split logic so `dev_20` is sampled from `dev_80`, not counted as extra data.
- [ ] Ensure final evaluation scripts use predicted risk by default and reserve gold risk for diagnostics or named ablations.
- [ ] Preserve TEACh as a small-count included source in dataset planning and reports.

## Human Checklist

- [ ] Confirm that the 400-example target is feasible with available human annotation time.
- [ ] Approve the final dataset split sizes before any test-set freeze.
- [ ] Verify that every gold label used in final evaluation has been human-approved.
- [ ] Check that reported final results are from the frozen `test` split, not `dev_20` or `dev_80`.
- [ ] Confirm that TEACh inclusion satisfies the proposal promise without displacing higher-value examples.

---

**Next ->** [Target Outputs](01_target_outputs.md)
