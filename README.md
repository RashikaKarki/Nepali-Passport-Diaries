# The Nepali Passport Diaries 🇳🇵

> A field guide to every border that will let you in.

An open-source, community-maintained guide to everywhere a **Nepali passport
holder** can travel **visa-free**, with a **visa on arrival**, with an
**eVisa** — plus the extra doors that open if you hold a valid **US, Schengen,
Japan, UK, Canada, or Australia** visa.

**Every entry links to an official government source and carries the date it
was last verified.** No blogs, no hearsay.

**Live site:** 

## Why

Visa information for Nepali travellers is scattered, outdated, and often
copied blog-to-blog without sources. This repo keeps one dataset where every
fact is dated and verifiable — and anyone can fix it.

## Contributing — two ways

1. **Fill a form (easiest):** open an
   [Add a destination](../../issues/new?template=add-entry.yml) or
   [Update a destination](../../issues/new?template=update-entry.yml) issue.
   A bot turns your submission into a pull request automatically.
2. **Edit the YAML directly:** the data lives in [`_data/`](_data/). See
   [CONTRIBUTING.md](CONTRIBUTING.md) for the schema.

All changes are validated in CI (schema, official-source domain, reachable
URL) and reviewed by a maintainer before they go live. Read
[DATA_POLICY.md](DATA_POLICY.md) — it is short and strict.

## Running locally

```bash
bundle install
bundle exec jekyll serve   # http://127.0.0.1:4000
python3 scripts/validate_data.py   # check the data
```

## Setup after forking/creating the repo

1. Settings → Pages → Deploy from branch → `main` / root.
2. Replace `CHANGE-ME` in `_config.yml`, `README.md`, and
   `.github/ISSUE_TEMPLATE/config.yml` with your GitHub username.

## Disclaimer

Informational only. Visa rules change without notice — always confirm with
the embassy or the official source before you travel.

## License

Code: [MIT](LICENSE). Data (`_data/`):
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
