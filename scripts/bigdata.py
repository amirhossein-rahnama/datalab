#!/usr/bin/env python3
"""Big-data helpers for CSVs too large to load into memory at once.

Provides a fast row count, a class-stratified sampler that only ever loads the rows it
needs, a chunked reader for streaming aggregation, and an optional fast reader backed by
polars.

Only core deps (pandas, numpy) are used at module scope. `polars` (used by `read_fast`) is
a heavy optional dependency and is imported lazily inside that function only, so importing
this module never fails if polars isn't installed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def count_rows(path) -> int:
    """Count data rows in a CSV file (total lines minus the header row).

    Scans the file as raw bytes in fixed-size chunks and counts newlines, so it never
    loads the file into memory and stays fast on files far larger than RAM.
    """
    path = Path(path)
    chunk_size = 1 << 20  # 1 MiB
    newline_count = 0
    ends_with_newline = True

    with open(path, "rb") as f:
        chunk = f.read(chunk_size)
        if not chunk:
            return 0
        while chunk:
            newline_count += chunk.count(b"\n")
            ends_with_newline = chunk.endswith(b"\n")
            chunk = f.read(chunk_size)

    total_lines = newline_count if ends_with_newline else newline_count + 1
    return max(total_lines - 1, 0)


def sample_csv(path, n, stratify_col=None, seed=42) -> pd.DataFrame:
    """Return a pandas DataFrame sample of about `n` rows from a (possibly huge) CSV.

    Only the sampled rows are ever loaded into memory: row positions are chosen first
    (uniform random choice, or per-class when `stratify_col` is given), then a single
    `read_csv(..., skiprows=...)` pass loads just those rows.

    If `stratify_col` is given, that one column is read on its own first, per-class sample
    sizes are computed from its class proportions (rounded, with any rounding drift
    absorbed by the largest class so sizes sum to `n`), and the sample preserves those
    class proportions.
    """
    path = Path(path)
    rng = np.random.RandomState(seed)
    total_rows = count_rows(path)
    if total_rows == 0:
        return pd.read_csv(path)
    n = max(min(n, total_rows), 0)

    if stratify_col is None:
        chosen = rng.choice(total_rows, size=n, replace=False)
    else:
        col = pd.read_csv(path, usecols=[stratify_col])[stratify_col]
        counts = col.value_counts()  # sorted descending by frequency
        proportions = counts / counts.sum()
        sizes = (proportions * n).round().astype(int)

        drift = n - int(sizes.sum())
        if drift != 0:
            biggest = counts.index[0]
            sizes.loc[biggest] = max(int(sizes.loc[biggest]) + drift, 0)

        chosen_parts = []
        values = col.to_numpy()
        for cls, size in sizes.items():
            positions = np.flatnonzero(values == cls)
            size = min(int(size), len(positions))
            if size > 0:
                chosen_parts.append(rng.choice(positions, size=size, replace=False))
        chosen = np.concatenate(chosen_parts) if chosen_parts else np.array([], dtype=np.int64)

    keep = set(int(i) for i in chosen)

    def _skip(line_no: int) -> bool:
        # line_no counts file lines starting at 0 (the header). Data row i (0-based) is
        # file line i + 1, so never skip the header and keep only the chosen data rows.
        return line_no != 0 and (line_no - 1) not in keep

    sample = pd.read_csv(path, skiprows=_skip)
    return sample.reset_index(drop=True)


def read_chunked(path, chunksize: int = 100_000):
    """Yield the CSV at `path` as pandas DataFrame chunks of up to `chunksize` rows each.

    Lets a caller aggregate over a file too large to fit in memory, one chunk at a time,
    e.g. `total = sum(len(chunk) for chunk in read_chunked(path))`.
    """
    for chunk in pd.read_csv(path, chunksize=chunksize):
        yield chunk


def read_fast(path) -> pd.DataFrame:
    """Read a CSV with polars (fast, multi-threaded, lower memory) and return the result
    as a pandas DataFrame.

    Optional dependency: requires `polars`, imported lazily here only, so importing this
    module never fails if polars isn't installed.
    """
    try:
        import polars as pl
    except ImportError as exc:
        raise ImportError(
            "read_fast requires the 'polars' package. Install it with: pip install polars"
        ) from exc

    return pl.read_csv(path).to_pandas()
