---
title: "Repository Structure"
section: 17
description: "Required source, data, config, and result layout."
---

## 17. Repository Structure

The repository must make the experiment inspectable without rerunning Gemini.

```text
risk-aware-ambiguity-manager/
  README.md
  pyproject.toml
  requirements.txt
  .env.example
  configs/
    dev_20.yaml
    dev_80.yaml
    final_eval.yaml
    ablation.yaml
    local_llm.yaml
  data/
    raw/<dataset>/
    interim/*_mapped.jsonl
    interim/filtering_log.jsonl
    manual/compound_50.jsonl
    processed/dev_20.json
    processed/dev_80.json
    processed/train.json
    processed/test.json
    processed/manifest.json
    processed/errata.md
    annotation/annotator_a.jsonl
    annotation/annotator_b.jsonl
  docs/
    annotation_guidelines.md
    ambiguity_taxonomy.md
    routing_strategy_definitions.md
    dataset_mapping_rules.md
    safety_api_contract.md
    plan/*.md
  schemas/
    example_schema.json
    manager_input.json
    manager_output.json
  src/
    schema.py
    config.py
    llm_client.py
    baselines/
    manager/
    ablations/
    data/
    evaluation/
  scripts/
    run_evaluation.py
    validate_dataset.py
    compute_iaa.py
    summarise_data_selection.py
    significance_tests.py
    bootstrap_ci.py
    generate_tables.py
    generate_figures.py
    smoke_test.py
  jobs/
  results/
    predictions/*.json
    metrics/*.json
    tables/*.csv
    figures/*.png
    statistics/*.json
    annotation/*.json
    failure_cases/*.json
  cache/
    llm_responses/
```

TEACh is included because the proposal names it. Local LLM/HPC files are allowed but must be clearly optional.

## Coding LLM Checklist

- [ ] Keep generated predictions, metrics, tables, figures, and statistics under `results/`.
- [ ] Keep raw Gemini response cache under `cache/llm_responses/` or equivalent.
- [ ] Add missing scripts only when required by a plan doc.
- [ ] Keep optional HPC/SFT files separate from primary Gemini configs.
- [ ] Ensure all paths are project-relative, not machine-specific.

## Human Checklist

- [ ] Confirm data provenance and license notes exist under `data/raw/`.
- [ ] Confirm `test.json` and `manifest.json` are present before final evaluation.
- [ ] Confirm cached predictions correspond to the frozen manifest.
- [ ] Confirm optional outputs are clearly labelled.
- [ ] Confirm repository structure is clean before submission.

---
**Previous:** [Tools](16_tools.md) | **Next:** [Reproducibility and Code Visibility](18_reproducibility.md)
