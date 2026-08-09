import copy
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_data as vd

VALID = {
    "country": "Thailand",
    "iso": "TH",
    "region": "Asia",
    "status": "visa_on_arrival",
    "duration": "15 days",
    "fee": "THB 2,000",
    "conditions": ["Passport valid ≥ 6 months", "Return ticket"],
    "source": {"name": "Thai Immigration Bureau", "url": "https://www.immigration.go.th/en"},
    "verified": datetime.date(2026, 8, 1),
}
ALLOWED = ["immigration.go.th"]


def entry(**overrides):
    e = copy.deepcopy(VALID)
    e.update(overrides)
    return e


def test_valid_entry_passes():
    assert vd.validate_entry(VALID, "visa_on_arrival", ALLOWED) == []


def test_missing_required_field():
    e = entry()
    del e["duration"]
    errors = vd.validate_entry(e, "visa_on_arrival", ALLOWED)
    assert any("duration" in err for err in errors)


def test_bad_iso():
    errors = vd.validate_entry(entry(iso="Thai"), "visa_on_arrival", ALLOWED)
    assert any("iso" in err for err in errors)


def test_bad_region():
    errors = vd.validate_entry(entry(region="Far East"), "visa_on_arrival", ALLOWED)
    assert any("region" in err for err in errors)


def test_status_must_match_file():
    errors = vd.validate_entry(entry(status="visa_free"), "visa_on_arrival", ALLOWED)
    assert any("status" in err for err in errors)


def test_future_verified_date():
    future = datetime.date.today() + datetime.timedelta(days=30)
    errors = vd.validate_entry(entry(verified=future), "visa_on_arrival", ALLOWED)
    assert any("verified" in err for err in errors)


def test_checked_accepted_instead_of_verified():
    e = entry(verified=None, checked="2026-08-01")
    assert vd.validate_entry(e, "visa_on_arrival", ALLOWED) == []


def test_missing_both_date_fields():
    errors = vd.validate_entry(entry(verified=None), "visa_on_arrival", ALLOWED)
    assert any("verified" in err for err in errors)


def test_both_date_fields_rejected():
    e = entry(checked="2026-08-01")
    errors = vd.validate_entry(e, "visa_on_arrival", ALLOWED)
    assert any("not both" in err for err in errors)


def test_variant_status_allowed_in_file():
    e = entry(status="online_visa_required")
    assert vd.validate_entry(e, "visa_on_arrival", ALLOWED) == []


def test_variant_status_wrong_file():
    errors = vd.validate_entry(entry(status="visa_required"), "visa_on_arrival", ALLOWED)
    assert any("status" in err for err in errors)


def test_bad_confidence():
    errors = vd.validate_entry(entry(confidence="certain"), "visa_on_arrival", ALLOWED)
    assert any("confidence" in err for err in errors)


def test_valid_confidence():
    assert vd.validate_entry(entry(confidence="medium"), "visa_on_arrival", ALLOWED) == []


def test_proof_shape_enforced():
    errors = vd.validate_entry(entry(proof={"url": "http://x.example"}), "visa_on_arrival", ALLOWED)
    joined = " ".join(errors)
    assert "nepal_explicitly_named" in joined and "https" in joined and "evidence" in joined


def test_valid_proof():
    proof = {
        "nepal_explicitly_named": True,
        "url": "https://example.gov/nepal",
        "evidence": "Official page names Nepal.",
    }
    assert vd.validate_entry(entry(proof=proof), "visa_on_arrival", ALLOWED) == []


def test_special_restricted_needs_only_benefit():
    e = entry(status="special_restricted", benefit="None — warning entry")
    assert vd.validate_entry(e, "special", ALLOWED) == []
    errors = vd.validate_entry(entry(status="special_restricted"), "special", ALLOWED)
    assert any("benefit" in err for err in errors)


def test_expanded_held_visas():
    e = entry(
        status="special",
        requires="Valid UAE or Saudi visa",
        benefit="Unlocks eVisa/VOA",
        held_visas=["UAE", "Saudi Arabia", "New Zealand", "GCC"],
    )
    assert vd.validate_entry(e, "special", ALLOWED) == []


def test_verified_accepts_iso_string():
    assert vd.validate_entry(entry(verified="2026-08-01"), "visa_on_arrival", ALLOWED) == []


def test_unlisted_source_domain():
    e = entry(source={"name": "Some Blog", "url": "https://travelblog.example.com/x"})
    errors = vd.validate_entry(e, "visa_on_arrival", ALLOWED)
    assert any("source" in err for err in errors)


def test_none_allowed_domains_skips_domain_check():
    e = entry(source={"name": "New Gov Site", "url": "https://evisa.example.gov.xx"})
    assert vd.validate_entry(e, "visa_on_arrival", None) == []


def test_http_url_rejected():
    e = entry(source={"name": "Thai Immigration", "url": "http://www.immigration.go.th"})
    errors = vd.validate_entry(e, "visa_on_arrival", ALLOWED)
    assert any("https" in err for err in errors)


def test_special_requires_extra_fields():
    e = entry(status="special")
    errors = vd.validate_entry(e, "special", ALLOWED)
    joined = " ".join(errors)
    assert "requires" in joined and "benefit" in joined and "held_visas" in joined


def test_special_valid():
    e = entry(
        status="special",
        requires="Valid US B1/B2 visa",
        benefit="Enter without a Mexican visa",
        held_visas=["US"],
    )
    assert vd.validate_entry(e, "special", ALLOWED) == []


def test_special_unknown_held_visa():
    e = entry(status="special", requires="x", benefit="y", held_visas=["Mars"])
    errors = vd.validate_entry(e, "special", ALLOWED)
    assert any("held_visas" in err for err in errors)


def test_validate_file_flags_duplicates(tmp_path):
    import yaml

    path = tmp_path / "visa_on_arrival.yml"
    a, b = entry(), entry()
    a["verified"] = b["verified"] = "2026-08-01"
    path.write_text(yaml.safe_dump([a, b], sort_keys=False, allow_unicode=True))
    errors = vd.validate_file(path, "visa_on_arrival", ALLOWED)
    assert any("duplicate" in err.lower() for err in errors)
