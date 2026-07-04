---
title: "Risks and Mitigations"
section: 22
description: "Project risks, mitigations, and human review obligations."
---

## 22. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Dataset too messy | Medium | Start with manual/dev examples, time-box mappers, document exclusions |
| Annotation inconsistency | Medium | Binding guidelines, IAA, adjudication, human review |
| Gold-risk leakage | High | final config guard, prompt audit, diagnostic-only gold mode |
| Gemini throttling | Medium | caching, throttling, resumable runs, HPC fallback |
| Gemini privacy constraints | Medium | no sensitive/private data in free-tier calls |
| Direct baseline fallback | High | forbid heuristic fallback in final direct Gemini |
| Degree baseline too weak | Medium | pre-declare scalar method and audit fairness |
| Results not significant | Medium | report honestly, use subgroup/failure analysis |
| TEACh time sink | Medium | keep small required sample: 30 total, 15 test |
| Overengineering | Medium | no LangChain/agents/MLflow unless plan changes |
| HPC unavailable | Low/Medium | primary Gemini path and cached reproduction remain local |
| SFT overclaim | High | report SFT only if actually run and cached |

## Open Questions to Resolve

- Who is the second human annotator?
- What are the active Gemini free-tier limits in AI Studio on the final run date?
- Are HPC partition names and queue limits confirmed?
- Is the external safety API available, or should it remain out of scope?
- Is the 400-example target feasible, or is the documented fallback needed?

## Coding LLM Checklist

- [ ] Implement mitigations as checks, logs, or scripts wherever possible.
- [ ] Add tests/config guards against gold-risk leakage in final runs.
- [ ] Ensure Gemini cache/resume logic prevents losing progress on throttling.
- [ ] Keep optional synthetic/HPC/SFT work out of required gates unless explicitly promoted.
- [ ] Surface failures in result artifacts instead of silently hiding them.

## Human Checklist

- [ ] Review every risk mitigation before final evaluation starts.
- [ ] Confirm Gemini free-tier privacy terms are acceptable for the data used.
- [ ] Confirm second annotator availability and IAA plan.
- [ ] Confirm HPC fallback details before relying on them.
- [ ] Ensure limitations honestly cover any unresolved risks.

---
**Previous:** [Report Alignment](21_report_alignment.md)
