---
title: "Quality Gates"
section: 19
description: "Mandatory gates before final evaluation and submission."
---

## 19. Quality Gates

No final claims until these gates pass.

| # | Gate | Verification |
|---|------|--------------|
| 1 | `dev_20` smoke test passes | `python scripts/smoke_test.py` |
| 2 | schema validation passes | `python scripts/validate_dataset.py data/processed/*.json` |
| 3 | `risk_mode="predicted"` supported | schema/config tests |
| 4 | no gold-risk leakage in primary run | config/unit test |
| 5 | manual compound validation complete | human sign-off |
| 6 | filtering log generated | `data/interim/filtering_log.jsonl` |
| 7 | IAA complete | `results/annotation/iaa_results.json` |
| 8 | test set frozen | `data/processed/manifest.json` |
| 9 | all systems implemented | prediction files exist |
| 10 | ablations implemented | Table 2 exists |
| 11 | McNemar and CIs computed | statistics JSON exists |
| 12 | failure analysis complete | Table 10 and representative cases exist |
| 13 | cached reproduction works | final eval from cache succeeds |
| 14 | report limitations drafted | human review |
| 15 | repo ready | human review |

## Code Quality

```powershell
ruff check src tests scripts
ruff format src tests scripts
pytest tests -v
python -m compileall src scripts
```

Use the available subset if a tool is not installed yet; document skipped checks.

## Coding LLM Checklist

- [ ] Implement gates as scripts/tests where possible.
- [ ] Add a guard preventing final configs from using gold risk unless labelled diagnostic.
- [ ] Ensure every generated output is schema-validated.
- [ ] Ensure failed Gemini calls are visible in logs/artifacts.
- [ ] Keep smoke-test and final-test outputs clearly separated.

## Human Checklist

- [ ] Manually verify data and risk labels before final evaluation.
- [ ] Check IAA and adjudication notes before freeze.
- [ ] Confirm all high/critical examples are reviewed.
- [ ] Confirm final tables are generated from frozen cached predictions.
- [ ] Confirm limitations cover any failed or skipped gate.

---
**Previous:** [Reproducibility and Code Visibility](18_reproducibility.md) | **Next:** [Timeline](20_timeline.md)
