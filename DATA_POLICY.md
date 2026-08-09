# Data Policy

This project's only promise is accuracy. These rules are non-negotiable.

## 1. Official sources only

Every entry's `source` must cite a page operated by a **government**: an
immigration department, ministry of foreign affairs, official eVisa portal,
or embassy.

Not acceptable: Wikipedia, IATA/Timatic resellers, airline pages, visa
agencies, travel blogs, news articles, other aggregator sites.

**Narrow exception:** when a destination government publishes no usable web
source at all, airline-grade data (IATA Travel Centre / Timatic) may be cited
as the `source`, and the entry must carry `verify_before_travel: true`.
Aggregators such as Passport Index or Wikipedia are never acceptable as a
`source` except under this same no-official-page exception; they are welcome
in the `proof` block (see §2).

The source's domain must be listed in `scripts/allowed_sources.yml`. If you
cite a new official domain, add it in the same pull request — reviewers will
check that the domain really belongs to a government.

## 2. Every fact is dated — and Nepal-specific proof is gold

Each entry carries exactly one date field:

- `verified: YYYY-MM-DD` — someone opened the source and confirmed the details
  **as they apply to Nepali passports** on that date.
- `checked: YYYY-MM-DD` — someone reviewed the entry against the source, but
  Nepal-specific confirmation is still outstanding.

Refreshing these dates (after re-checking!) is a valuable contribution on its
own, and upgrading a `checked` entry to `verified` even more so.

An optional `proof` block records the Nepal-specific corroboration:

```yaml
proof:
  nepal_explicitly_named: true   # false when a nationality-agnostic rule covers Nepal
  url: https://…                 # where the Nepal-specific claim is shown (any https page)
  evidence: >                    # what the page says, in one paragraph
  secondary_url: https://…       # optional second corroborating page
  caveat: …                      # optional known wrinkle
```

`proof.url` is deliberately not restricted to the allowlist — Wikipedia's
Nepal table, Timatic-derived data, or news coverage are fine *as proof*; the
primary `source` still has to be official.

## 3. When in doubt, leave it out

If a rule cannot be confirmed on an official source, it does not ship.
Partial, verified information beats complete, guessed information.

## 4. Corrections outrank additions

If the site says something wrong, fixing it is the highest-priority
contribution. Correction entries stay in their original file with a
correction status (see §5) so readers who expect the old claim find the
warning. Use the *Report an error* issue form even if you don't have the
corrected details.

## 5. What each entry needs

Required: `country`, `iso`, `region`, `status`, `duration`, `conditions`,
`source.name`, `source.url` (https, official), and `verified` or `checked`.
Special cases also require: `requires`, `benefit`, `held_visas`.
Optional: `fee`, `extension`, `notes`, `legal_basis`, `confidence`
(high/medium/low), `proof` (§2), `verify_before_travel`.

`status` must match the file, with these variants allowed:

| File | Statuses |
|---|---|
| `visa_free.yml` | `visa_free`, `freedom_of_movement`, `visa_free_nominal`, `visa_required` (correction) |
| `visa_on_arrival.yml` | `visa_on_arrival`, `online_visa_required` (correction) |
| `evisa.yml` | `evisa`, `evisa_conditional` |
| `special_cases.yml` | `special`, `special_restricted` (no-shortcut warning) |

`region` is one of: Africa, Americas, Asia, Caribbean, Europe, Middle East,
Oceania. `held_visas` values: US, Schengen, Japan, UK, Canada, Australia,
New Zealand, Ireland, South Korea, Israel, UAE, Saudi Arabia, GCC.
A country may appear in more than one file when it genuinely offers both
channels (e.g. Cambodia's airport VOA and its eVisa).

CI enforces all of this on every pull request.
