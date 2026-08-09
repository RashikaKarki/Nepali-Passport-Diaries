#!/usr/bin/env python3
"""Validates the visa data files in _data/ against the schema in DATA_POLICY.md."""

import argparse
import datetime
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "_data"
ALLOWLIST_PATH = Path(__file__).resolve().parent / "allowed_sources.yml"

FILES = {
    "visa_free.yml": "visa_free",
    "visa_on_arrival.yml": "visa_on_arrival",
    "evisa.yml": "evisa",
    "special_cases.yml": "special",
}
# Each file's primary status plus the correction/variant statuses it may hold.
STATUS_VARIANTS = {
    "visa_free": {"visa_free", "freedom_of_movement", "visa_free_nominal", "visa_required"},
    "visa_on_arrival": {"visa_on_arrival", "online_visa_required"},
    "evisa": {"evisa", "evisa_conditional"},
    "special": {"special", "special_restricted"},
}
REQUIRED = ("country", "iso", "region", "status", "duration", "conditions", "source")
REGIONS = {"Africa", "Americas", "Asia", "Caribbean", "Europe", "Middle East", "Oceania"}
HELD_VISAS = {
    "US", "Schengen", "Japan", "UK", "Canada", "Australia",
    "New Zealand", "Ireland", "South Korea", "Israel", "UAE", "Saudi Arabia", "GCC",
}
CONFIDENCE = {"high", "medium", "low"}
ISO_RE = re.compile(r"^[A-Z]{2}$")


def load_allowed_domains():
    return yaml.safe_load(ALLOWLIST_PATH.read_text()) or []


def _domain_allowed(url, allowed_domains):
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in allowed_domains)


def _parse_date(value):
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def _validate_date(e, errors):
    dated_fields = [f for f in ("verified", "checked") if e.get(f)]
    if not dated_fields:
        errors.append("missing required field(s): verified (or checked)")
        return
    if len(dated_fields) == 2:
        errors.append("use either verified or checked, not both")
    field = dated_fields[0]
    date = _parse_date(e[field])
    if date is None:
        errors.append(f"{field} must be a YYYY-MM-DD date, got {e[field]!r}")
    elif date > datetime.date.today():
        errors.append(f"{field} date {date} is in the future")


def _validate_proof(proof, errors):
    if not isinstance(proof, dict):
        errors.append("proof must be a mapping")
        return
    if "nepal_explicitly_named" not in proof or not isinstance(proof["nepal_explicitly_named"], bool):
        errors.append("proof needs a boolean nepal_explicitly_named")
    if not proof.get("url") or not str(proof["url"]).startswith("https://"):
        errors.append("proof.url must be an https URL")
    if not proof.get("evidence"):
        errors.append("proof needs an evidence summary")


def validate_entry(e, status, allowed_domains):
    errors = []
    missing = [f for f in REQUIRED if not e.get(f)]
    if missing:
        return [f"missing required field(s): {', '.join(missing)}"]

    if not ISO_RE.match(e["iso"]):
        errors.append(f"iso must be two uppercase letters, got {e['iso']!r}")
    if e["region"] not in REGIONS:
        errors.append(f"region must be one of {sorted(REGIONS)}, got {e['region']!r}")
    variants = STATUS_VARIANTS[status]
    if e["status"] not in variants:
        errors.append(f"status must be one of {sorted(variants)} in this file, got {e['status']!r}")
    if not isinstance(e["conditions"], list) or not all(isinstance(c, str) and c for c in e["conditions"]):
        errors.append("conditions must be a non-empty list of strings")

    source = e["source"]
    if not isinstance(source, dict) or not source.get("name") or not source.get("url"):
        errors.append("source must have name and url")
    else:
        url = source["url"]
        if not url.startswith("https://"):
            errors.append("source.url must use https")
        elif allowed_domains is not None and not _domain_allowed(url, allowed_domains):
            errors.append(
                f"source domain not in scripts/allowed_sources.yml: {urlparse(url).hostname}"
            )

    _validate_date(e, errors)

    if e.get("confidence") and e["confidence"] not in CONFIDENCE:
        errors.append(f"confidence must be one of {sorted(CONFIDENCE)}, got {e['confidence']!r}")
    if e.get("proof"):
        _validate_proof(e["proof"], errors)

    if e["status"] == "special":
        for field in ("requires", "benefit", "held_visas"):
            if not e.get(field):
                errors.append(f"special entries need {field}")
        held = e.get("held_visas") or []
        unknown = [v for v in held if v not in HELD_VISAS]
        if unknown:
            errors.append(f"held_visas must be from {sorted(HELD_VISAS)}, got {unknown}")
    elif e["status"] == "special_restricted":
        if not e.get("benefit"):
            errors.append("special_restricted entries need benefit")

    return errors


def validate_file(path, status, allowed_domains):
    entries = yaml.safe_load(path.read_text())
    if not isinstance(entries, list) or not entries:
        return [f"{path.name}: must be a non-empty list of entries"]

    errors = []
    seen = set()
    for i, e in enumerate(entries):
        label = e.get("country", f"entry {i}") if isinstance(e, dict) else f"entry {i}"
        if not isinstance(e, dict):
            errors.append(f"{path.name} → {label}: entry must be a mapping")
            continue
        if label in seen:
            errors.append(f"{path.name} → {label}: duplicate country")
        seen.add(label)
        errors.extend(f"{path.name} → {label}: {err}" for err in validate_entry(e, status, allowed_domains))
    return errors


def check_urls(paths):
    import requests

    errors = []
    for path in paths:
        for e in yaml.safe_load(path.read_text()):
            url = e.get("source", {}).get("url")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=20, allow_redirects=True,
                                    headers={"User-Agent": "nepali-passport-diaries-validator"})
                if resp.status_code >= 400:
                    errors.append(f"{path.name} → {e['country']}: source URL returned {resp.status_code}: {url}")
            except requests.RequestException as exc:
                errors.append(f"{path.name} → {e['country']}: source URL unreachable ({exc.__class__.__name__}): {url}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-urls", action="store_true", help="also verify every source URL is reachable")
    args = parser.parse_args()

    allowed = load_allowed_domains()
    errors = []
    for name, status in FILES.items():
        path = DATA_DIR / name
        if not path.exists():
            errors.append(f"{name}: file missing")
            continue
        errors.extend(validate_file(path, status, allowed))

    if errors:
        print(f"{len(errors)} problem(s) found:\n")
        print("\n".join(f"  ✗ {e}" for e in errors))
        sys.exit(1)

    if args.check_urls:
        errors = check_urls([DATA_DIR / name for name in FILES])
        if errors:
            print(f"{len(errors)} problem(s) found:\n")
            print("\n".join(f"  ✗ {e}" for e in errors))
            sys.exit(1)
    print("All data files valid.")


if __name__ == "__main__":
    main()
