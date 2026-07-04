#!/usr/bin/env python3

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


MISSING_VALUES = {None, "", "null", "None"}


def is_missing(value):
    """Treat None, empty strings, empty lists, and empty dicts as missing/blank."""
    if value in MISSING_VALUES:
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_values(value):
    """Used for counting values inside list fields like ambiguity_types."""
    if isinstance(value, list):
        return value
    return [value]


def print_counter(title, counter, limit=20):
    print(f"\n{title}")
    print("-" * len(title))

    if not counter:
        print("No values found.")
        return

    for value, count in counter.most_common(limit):
        print(f"{repr(value):35} {count}")


def analyze_file(path):
    data = load_json(path)

    print("\n" + "=" * 80)
    print(f"FILE: {path}")
    print("=" * 80)

    print(f"Top-level type: {type(data).__name__}")

    if isinstance(data, list):
        rows = data
        print(f"Length / number of records: {len(rows)}")
    elif isinstance(data, dict):
        rows = [data]
        print(f"Top-level keys: {len(data)}")
        print(f"Keys: {sorted(data.keys())}")
    else:
        print("Unsupported JSON structure for dataset-style stats.")
        return

    if not rows:
        print("Empty JSON.")
        return

    if not all(isinstance(row, dict) for row in rows):
        print("Not all records are objects/dicts.")
        return

    all_keys = sorted(set().union(*(row.keys() for row in rows)))
    print(f"Total unique fields: {len(all_keys)}")
    print(f"Fields: {', '.join(all_keys)}")

    # Field completeness
    print("\nFIELD COMPLETENESS")
    print("------------------")
    for key in all_keys:
        present = sum(1 for row in rows if key in row)
        missing_or_blank = sum(1 for row in rows if key not in row or is_missing(row.get(key)))
        filled = len(rows) - missing_or_blank
        print(f"{key:35} present={present:3}  filled={filled:3}  blank/missing={missing_or_blank:3}")

    # Useful categorical distributions
    useful_fields = [
        "split",
        "source_dataset",
        "ambiguity_present",
        "primary_ambiguity_type",
        "is_compound",
        "compound_ambiguity_count",
        "risk_level",
        "risk_target",
        "capability_status",
        "gold_strategy",
        "annotator",
        "annotation_date",
    ]

    for field in useful_fields:
        if field in all_keys:
            counter = Counter(row.get(field) for row in rows)
            print_counter(f"Distribution: {field}", counter)

    # List-valued distributions
    list_fields = [
        "ambiguity_types",
        "capability_context",
        "gold_strategy_sequence",
    ]

    for field in list_fields:
        if field in all_keys:
            counter = Counter()
            empty_count = 0

            for row in rows:
                value = row.get(field)
                if is_missing(value):
                    empty_count += 1
                    continue

                for item in flatten_values(value):
                    counter[item] += 1

            print_counter(f"List item distribution: {field}", counter)
            print(f"Empty/blank {field}: {empty_count}")

    # Duplicate IDs
    if "example_id" in all_keys:
        ids = [row.get("example_id") for row in rows]
        id_counts = Counter(ids)
        duplicates = {k: v for k, v in id_counts.items() if v > 1}

        print("\nDUPLICATE example_id VALUES")
        print("---------------------------")
        if duplicates:
            for example_id, count in sorted(duplicates.items(), key=lambda x: (-x[1], str(x[0]))):
                print(f"{repr(example_id):35} {count}")
        else:
            print("No duplicate example_id values found.")

    # Command length stats
    if "command" in all_keys:
        lengths = [len(str(row.get("command", ""))) for row in rows]
        words = [len(str(row.get("command", "")).split()) for row in rows]

        print("\nCOMMAND LENGTH STATS")
        print("--------------------")
        print(f"Characters: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths) / len(lengths):.2f}")
        print(f"Words:      min={min(words)}, max={max(words)}, avg={sum(words) / len(words):.2f}")

    # Filled annotation summary
    annotation_fields = [
        "gold_intent",
        "gold_slots",
        "ambiguity_present",
        "ambiguity_types",
        "primary_ambiguity_type",
        "risk_level",
        "capability_status",
        "gold_strategy",
        "gold_clarification_question",
        "gold_reinterpretation",
        "gold_rejection_explanation",
        "gold_success_condition",
        "annotation_notes",
    ]

    print("\nANNOTATION FIELD FILLED COUNTS")
    print("------------------------------")
    for field in annotation_fields:
        if field in all_keys:
            filled = sum(1 for row in rows if not is_missing(row.get(field)))
            print(f"{field:35} {filled}/{len(rows)}")


def main():
    parser = argparse.ArgumentParser(description="Print useful statistics for JSON annotation files.")
    parser.add_argument("json_files", nargs="+", help="One or more JSON files to analyze")
    args = parser.parse_args()

    for json_file in args.json_files:
        path = Path(json_file)
        if not path.exists():
            print(f"\nERROR: File not found: {path}")
            continue

        try:
            analyze_file(path)
        except json.JSONDecodeError as e:
            print(f"\nERROR: Invalid JSON in {path}: {e}")
        except Exception as e:
            print(f"\nERROR while analyzing {path}: {e}")


if __name__ == "__main__":
    main()