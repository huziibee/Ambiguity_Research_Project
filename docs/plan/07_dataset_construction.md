---
title: "Dataset Construction Plan"
section: 7
description: "Dataset standardization, target composition, construction order, manual examples, and split strategy."
---

## 7. Dataset Construction Plan

The final dataset must contain **310 unique human-labelled examples**:

- `dev_100`: 100 examples for development, prompt iteration, and tuning.
- `train`: 60 examples for optional development/training experiments only.
- `test`: 150 frozen examples for final evaluation.
- `dev_20`: 20-example smoke-test subset of `dev_100`; not counted separately.

Quality and label reliability matter more than maximizing size. Every final example must be human-approved.

The primary experiment uses Gemini 3.1 Flash-Lite free-tier first. Dataset construction should not assume SFT, HPC, or local model training as core requirements. HPC may accelerate later optional runs or help if Gemini throttles; it does not define the dataset.

### 7.1 Dataset Installation and Standardization Phase

Standardize all target source datasets into a uniform CSV schema before mapping into JSONL.

#### Target Datasets to Standardize

1. **AmbiK** - ambiguity classification and ambiguity-type coverage.
2. **CLARA-Dataset / SaGC** - clear, ambiguous, and infeasible routing cases.
3. **SafeAgentBench** - safety and rejection stress cases.
4. **IndirectRequests** - indirect speech acts and pragmatic ambiguity.
5. **TEACh** - multi-turn embodied dialogue; included at small count because the proposal promised it.

#### Standardized CSV Schema Columns

Every dataset should have a standardized `<dataset>_standardized.csv` file with:

- `source_id`: unique identifier in the original dataset.
- `command`: primary natural-language command or user instruction.
- `scene_context`: scene details such as objects, location, floorplan, or task context.
- `dialogue_history`: JSON array of previous dialogue turns, empty if not applicable.
- `capability_context`: robot capability or task-domain information.
- `gold_intent`: mapped or human-approved intent.
- `ambiguity_types`: JSON list of ambiguity types present.
- `risk_level`: human-approved gold risk label.
- `gold_strategy`: mapped and human-approved routing strategy.
- `original_split`: split from the original dataset, if any.
- `metadata`: serialized JSON for useful raw fields and provenance.

#### Cleanup and Context Retention

- Preserve dataset README, license, citation, and source-link information.
- Do not commit unnecessary raw archives, images, point clouds, or large binary files.
- Keep enough raw metadata to audit provenance and label decisions.
- Write a README inside each dataset folder explaining project use, original dataset goal, source, and any cleaning performed.

#### Automated Verification

`scripts/verify_standardization.py` should check that standardized CSV files exist and conform to the expected columns. It should not decide gold labels; it only verifies structure.

### 7.2 Target Dataset Composition

The exact source counts can move during selection, but the final total and split sizes are fixed. TEACh must remain included at a small count.

| Source | Target Count | Priority | Role in Evaluation |
|--------|--------------|----------|--------------------|
| Manual compound examples | 50-70 | MUST | Ensures compound ambiguity coverage |
| AmbiK | 60-80 | MUST | Ambiguity-focused coverage |
| SaGC | 50-70 | MUST | Clear, ambiguous, and infeasible routing labels |
| IndirectRequests | 30-50 | MUST | Pragmatic and indirect request coverage |
| SafeAgentBench | 20-35 | SHOULD | Safety and rejection stress testing |
| TEACh | 10-20 | MUST at small count | Multi-turn embodied dialogue promised in proposal |

The final included count across all sources must be exactly 310. If source availability forces changes, preserve split sizes and document the rationale in the data selection log.

### 7.3 Construction Order

| Step | What | Definition of Done |
|------|------|--------------------|
| 1 | Standardize source CSVs | `verify_standardization.py` passes |
| 2 | Draft/select candidate examples | Candidate pool exceeds 310 and has provenance logs |
| 3 | Build `dev_100` candidates | 100 examples cover all major strategy and risk paths |
| 4 | Derive `dev_20` | 20 smoke examples sampled from `dev_100` |
| 5 | Build optional `train` | 60 examples for optional development/training only |
| 6 | Build candidate `test` | 150 examples held out from tuning |
| 7 | Human approval pass | All 310 examples approved for labels, risk, strategy, and provenance |
| 8 | IAA double annotation | 30 examples double-labelled; target kappa >= 0.75 |
| 9 | Resolve disagreements | Final human-approved labels documented |
| 10 | Freeze final splits | `manifest.json` written; `test.jsonl` read-only by policy |
| 11 | Run primary experiment | Gemini 3.1 Flash-Lite free-tier first, predicted-risk mode |

Do not add synthetic test expansion to the core dataset. If synthetic rewrites are explored later, label them optional and keep them separate from the 310 human-labelled examples.

### 7.4 Manual Compound Ambiguity Construction

Manual examples should target compound ambiguity combinations that are under-represented in source datasets.

| Combination | Target Count | Example Template |
|-------------|--------------|------------------|
| pragmatic + referential | 10-15 | "Can you pass that thing?" |
| pragmatic + temporal | 5-10 | "Could you do it soon?" |
| referential + temporal | 10-15 | "Move that there in a bit" |
| referential + quantitative | 5-10 | "Get some of those things" |
| pragmatic + referential + temporal | 10-15 | "Can you move that thing over there in a few minutes?" |
| referential + temporal + quantitative | 5-10 | "Get a few of those things ready in about ten minutes" |
| 3-4 type combinations | 5-10 | "Would you bring some of those over there in a while?" |

Vary `risk_level` across manual examples. Include low-risk silently resolvable cases, medium-risk clarification cases, and high/critical rejection or safety-sensitive cases.

Manual examples still require human approval and provenance notes. They are not valid merely because they were written by the project author.

### 7.5 Split Strategy

| Split | Size | Purpose | Used By |
|-------|------|---------|---------|
| `dev_100` | 100 | Development evaluation, prompt tuning, debugging, and ablation iteration | Development only |
| `dev_20` | 20 subset of `dev_100` | Fast smoke testing | Development only |
| `train` | 60 | Optional development/training experiments; not required for primary Gemini run | Optional only |
| `test` | 150 | Frozen held-out final evaluation | Final results only |

Splitting rules:

- Stratify by `source_dataset`, `is_compound`, `risk_level`, `gold_strategy`, and major ambiguity type.
- Keep near-duplicates in the same split or exclude them.
- Keep `test` hidden from prompt iteration and system tuning.
- Reserve enough compound and high-risk cases in `test` to support final breakdowns.
- Include TEACh examples across development/test only if labels and context are strong enough; otherwise keep the count small but documented.
- If using the optional `train` split, do not make SFT a core requirement. Treat it as optional development or later extension.

### 7.6 Final Evaluation Implications

The final `test` evaluation must:

- Use predicted risk for all primary systems.
- Score predicted strategy against human-approved `gold_strategy`.
- Use gold risk only to analyse where risk prediction helped or failed.
- Run Gemini 3.1 Flash-Lite free-tier first.
- Log any Gemini quota or throttling event that triggers a fallback or delayed run.

## Coding LLM Checklist

- [ ] Build final split generation around exactly 310 unique examples: `dev_100=100`, `train=60`, and `test=150`.
- [ ] Generate `dev_20` as a deterministic subset of `dev_100`.
- [ ] Keep TEACh in the source plan with a small documented count.
- [ ] Exclude synthetic rewrites from the core human-labelled dataset.
- [ ] Make split scripts stratify by source, compound status, risk, strategy, and ambiguity type.
- [ ] Default final run configs to Gemini 3.1 Flash-Lite free-tier with predicted-risk mode.

## Human Checklist

- [ ] Approve the final source-count mix before freezing splits.
- [ ] Verify every included example has human-approved labels and provenance.
- [ ] Check that `dev_20` examples are a subset of `dev_100`.
- [ ] Confirm that `test` contains enough compound and high-risk cases for meaningful analysis.
- [ ] Review TEACh examples manually for sufficient dialogue context and proposal alignment.
- [ ] Confirm optional `train` examples are not presented as evidence of mandatory SFT.

---

**<- Previous:** [Data Selection Logging](06_data_selection_logging.md) | **Next ->** [Systems Under Comparison](08_systems_under_comparison.md)
