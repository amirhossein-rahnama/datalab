#!/usr/bin/env python3
"""Lightweight PII scanner: flags columns by name keyword and by regex on sampled values.

Heuristic only — designed to catch obvious PII (emails, phone numbers, and common
name-based hints like "ssn", "dob", "address") so a project can be warned before data
with personal information is committed or shared.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

NAME_KEYWORDS = ["email", "mail", "phone", "ssn", "name", "address", "dob", "zip"]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Requires a separator between digit groups so plain numeric IDs don't false-positive.
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-])?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")

VALUE_PATTERNS = [("email", EMAIL_RE), ("phone", PHONE_RE)]


def _load(data) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data
    path = Path(data)
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def scan_pii(df, sample_size: int = 50) -> list[dict]:
    """Scan a DataFrame (or CSV/Parquet path) for likely-PII columns.

    A column is flagged when either:
    - its name contains a PII keyword (see `NAME_KEYWORDS`), or
    - a sample of its values matches an email or phone regex.

    Returns a list of {"column", "reason", "sample_match"} dicts (one per flagged column).
    """
    df = _load(df)
    findings: list[dict] = []

    for col in df.columns:
        col_lower = str(col).lower()
        name_hit = next((kw for kw in NAME_KEYWORDS if kw in col_lower), None)
        if name_hit:
            findings.append(
                {"column": col, "reason": f"column name matches keyword '{name_hit}'", "sample_match": None}
            )
            continue

        sample = df[col].dropna().astype(str).head(sample_size)
        for reason, pattern in VALUE_PATTERNS:
            match = next((v for v in sample if pattern.search(v)), None)
            if match is not None:
                findings.append({"column": col, "reason": f"value matches {reason} pattern", "sample_match": match})
                break

    return findings
