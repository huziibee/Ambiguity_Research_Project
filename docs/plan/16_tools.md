---
title: "Tools"
section: 16
description: "Required, recommended, and rejected tools for a reproducible Gemini-first experiment."
---

## 16. Tools

Use the smallest toolset that makes the experiment reproducible.

## Required

| Tool | Purpose |
|------|---------|
| Python 3.11+ | project language |
| Pydantic v2 | schema validation and JSON schema export |
| JSONL | datasets and predictions |
| pandas | result tables |
| numpy | bootstrap sampling |
| scipy | McNemar/statistical tests |
| scikit-learn | F1, kappa, confusion matrices |
| pytest | focused checks |
| PyYAML or omegaconf | configs |
| Gemini API client or LiteLLM | Gemini 3.1 Flash-Lite calls |
| tenacity | retry/backoff |

## Recommended

| Tool | Purpose |
|------|---------|
| httpx | optional safety API |
| matplotlib/seaborn | figures |
| ruff | lint/format |

## Rejected Unless Strongly Justified

| Tool | Why |
|------|-----|
| LangChain | unnecessary abstraction for fixed prompts and schemas |
| n8n | not reproducible experimental control |
| agent frameworks | project is a fixed pipeline, not autonomous multi-agent execution |
| MLflow/W&B | file-based results are enough |
| Docker | overhead for honours unless environment drift becomes a blocker |

## Coding LLM Checklist

- [ ] Prefer existing dependencies and standard library before adding tools.
- [ ] Keep Gemini calls direct, schema-validated, cached, and logged.
- [ ] Keep optional HPC/local-LLM dependencies out of the primary install if possible.
- [ ] Add dependency changes to `requirements.txt` or `pyproject.toml`.
- [ ] Avoid adding rejected tools unless the plan is updated with a concrete reason.

## Human Checklist

- [ ] Confirm every dependency is actually needed.
- [ ] Confirm no secret keys are committed.
- [ ] Confirm Gemini API usage follows free-tier privacy constraints.
- [ ] Confirm optional HPC/local-LLM tools are not required for reproducing primary tables.
- [ ] Confirm setup instructions match the final toolset.

---
**Previous:** [Local LLM and SFT Fallback Guidance](15_sft_guidance.md) | **Next:** [Repository Structure](17_repository_structure.md)
