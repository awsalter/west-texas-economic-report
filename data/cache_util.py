"""
Cache-freshness helper shared by every fetcher in this package.

Why this exists: each fetcher saves its API response as a parquet file under
data/cache/ (gitignored). The original guard was `if CACHE.exists(): return
read_parquet(CACHE)` — an expiry-free cache. Once written, it was served
forever, so a rebuild produced identical numbers under a freshly stamped
"Last updated" date. The caches written on 2026-05-27 were still being served
in September 2026, two published QCEW quarters behind.

This module adds one age check so stale caches re-fetch on their own.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

# QCEW publishes quarterly with a 6-9 month lag, so re-checking weekly is more
# than enough resolution while keeping the refresh cheap (~100 small CSVs).
DEFAULT_MAX_AGE_DAYS = 7

# Annual series (BEA farm income, FRED county GDP, IRS migration) only change
# once a year; checking monthly avoids pointless API traffic.
ANNUAL_MAX_AGE_DAYS = 30


def force_refresh() -> bool:
    """True when the caller demanded a full re-fetch via WTER_REFRESH=1."""
    return os.environ.get("WTER_REFRESH", "").strip().lower() in {"1", "true", "yes"}


def cache_is_fresh(path: Path, max_age_days: float = DEFAULT_MAX_AGE_DAYS) -> bool:
    """True if `path` exists, is non-empty, and is younger than `max_age_days`.

    A missing, empty, or unreadable file counts as stale so the caller re-fetches.
    WTER_REFRESH=1 forces every cache to report stale.
    """
    if force_refresh():
        return False
    try:
        stat = path.stat()
    except OSError:
        return False
    if stat.st_size == 0:
        return False
    return (time.time() - stat.st_mtime) < max_age_days * 86400
