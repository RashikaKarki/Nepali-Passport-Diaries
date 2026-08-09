#!/usr/bin/env python3
"""Turns a parsed entry-submission issue into a _data/ edit for the bot PR."""

import os
import sys
from pathlib import Path

import yaml

from validate_data import DATA_DIR, validate_entry

NO_RESPONSE = "_No response_"

CATEGORY_FILES = {
    "Visa-free": ("visa_free.yml", "visa_free"),
    "Visa on arrival": ("visa_on_arrival.yml", "visa_on_arrival"),
    "eVisa": ("evisa.yml", "evisa"),
    "Special case (extra access with another country's visa)": ("special_cases.yml", "special"),
}

FIELD_ORDER = (
    "country", "iso", "region", "status", "requires", "benefit", "held_visas",
    "duration", "fee", "conditions", "extension", "notes", "source", "verified",
)


def parse_issue(body):
    sections = {}
    current = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    fields = {k: "\n".join(v).strip() for k, v in sections.items()}
    return {k: (None if v in ("", NO_RESPONSE) else v) for k, v in fields.items()}


def _checked(value):
    if not value:
        return []
    return [line[6:].strip() for line in value.splitlines() if line.lower().startswith("- [x]")]


def build_entry(fields):
    filename, status = CATEGORY_FILES[fields["Category"]]
    raw = {
        "country": fields.get("Country"),
        "iso": (fields.get("ISO code") or "").upper() or None,
        "region": fields.get("Region"),
        "status": status,
        "requires": fields.get("Requires (special cases only)"),
        "benefit": fields.get("Benefit (special cases only)"),
        "held_visas": _checked(fields.get("Held visas (special cases only)")) or None,
        "duration": fields.get("Duration"),
        "fee": fields.get("Fee"),
        "conditions": [c.strip() for c in (fields.get("Conditions (one per line)") or "").splitlines() if c.strip()] or None,
        "extension": fields.get("Extension"),
        "notes": fields.get("Notes"),
        "source": {"name": fields.get("Official source name"), "url": fields.get("Official source URL")},
        "verified": fields.get("Date you verified (YYYY-MM-DD)"),
    }
    if status != "special":
        raw["requires"] = raw["benefit"] = raw["held_visas"] = None
    entry = {k: raw[k] for k in FIELD_ORDER if raw[k] is not None}
    return filename, entry


def upsert(path, entry):
    entries = yaml.safe_load(path.read_text())
    entries = [e for e in entries if e.get("country") != entry["country"]]
    entries.append(entry)
    entries.sort(key=lambda e: e.get("country", ""))
    path.write_text(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True, width=100))


def main():
    fields = parse_issue(os.environ["ISSUE_BODY"])
    if not fields.get("Category") or fields["Category"] not in CATEGORY_FILES:
        sys.exit("Could not read the Category field — please edit the issue using the form structure.")

    filename, entry = build_entry(fields)
    errors = validate_entry(entry, entry["status"], None)
    if errors:
        sys.exit("The submission has problems:\n" + "\n".join(f"- {e}" for e in errors))

    upsert(DATA_DIR / filename, entry)
    print(f"Updated _data/{filename} for {entry['country']}")


if __name__ == "__main__":
    main()
