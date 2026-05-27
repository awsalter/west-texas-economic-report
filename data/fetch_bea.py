"""
BEA Regional Economic Accounts fetcher — farm employment by county.

Pulls table CAEMP25N line 70 ("Farm employment") from the BEA API. Unlike
QCEW (which is UI-payroll only), BEA farm employment INCLUDES self-employed
farmers and ranchers — closing QCEW's largest agricultural coverage gap.

Reads BEA_API_KEY from the environment (via .env in dev, via GitHub secrets
in CI). Returns an empty DataFrame on missing key or any fetch failure so
the treemap annotation degrades silently.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests

from data.constants import (
    BEA_API_BASE, BEA_FARM_EMPLOYMENT_TABLE, BEA_FARM_EMPLOYMENT_LINECODE,
    COUNTIES,
)

CACHE_DIR = Path(__file__).parent / "cache"
BEA_CACHE = CACHE_DIR / "bea_farm_employment.parquet"


def _bea_api_key() -> str:
    return os.environ.get("BEA_API_KEY", "").strip()


def _fetch_from_bea(api_key: str) -> pd.DataFrame:
    """One API call for all 3 counties × all available years."""
    geo_fips = ",".join(COUNTIES.keys())
    resp = requests.get(
        BEA_API_BASE,
        params={
            "UserID": api_key,
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": BEA_FARM_EMPLOYMENT_TABLE,
            "LineCode": BEA_FARM_EMPLOYMENT_LINECODE,
            "GeoFips": geo_fips,
            "Year": "ALL",
            "ResultFormat": "json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json().get("BEAAPI", {}).get("Results", {})
    if isinstance(payload, dict) and "Error" in payload:
        return pd.DataFrame()
    rows = payload.get("Data", []) if isinstance(payload, dict) else []
    if not rows:
        return pd.DataFrame()

    records = []
    for row in rows:
        fips = row.get("GeoFips")
        county = COUNTIES.get(fips)
        if not county:
            continue
        raw_val = str(row.get("DataValue", "")).replace(",", "").strip()
        # BEA suppression markers — "(D)", "(NA)", "(L)" — yield missing values.
        try:
            value = float(raw_val)
        except (ValueError, TypeError):
            continue
        try:
            year = int(row.get("TimePeriod"))
        except (ValueError, TypeError):
            continue
        records.append({"county_name": county, "year": year, "value": value})

    return pd.DataFrame(records).sort_values(["county_name", "year"]).reset_index(drop=True)


def fetch_farm_employment() -> pd.DataFrame:
    """Cached fetch of annual BEA farm employment for the 3 counties.

    Returns an empty DataFrame if no cache and no API key is set.
    """
    if BEA_CACHE.exists():
        return pd.read_parquet(BEA_CACHE)
    api_key = _bea_api_key()
    if not api_key:
        return pd.DataFrame()
    df = _fetch_from_bea(api_key)
    if not df.empty:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(BEA_CACHE, index=False)
    return df


def latest_farm_employment(df: pd.DataFrame, county_name: str) -> dict | None:
    """Most recent year's farm employment for one county."""
    if df.empty:
        return None
    sub = df[df["county_name"] == county_name].sort_values("year")
    if sub.empty:
        return None
    row = sub.iloc[-1]
    return {"year": int(row["year"]), "value": int(row["value"])}
