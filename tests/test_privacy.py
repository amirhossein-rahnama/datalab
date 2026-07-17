import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pandas as pd  # noqa: E402
import privacy  # noqa: E402

def test_email_column_flagged_by_name():
    df = pd.DataFrame({
        "email": ["alice@example.com", "bob@example.com"],
        "amount": [10, 20],
    })
    findings = privacy.scan_pii(df)
    assert "email" in {f["column"] for f in findings}

def test_value_pattern_flags_unlabeled_email_column():
    df = pd.DataFrame({
        "contact_info": ["alice@example.com", "bob@example.com"],
        "amount": [10, 20],
    })
    findings = privacy.scan_pii(df)
    flagged = {f["column"]: f for f in findings}
    assert "contact_info" in flagged
    assert "email" in flagged["contact_info"]["reason"]
    assert flagged["contact_info"]["sample_match"] is not None

def test_non_pii_column_not_flagged():
    df = pd.DataFrame({"amount": [10, 20, 30]})
    assert privacy.scan_pii(df) == []

def test_phone_column_flagged_by_value_pattern():
    df = pd.DataFrame({"contact_number": ["123-456-7890", "234-567-8901"]})
    findings = privacy.scan_pii(df)
    flagged = {f["column"]: f for f in findings}
    assert "contact_number" in flagged
    assert "phone" in flagged["contact_number"]["reason"]
