"""
Constants for the West Texas Regional Economic Dashboard.
FIPS codes, NAICS labels, ownership codes, color palette, and API config.

Covers the top 3 counties by population of Texas's 19th congressional district:
Lubbock, Taylor (Abilene), and Howard (Big Spring).
"""
from datetime import date

# ── BLS QCEW API ──────────────────────────────────────────────────────────────
BLS_BASE_URL = "https://data.bls.gov/cew/data/api/{year}/{quarter}/area/{fips}.csv"

# Year range: 2019 through current year (API returns 404 for unpublished quarters)
START_YEAR = 2019
END_YEAR = date.today().year
YEARS = list(range(START_YEAR, END_YEAR + 1))
QUARTERS = [1, 2, 3, 4]

# ── Counties (top 3 of TX-19 by population) ──────────────────────────────────
COUNTIES = {
    "48303": "Lubbock",  # Lubbock metro
    "48441": "Taylor",   # Abilene metro
    "48227": "Howard",   # Big Spring
}

# ── Color Palette ────────────────────────────────────────────────────────────
# TTU-inspired scarlet & black anchor; no institutional affiliation claimed.
BLACK       = "#000000"   # primary; headers, titles, KPI values, Lubbock county
SCARLET     = "#CC0000"   # accent; negative deltas, Taylor county, goods-producing
CHARCOAL    = "#2D2D2D"   # body text, labels
LIGHT_GRAY  = "#CCCCCC"   # borders, tab underlines
SLATE_BLUE  = "#5B7C8C"   # links, Howard county, professional & business industry
OLIVE       = "#7A8B5C"   # education & health industry
OFF_WHITE   = "#F5F5F5"   # badge background
SAND        = "#C9A87A"   # trade & logistics industry
NAVY        = "#1F3A5C"   # information & finance industry

COUNTY_COLORS = {
    "Lubbock": BLACK,
    "Taylor":  SCARLET,
    "Howard":  SLATE_BLUE,
}

# Industry → palette color, grouped by broad domain. Used by the Growth
# Quadrant chart, which colors bubbles by domain rather than by county.
INDUSTRY_DOMAIN_COLORS = {
    # Goods-producing
    "Agriculture":                       SCARLET,
    "Mining":                            SCARLET,
    "Utilities":                         SCARLET,
    "Construction":                      SCARLET,
    "Manufacturing":                     SCARLET,
    # Trade & Logistics
    "Wholesale Trade":                   SAND,
    "Retail Trade":                      SAND,
    "Transportation & Warehousing":      SAND,
    # Information & Finance
    "Information":                       NAVY,
    "Finance & Insurance":               NAVY,
    "Real Estate":                       NAVY,
    # Professional & Business
    "Professional & Technical Services": SLATE_BLUE,
    "Management of Companies":           SLATE_BLUE,
    "Admin & Waste Services":            SLATE_BLUE,
    # Education & Health
    "Educational Services":              OLIVE,
    "Health Care & Social Assistance":   OLIVE,
    # Leisure & Other
    "Arts & Entertainment":              CHARCOAL,
    "Accommodation & Food Services":     CHARCOAL,
    "Other Services":                    CHARCOAL,
    "Public Administration":             CHARCOAL,
}

# ── Aggregation levels ────────────────────────────────────────────────────────
# 70 = Total, all industries (own_code 0 only)
# 71 = Total, all industries by ownership
# 72 = Supersector (NAICS domain)
# 73 = Supersector subdivision
# 74 = NAICS Sector (2-digit)
# 75 = NAICS 3-digit
# 76 = NAICS 4-digit
# 77 = NAICS 5-digit
# 78 = NAICS 6-digit
AGGLVL_US_TOTAL = 10       # U.S. national total (only valid for area_fips=US000)
AGGLVL_US_BY_OWN = 11      # U.S. total by ownership; rows for own_codes 1, 2, 3, 5


# ── External (non-QCEW) data sources ─────────────────────────────────────────
# These power the second row of metrics on each county's KPI card.

FRED_API_BASE = "https://api.stlouisfed.org/fred"

# Real GDP series (annual, thousands of chained 2017 dollars). FIPS-derivable.
FRED_GDP_SERIES = {
    "Lubbock": "REALGDPALL48303",
    "Taylor":  "REALGDPALL48441",
    "Howard":  "REALGDPALL48227",
}

# Unemployment rate series (monthly %, NSA). IDs are NOT derivable from FIPS —
# verified manually via FRED search. Bump if any series ID is renamed.
FRED_UNRATE_SERIES = {
    "Lubbock": "TXLUBB3URN",
    "Taylor":  "TXTAYL1URN",
    "Howard":  "TXHOWA7URN",
}

# IRS Statistics of Income county-to-county migration data. Year pair is the
# tax-year transition (e.g., "2223" = 2022→2023 flows). Bump explicitly when
# IRS publishes a newer year so the version change is visible in git.
IRS_SOI_BASE_URL = "https://www.irs.gov/pub/irs-soi"
LATEST_IRS_YEAR_PAIR = "2223"

# BEA Regional Economic Accounts. Farm employment (CAEMP25N line 70) covers
# the full agricultural workforce INCLUDING self-employed farmers and
# ranchers — fills QCEW's UI-coverage gap. Annual, county-level.
BEA_API_BASE = "https://apps.bea.gov/api/data"
BEA_FARM_EMPLOYMENT_TABLE = "CAEMP25N"
BEA_FARM_EMPLOYMENT_LINECODE = 70
AGGLVL_TOTAL = 70          # Single-area total covered, own_code=0
AGGLVL_TOTAL_BY_OWN = 71   # Total by ownership
AGGLVL_SUPERSECTOR = 72    # Supersector by ownership
AGGLVL_NAICS_SECTOR = 74   # 2-digit NAICS sector by ownership
AGGLVL_NAICS_4DIGIT = 76   # 4-digit NAICS industry by ownership

# ── Supersector labels (own_code 5 = private) ────────────────────────────────
SUPERSECTOR_LABELS = {
    "11":    "Agriculture",
    "21":    "Mining",
    "22":    "Utilities",
    "23":    "Construction",
    "31-33": "Manufacturing",
    "42":    "Wholesale Trade",
    "44-45": "Retail Trade",
    "48-49": "Transportation & Warehousing",
    "51":    "Information",
    "52":    "Finance & Insurance",
    "53":    "Real Estate",
    "54":    "Professional & Technical Services",
    "55":    "Management of Companies",
    "56":    "Admin & Waste Services",
    "61":    "Educational Services",
    "62":    "Health Care & Social Assistance",
    "71":    "Arts & Entertainment",
    "72":    "Accommodation & Food Services",
    "81":    "Other Services",
    "92":    "Public Administration",
    "99":    "Unclassified",
}

# Supersector codes used by each ownership type at agglvl 72
# (subset varies by ownership; own_code 5 has the broadest private set)
SUPERSECTOR_DOMAIN_CODES = {
    "101": "Goods-producing",
    "102": "Service-providing",
    "1011": "Natural Resources & Mining",
    "1012": "Construction",
    "1013": "Manufacturing",
    "1021": "Trade, Transportation & Utilities",
    "1022": "Information",
    "1023": "Financial Activities",
    "1024": "Professional & Business Services",
    "1025": "Education & Health Services",
    "1026": "Leisure & Hospitality",
    "1027": "Other Services",
    "1028": "Public Administration",
    "1029": "Unclassified",
}

# ── Numeric columns that need type conversion ─────────────────────────────────
NUMERIC_COLS = [
    "own_code", "agglvl_code", "size_code", "year", "qtr",
    "qtrly_estabs",
    "month1_emplvl", "month2_emplvl", "month3_emplvl",
    "total_qtrly_wages", "taxable_qtrly_wages", "qtrly_contributions",
    "avg_wkly_wage",
    "lq_qtrly_estabs",
    "lq_month1_emplvl", "lq_month2_emplvl", "lq_month3_emplvl",
    "lq_total_qtrly_wages", "lq_taxable_qtrly_wages",
    "lq_qtrly_contributions", "lq_avg_wkly_wage",
    "oty_qtrly_estabs_chg", "oty_qtrly_estabs_pct_chg",
    "oty_month1_emplvl_chg", "oty_month1_emplvl_pct_chg",
    "oty_month2_emplvl_chg", "oty_month2_emplvl_pct_chg",
    "oty_month3_emplvl_chg", "oty_month3_emplvl_pct_chg",
    "oty_total_qtrly_wages_chg", "oty_total_qtrly_wages_pct_chg",
    "oty_taxable_qtrly_wages_chg", "oty_taxable_qtrly_wages_pct_chg",
    "oty_qtrly_contributions_chg", "oty_qtrly_contributions_pct_chg",
    "oty_avg_wkly_wage_chg", "oty_avg_wkly_wage_pct_chg",
]
