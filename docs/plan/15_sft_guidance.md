---
title: "Local LLM and SFT Fallback Guidance"
section: 15
description: "Optional local LLM, vLLM, and LoRA/SFT guidance for HPC fallback or extension experiments."
---

## 15. Local LLM and SFT Fallback Guidance

The primary experiment uses Gemini 3.1 Flash-Lite structured outputs plus a deterministic router. Local LLMs and SFT are not part of the core claim unless actually run, cached, and reported as a separate extension.

## When To Use This

Use local LLM/SFT only if:

- Gemini throttling prevents completing cached final predictions, or
- supervisors approve an extension after the Gemini-first experiment is stable, or
- a robustness comparison against local open-source models is explicitly needed.

## Optional Training Strategy

If approved:

- Use a small open-source instruct model compatible with available HPC GPUs.
- Use LoRA/PEFT rather than full fine-tuning.
- Train only on `train.jsonl`.
- Never train on `dev_100` or `test`.
- Save training config, seed, checkpoint, prompt template, and predictions.

## Serving

Preferred: `vLLM` with an OpenAI-compatible endpoint. Alternative: `transformers` pipeline. Do not run long-lived servers on login nodes.

## Reporting Rule

If local LLM/SFT is used, report it as:

- fallback result, if Gemini throttled
- extension result, if added after primary experiment

Do not silently replace the Gemini-first methodology.

## Coding LLM Checklist

- [ ] Keep SFT code/config separate from primary Gemini configs.
- [ ] Do not require SFT for `dev_20`, `dev_100`, or final cached Gemini evaluation.
- [ ] If SFT is run, save training config, seed, checkpoint path, prompt format, and prediction cache.
- [ ] Ensure direct local-LLM and proposed local-LLM variants use fair matching backbones.
- [ ] Clearly label SFT outputs as fallback/extension outputs unless the whole methodology is revised.

## Human Checklist

- [ ] Approve any SFT/local-LLM run before spending HPC time.
- [ ] Confirm SFT does not replace the Gemini-first plan silently.
- [ ] Verify train/test separation before any SFT run.
- [ ] Review whether SFT results are strong enough and fair enough to include.
- [ ] Ensure the final report states exactly which model path produced each table.

---
**Previous:** [HPC Execution Plan](14_hpc_execution.md) | **Next:** [Tools](16_tools.md)
