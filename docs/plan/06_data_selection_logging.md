---
title: "Data Selection Logging"
section: 6
description: "Filtering log format, exclusion reasons, summary script, and Table 7 structure."
---

## 6. Data Selection Logging

> [!IMPORTANT]
> Every mapper must log which examples it includes, which it excludes, and why. The examiner should be able to trace raw source material to the final 310 unique human-approved examples.

The final dataset target is 310 unique human-labelled examples split into `dev_100=100`, optional/development `train=60`, and `test=150`. `dev_20` is a subset of `dev_100` and must not be counted as additional data.

### 6.1 Filtering Log Format

Each mapper writes records to `data/interim/filtering_log.jsonl`:

```json
{
  "source_dataset": "ambik",
  "source_id": "ambik_raw_042",
  "decision": "included_candidate",
  "reason": "Meets schema requirements; has routing-relevant ambiguity signal",
  "mapper_stage": "ambik_mapper",
  "human_approval_status": "pending",
  "provenance": "Original command and metadata retained"
}
```

```json
{
  "source_dataset": "ambik",
  "source_id": "ambik_raw_107",
  "decision": "excluded",
  "reason": "Missing command text; cannot map to shared schema",
  "mapper_stage": "ambik_mapper",
  "human_approval_status": "not_applicable",
  "provenance": "Raw record inspected"
}
```

Use these final decision values:

- `included_candidate` - selected by mapper but not yet human-approved.
- `included_human_approved` - reviewed and accepted for one of the 310 examples.
- `excluded` - rejected before final dataset inclusion.
- `duplicate` - excluded because it duplicates or near-duplicates another example.
- `deferred` - held for possible replacement, not counted in the 310.

Common exclusion reasons:

- Missing command text.
- Duplicate or near-duplicate of an already included example.
- Cannot reliably assign ambiguity labels from source metadata and human review cannot resolve it.
- Outside the scope of routing evaluation, such as perception-only tasks.
- Language not English.
- Insufficient dialogue context, especially for TEACh.
- Unsafe or private content that should not be included.

### 6.2 Summary Script and Output

| Script | Output |
|--------|--------|
| `scripts/summarise_data_selection.py` | `results/tables/data_selection_summary.csv` for Table 7 |

Table 7 structure:

| Source | Raw Loaded | Excluded | Included Human-Approved | Final Split Counts | Top Exclusion Reason |
|--------|------------|----------|-------------------------|--------------------|----------------------|
| manual | TBD | TBD | TBD | dev/train/test counts | TBD |
| ambik | TBD | TBD | TBD | dev/train/test counts | TBD |
| sagc | TBD | TBD | TBD | dev/train/test counts | TBD |
| indirect_requests | TBD | TBD | TBD | dev/train/test counts | TBD |
| safe_agent_bench | TBD | TBD | TBD | dev/train/test counts | TBD |
| teach | small count required | TBD | TBD | dev/train/test counts | Insufficient usable dialogue context |
| **Total** | TBD | TBD | **310** | `dev_100=100`, `train=60`, `test=150` | |

Do not hand-write final counts. Generate them from logs and final JSONL files.

### 6.3 Provenance Requirements

For every included human-approved example, the log or metadata must identify:

- Source dataset and source ID, if applicable.
- Whether the command text is original, lightly cleaned, translated, or manually written.
- What context fields were retained or constructed.
- Which human approved the labels.
- Why the example belongs in the selected split.
- Whether it is part of the `dev_20` smoke subset.

## Coding LLM Checklist

- [ ] Make every mapper write one filtering-log record per raw item inspected.
- [ ] Distinguish mapper-selected candidates from human-approved inclusions.
- [ ] Generate Table 7 from logs and final JSONL files, not manual counts.
- [ ] Ensure `dev_20` is marked as a subset flag or derived file and excluded from total-count arithmetic.
- [ ] Include provenance fields for source ID, transformation status, approval status, and final split.

## Human Checklist

- [ ] Review filtering-log reasons for excluded and included examples.
- [ ] Confirm that the final included count is exactly 310 unique human-approved examples.
- [ ] Verify that TEACh has a small but real included count because the proposal promised it.
- [ ] Check that no source dataset dominates the final test split without justification.
- [ ] Approve provenance notes for mapped, cleaned, or manually drafted examples.

---

**<- Previous:** [Inter-Annotator Agreement Protocol](05_iaa_protocol.md) | **Next ->** [Dataset Construction Plan](07_dataset_construction.md)
