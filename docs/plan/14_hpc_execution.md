---
title: "HPC Execution Plan"
section: 14
description: "HPC fallback, acceleration, and optional local-LLM execution."
---

## 14. HPC Execution Plan

HPC is a fallback and accelerator, not a primary dependency. The Gemini-first experiment must remain reproducible from cached local files.

Use HPC for:

- batch inference if Gemini throttles or a local model fallback is approved
- bootstrap/statistical jobs if local runtime is slow
- optional local LLM/SFT extension after primary results are stable

Do not claim HPC/local-LLM/SFT results unless predictions, configs, and logs are saved.

## Job Types

| Job | Partition | Use |
|-----|-----------|-----|
| cached metrics/statistics | CPU batch | recompute tables and CIs |
| final batch inference | GPU if local LLM used | fallback only |
| ablations | CPU/GPU depending on implementation | usually from cached outputs |
| optional LoRA/SFT | GPU | extension only |

## Local Development Guarantee

This must always work without HPC:

```powershell
python scripts/run_evaluation.py --config configs/dev_20.yaml
python scripts/run_evaluation.py --config configs/final_eval.yaml --use-cached-predictions
```

## Coding LLM Checklist

- [ ] Keep local `dev_20` and cached-prediction evaluation runnable without HPC.
- [ ] Write HPC scripts only for final batch inference, bootstrap/statistics, or optional local-LLM fallback.
- [ ] Save SLURM stdout/stderr logs for any HPC result reported.
- [ ] Ensure HPC-generated predictions use the same `ManagerOutput` schema and metrics.
- [ ] Do not mix Gemini and HPC/local-LLM results in the same primary table unless clearly labelled.

## Human Checklist

- [ ] Confirm actual HPC partition names and queue limits before relying on jobs.
- [ ] Confirm any HPC/SFT result in the report has matching cached prediction files.
- [ ] Confirm Gemini throttling or experiment scale justifies HPC use.
- [ ] Review HPC job logs for failures before accepting generated predictions.
- [ ] Ensure the report does not imply HPC/local-LLM work happened unless it did.

---
**Previous:** [Safety API Integration](13_safety_api.md) | **Next:** [Local LLM and SFT Fallback Guidance](15_sft_guidance.md)
