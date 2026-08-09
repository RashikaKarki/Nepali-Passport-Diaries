import sys
import textwrap
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import issue_to_pr as bot

BODY = textwrap.dedent("""\
    ### Category

    Visa on arrival

    ### Country

    Thailand

    ### ISO code

    TH

    ### Region

    Asia

    ### Duration

    15 days

    ### Fee

    THB 2,000 (cash only)

    ### Conditions (one per line)

    Passport valid ≥ 6 months
    Confirmed return or onward ticket

    ### Extension

    _No response_

    ### Notes

    _No response_

    ### Official source name

    Thai Immigration Bureau

    ### Official source URL

    https://www.immigration.go.th/en

    ### Date you verified (YYYY-MM-DD)

    2026-08-01

    ### Requires (special cases only)

    _No response_

    ### Benefit (special cases only)

    _No response_

    ### Held visas (special cases only)

    - [ ] US
    - [ ] Schengen
    - [ ] Japan
    - [ ] UK
    - [ ] Canada
    - [ ] Australia

    ### Accuracy confirmation

    - [x] I checked this information on the official source linked above, on the date given.
    """)


def test_parse_issue_reads_fields():
    fields = bot.parse_issue(BODY)
    assert fields["Country"] == "Thailand"
    assert fields["Fee"] == "THB 2,000 (cash only)"
    assert fields["Extension"] is None


def test_build_entry_maps_category_and_fields():
    filename, entry = bot.build_entry(bot.parse_issue(BODY))
    assert filename == "visa_on_arrival.yml"
    assert entry["status"] == "visa_on_arrival"
    assert entry["conditions"] == ["Passport valid ≥ 6 months", "Confirmed return or onward ticket"]
    assert "extension" not in entry
    assert entry["source"] == {"name": "Thai Immigration Bureau", "url": "https://www.immigration.go.th/en"}
    assert entry["verified"] == "2026-08-01"


def test_build_entry_special_case():
    body = BODY.replace("Visa on arrival", "Special case (extra access with another country's visa)")
    body = body.replace("### Requires (special cases only)\n\n_No response_", "### Requires (special cases only)\n\nValid US visa")
    body = body.replace("### Benefit (special cases only)\n\n_No response_", "### Benefit (special cases only)\n\nVisa-free entry")
    body = body.replace("- [ ] US", "- [x] US")
    filename, entry = bot.build_entry(bot.parse_issue(body))
    assert filename == "special_cases.yml"
    assert entry["held_visas"] == ["US"]
    assert entry["requires"] == "Valid US visa"


def test_upsert_inserts_alphabetically(tmp_path):
    path = tmp_path / "visa_on_arrival.yml"
    path.write_text(yaml.safe_dump([{"country": "Cambodia"}, {"country": "Timor-Leste"}], sort_keys=False))
    _, entry = bot.build_entry(bot.parse_issue(BODY))
    bot.upsert(path, entry)
    countries = [e["country"] for e in yaml.safe_load(path.read_text())]
    assert countries == ["Cambodia", "Thailand", "Timor-Leste"]


def test_upsert_replaces_existing(tmp_path):
    path = tmp_path / "visa_on_arrival.yml"
    path.write_text(yaml.safe_dump([{"country": "Thailand", "duration": "old"}], sort_keys=False))
    _, entry = bot.build_entry(bot.parse_issue(BODY))
    bot.upsert(path, entry)
    entries = yaml.safe_load(path.read_text())
    assert len(entries) == 1
    assert entries[0]["duration"] == "15 days"
