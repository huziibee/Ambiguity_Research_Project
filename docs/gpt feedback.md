 Spawned four subagents and reconciled their memos with the repo state. I also verified the current project skeleton locally.

  Verified Locally

  - python scripts/run_evaluation.py succeeds on dev_20.
  - python -m compileall src scripts succeeds.
  - python scripts/verify_standardization.py succeeds across standardized datasets.
  - Current dev_20 Table 1 is only a smoke test: proposed manager scores 0.95 routing accuracy on n=20, but it uses gold risk and heuristic logic, so it must not be treated as final evidence.

  Hard Corrections

  1. The core experiment must be reframed around Gemini 3.1 Flash-Lite prompt-plus-policy evaluation, not SFT/HPC.
  2. Main evaluation must use predicted risk, not gold risk. Current risk-aware-ambiguity-manager/src/schema.py does not allow risk_mode="predicted", and current risk-aware-ambiguity-manager/src/evaluation/runner.py
     injects risk_mode="gold".

  3. Gold labels must be human-created or human-approved. Gemini cannot be the final label authority.
  4. Final routing accuracy must be strict: predicted_strategy == gold_strategy. Do not count multi_step as correct just because it contains the gold strategy.
  5. dev_20 is pipeline validation only. The research question needs a frozen held-out test set.

  Gemini Constraints
  Official docs currently list gemini-3.1-flash-lite as stable and optimized for high-volume/simple processing. Free-tier standard input/output is free, but context caching and Search/Maps grounding are not available
  for Flash-Lite free tier. Rate limits are per project across RPM/TPM/RPD, actual capacity can vary, and active limits must be checked in AI Studio. Gemini structured outputs support JSON Schema/Pydantic. Unpaid usage
  may be used to improve Google products and may be reviewed by humans, so do not send sensitive/confidential/personal data.

  Sources: models (https://ai.google.dev/gemini-api/docs/models), pricing (https://ai.google.dev/gemini-api/docs/pricing), rate limits (https://ai.google.dev/gemini-api/docs/rate-limits), structured outputs
  (https://ai.google.dev/gemini-api/docs/structured-output), terms (https://ai.google.dev/gemini-api/terms).

  Final Research Story
  The report should not be “Gemini is good at robot commands.” The story is:

  A fixed LLM backbone provides structured interpretation signals. The contribution is the explicit type-and-risk-aware routing policy that coordinates ambiguity type, risk, and capability to choose between execute,
  clarify, silently_resolve, face_preserving_rejection, and multi_step.

  The final answer to the research question comes from whether that routing policy beats direct Gemini and simpler baselines, especially on compound and high-risk cases.

  Recommended Dataset Plan
  Use 310 unique human-labelled examples.

   Source              Count    Purpose
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Manual compound        50    Core compound ambiguity coverage
  ──────────────────  ───────  ───────────────────────────────────────
   AmbiK                  80    Ambiguity-focused robot/kitchen tasks
  ──────────────────  ───────  ───────────────────────────────────────
   SaGC/CLARA             70    Clear/ambiguous/infeasible routing
  ──────────────────  ───────  ───────────────────────────────────────
   IndirectRequests       50    Pragmatic/ISA coverage
  ──────────────────  ───────  ───────────────────────────────────────
   SafeAgentBench         30    Safety/rejection stress test
  ──────────────────  ───────  ───────────────────────────────────────
   TEACh                  30    Multi-turn embodied dialogue evidence

  Split:

   Split      Count    Use
  ━━━━━━━━━  ━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   dev_20        20    Smoke testing only
  ─────────  ───────  ────────────────────────────────────────────
   dev_100      100    Prompt/router tuning only
  ─────────  ───────  ────────────────────────────────────────────
   train         60    Optional training/few-shot/dev experiments
  ─────────  ───────  ────────────────────────────────────────────
   test         150    Frozen final evaluation

  Phase Plan
  Phase 0: Scope Lock

  - Rewrite plan around Gemini 3.1 Flash-Lite structured extraction plus deterministic router.
  - Remove SFT/HPC as core unless actually used.
  - Freeze primary metric: routing correctness.
  - Human gate: approve RQ, scope, model ID, and call budget.

  Phase 1: Fix Current MVE

  - Add risk_mode="predicted" to schema.
  - Stop final runner from injecting gold risk.
  - Make dev_20 clearly labelled as smoke-test output.
  - Ensure every prediction row records model, prompt hash, temperature, retry count, cache status.
  - Gate: dev_20 runs with valid outputs, but no final claims made from it.

  Phase 2: Annotation Foundation

  - Create docs/annotation_guidelines.md.
  - Create docs/dataset_mapping_rules.md.
  - Enforce annotation notes for compound, medium/high/critical risk, and rejection cases.
  - Human gate: annotation rules are frozen before large annotation.

  Phase 3: Dataset Construction

  - Produce data/manual/compound_50.jsonl.
  - Produce data/interim/*_mapped.jsonl.
  - Produce data/interim/filtering_log.jsonl.
  - Generate dev_100, train, test.
  - Freeze test.jsonl with manifest.json.
  - Human gate: no test edits after freeze; corrections go to errata.md.

  Phase 4: IAA And Human Validation

  - Double-annotate 30 test examples.
  - Compute Cohen’s kappa for primary_ambiguity_type, risk_level, gold_strategy.
  - Compute Jaccard agreement for multi-label ambiguity_types.
  - Target: kappa >= 0.75.
  - Human gate: if below target, revise guidelines and re-annotate.

  Phase 5: Gemini System Design
  Use a call-efficient design:

  - Always clarify: 0 Gemini calls.
  - Always resolve: 0 Gemini calls.
  - Shared Gemini extractor: 1 call/example.
  - Proposed manager: deterministic policy over extractor output.
  - Degree baseline: use scalar ambiguity degree, no type semantics.
  - Direct Gemini baseline: 1 separate call/example.
  - Ablations: 0 extra calls, reuse cached extractor outputs.

  For test=150, expect roughly 300 core Gemini calls plus retries.

  Phase 6: Final Evaluation
  Required tables:

  - Table 1: all systems on frozen test.
  - Table 2: ablations.
  - Table 3: compound vs non-compound.
  - Table 4: risk-level breakdown.
  - Table 5: ambiguity-type breakdown.
  - Table 6: strategy confusion matrix.
  - Table 7: data selection summary.
  - Table 8: IAA.
  - Table 9: McNemar + bootstrap CIs.
  - Table 10: failure analysis.

  Required metrics:

  - routing_accuracy
  - compound_routing_accuracy
  - high_risk_routing_accuracy
  - clarification_precision/recall/f1
  - unsafe_silent_resolution_rate
  - safe_rejection_rate
  - ambiguity_micro_f1, ambiguity_macro_f1
  - compound_detection_f1
  - risk_macro_f1, high/critical recall
  - slot_micro_f1
  - multistep_sequence_exact_match

  Phase 7: Failure Analysis
  Separate errors into:

  - Schema/API failures
  - Intent/slot failures
  - Ambiguity classification failures
  - Risk failures
  - Capability failures
  - Context/history failures
  - Routing-policy failures
  - Output-quality failures
  - Data/gold-label issues

  Human gate: representative failures must be selected and interpreted by a human, not auto-written by Gemini.

  Non-Negotiables Enforcement

   Requirement                                     Enforcement
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Enough empirical results answer the question    Frozen test, all systems, ablations, subgroup tables, McNemar, bootstrap CIs
  ──────────────────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Author shows clear understanding                Confusion matrix, layered failure analysis, human-written interpretation
  ──────────────────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Results relate to RQ/aim                        Routing accuracy is headline; compound/risk/type breakdowns are central
  ──────────────────────────────────────────────  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Limitations discussed                           Text-only routing, label subjectivity, hybrid dataset, manual compounds, Gemini volatility, no embodied/user study

  Immediate Next Work

  1. Patch schema/runner to support risk_mode="predicted" and prevent gold-risk leakage.
  2. Create annotation and dataset mapping docs from the plan.
  3. Build validation/IAA/split scripts.
  4. Freeze the 310-example dataset plan before adding more system complexity.