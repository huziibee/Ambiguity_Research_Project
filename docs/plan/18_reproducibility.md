---
title: "Reproducibility and Code Visibility"
section: 18
description: "Cached predictions, one-command reproduction, fixed seeds, and repository visibility."
---

## 18. Reproducibility and Code Visibility

The examiner must be able to inspect results without live Gemini, HPC, or API keys.

## Required Files

| File | Contents |
|------|----------|
| `README.md` | setup, data notes, one-command reproduction |
| `requirements.txt` or `pyproject.toml` | pinned dependencies |
| `.env.example` | environment variable template |
| `configs/final_eval.yaml` | exact final evaluation config |
| `data/processed/manifest.json` | frozen split metadata and hashes |

## Cached Inference

All final predictions must be saved in `results/predictions/`. Each LLM-backed prediction should include:

- model ID
- provider/path: Gemini, HPC fallback, or local extension
- prompt hash
- schema version
- temperature
- retry count
- cache key
- raw response
- parsed output
- fallback status

## One-Command Reproduction

```powershell
python scripts/run_evaluation.py --config configs/final_eval.yaml --use-cached-predictions
```

This must regenerate final metrics and tables from cached predictions without live API calls.

## Coding LLM Checklist

- [ ] Save raw and parsed predictions for every system.
- [ ] Save model ID, prompt hash, temperature, retry count, cache key, schema version, and timestamp.
- [ ] Make table/stat generation work from cached predictions with no live API calls.
- [ ] Hash frozen datasets and include hashes in `manifest.json`.
- [ ] Ensure rerunning evaluation from cache reproduces existing CSV tables exactly.

## Human Checklist

- [ ] Run the one-command cached reproduction before submission.
- [ ] Verify cached predictions correspond to the frozen `test.jsonl` hash.
- [ ] Confirm API keys are not committed.
- [ ] Confirm repo access is public or granted to supervisors/examiner.
- [ ] Confirm the AI declaration matches actual Gemini/Codex usage.

---
**Previous:** [Repository Structure](17_repository_structure.md) | **Next:** [Quality Gates](19_quality_gates.md)
