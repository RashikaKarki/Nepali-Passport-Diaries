# Contributing

Thank you — this project only works because people keep it accurate.

## The easy way: fill a form

1. Open [Add a destination](../../issues/new?template=add-entry.yml) or
   [Update a destination](../../issues/new?template=update-entry.yml).
2. Fill every required field. The **official source URL** and the **date you
   verified it** are mandatory — read [DATA_POLICY.md](DATA_POLICY.md) first.
3. Submit. A bot opens a pull request from your submission and links it on
   the issue. A maintainer reviews it against the source and merges.

If you spot a mistake but don't have the corrected details, use
[Report an error](../../issues/new?template=report-error.yml).

## The direct way: edit the YAML

Data lives in `_data/`, one file per category:

| File | Meaning | `status` value |
|---|---|---|
| `visa_free.yml` | No visa needed before or on arrival | `visa_free` |
| `visa_on_arrival.yml` | Visa issued at the border | `visa_on_arrival` |
| `evisa.yml` | Apply online before travel | `evisa` |
| `special_cases.yml` | Extra access via a third-country visa | `special` |

Entry template:

```yaml
- country: Thailand
  iso: TH
  region: Asia
  status: visa_on_arrival
  duration: 15 days
  fee: "THB 2,000 (cash only)"          # optional
  conditions:
    - Passport valid ≥ 6 months
    - Confirmed return or onward ticket
  extension: Not extendable              # optional
  notes: Available at major airports.    # optional
  source:
    name: Thai Immigration Bureau
    url: https://www.immigration.go.th/en
  verified: 2026-08-08
```

Special-case entries add:

```yaml
  requires: Valid US visa of any type
  benefit: Enter without a local visa
  held_visas: [US]
```

Keep entries **alphabetical by country**. If your source's domain is new,
add it to `scripts/allowed_sources.yml` in the same PR.

Before opening the PR:

```bash
python3 -m pip install pyyaml requests pytest
python3 scripts/validate_data.py        # must print "All data files valid."
python3 -m pytest tests/ -q             # if you changed scripts/
```

## What reviewers check

1. The source is genuinely official (government-operated).
2. The page actually says what the entry says.
3. The `verified` date is honest and recent.
4. CI is green.

## Code contributions

The site is deliberately boring: Jekyll, one CSS file, one small JS file, no
frameworks, no build step beyond Jekyll. Please keep it that way — modular
includes, small pure functions, minimal comments.
