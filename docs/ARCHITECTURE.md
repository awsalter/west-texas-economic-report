# West Texas Economic Report — Architecture

*Internal architecture reference for the project. New users should start at the [root README](../README.md); this file documents internals for anyone modifying the code.*

Adapted from Bryan Cutsinger's [South Florida Regional Economic Report](https://github.com/bryanpcutsinger/south-florida-economic-report) (MIT, FAU).

## What this is

A single-page Streamlit + Plotly dashboard analyzing the economies of Lubbock, Taylor (Abilene), and Howard (Big Spring) counties — the top three counties by population of Texas's 19th congressional district. Features a regional snapshot on the main page with per-county deep-dive tabs. The same components also feed `build.py`, which renders a static HTML version plus standalone iframe-embeddable chart pages for GitHub Pages.

Run with `streamlit run app.py` (interactive) or `python build.py` (static build).

## Project Structure

```
app.py                          # Main Streamlit app — regional snapshot + 3 county tabs
build.py                        # Static HTML generator — produces docs/index.html + docs/embeds/*.html
data/
  constants.py                  # FIPS codes (3 counties), NAICS labels, aggregation levels, color palette
  clean.py                      # QCEW cleaning pipeline + filtering helpers
  analysis.py                   # STL trend decomposition + linear 2Q projection (deseasonalize_trend, project_trend)
  fetch.py                      # QCEW data fetch (BLS CSV API) — county + national caches in data/cache/
  fetch_fred.py                 # FRED API client — county real GDP + unemployment rate (powers KPI secondary row)
  fetch_irs_migration.py        # IRS SOI migration fetcher — net domestic migration per county (KPI secondary row)
  fetch_bea.py                  # BEA REA CAEMP25N farm employment — annotation under workforce composition treemap
  cache/                        # Parquet caches — qcew_data.parquet, qcew_national.parquet, qcew_fred_gdp.parquet, qcew_fred_unrate.parquet, qcew_irs_migration.parquet, bea_farm_employment.parquet
components/
  employment_trends.py          # Side-by-side line charts — raw + STL trend + 2-quarter linear projection for employment and salary
  growth_quadrant.py            # Industry Landscape — YoY employment × YoY wage growth; bubbles colored by industry domain
  firm_formation.py             # Firm Openings & Closings — quarterly establishment churn aggregated from industry-level QoQ deltas
  employment_treemap.py         # Workforce Composition — treemap of private employment by NAICS sector + BEA farm-employment annotation
utils/
  formatting.py                 # fmt_number, fmt_currency, fmt_pct
  narratives.py                 # source_citation(), narrate_employment_trends(), format_industry_list()
docs/                           # Published GitHub Pages output
  embeds/                       # Standalone iframe-embeddable chart HTMLs (one per county × section)
audits/                         # Dated point-in-time data validation reports
.github/workflows/
  update-data.yml               # Weekly Monday refresh — fetches fresh data and rebuilds docs/
```

## Dashboard Layout

### Main Page — Regional Snapshot

- Title and subtitle with data quarter badge
- 3 styled KPI cards (one per county), each showing two rows:
  - Primary (QCEW): Total Employment, Establishments, Average Salary — all with YoY % change.
  - Secondary: Real GDP ($B + YoY %), Unemployment rate (% + YoY pp delta, sign-inverted so falling = green), Net Migration (signed integer, IRS SOI tax-year flow, no arrow). Each cell labels its data period in small gray text.
- Secondary row reads "—" gracefully if any API key is missing or any fetch fails; primary row is unaffected.

### County Tabs (Lubbock | Taylor | Howard)

Each tab renders 4 sections for that county:

| # | Section | Component | Chart Type |
|---|---------|-----------|------------|
| 1 | Employment & Salary Trends | `employment_trends.py` | Side-by-side line charts (raw + STL trend + 2Q linear projection) |
| 2 | Workforce Composition | `employment_treemap.py` | Treemap — sectors sized by private employment, colored by industry domain. Year buttons below the chart switch the snapshot to the latest quarter of any year back to 2019. Includes a BEA farm-employment annotation below the chart that closes QCEW's UI-payroll coverage gap for self-employed farmers and ranchers. |
| 3 | Industry Landscape | `growth_quadrant.py` | Bubble scatter — YoY employment × YoY wage growth |
| 4 | Firm Openings & Closings | `firm_formation.py` | Stacked-relative bar — QoQ establishment additions (blue) vs. losses (red) per quarter, with net line + dashed U.S. benchmark overlay |

## Counties

| County | FIPS | Card Color | Metro |
|--------|------|------------|-------|
| Lubbock | 48303 | Black (#000000) | Lubbock |
| Taylor | 48441 | Scarlet (#CC0000) | Abilene |
| Howard | 48227 | Slate Blue (#5B7C8C) | Big Spring |

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Black | #000000 | Primary — headers, titles, KPI values, Lubbock county |
| Scarlet | #CC0000 | Accent — negative deltas, Taylor county, goods-producing industry |
| Charcoal | #2D2D2D | Body text, labels, leisure & other industry |
| Light Gray | #CCCCCC | Borders, tab underlines |
| Slate Blue | #5B7C8C | Links, Howard county, professional & business industry |
| Olive | #7A8B5C | Education & health industry |
| Off-White | #F5F5F5 | Data badge background |
| Sand | #C9A87A | Trade & logistics industry |
| Navy | #1F3A5C | Information & finance industry |

Scarlet-and-black anchor inspired by Texas Tech but with no institutional affiliation claimed. White background throughout (no dark theme).

## Key Design Decisions

- **Single page, no sidebar** — scroll-through narrative layout with tabs for county drill-downs
- **3 counties**: Lubbock, Taylor (Abilene), Howard (Big Spring) — top 3 by population in TX-19
- **QCEW data only** for industry sections — all components use BLS QCEW CSV API (no API key needed)
- **2-digit NAICS** (agglvl_code=74) for all industry analysis
- **Ownership codes**: Regional snapshot uses own_code=0 (Total Covered); all industry sections use own_code=5 (Private only)
- **"Unclassified" excluded** from all industry charts
- **Employment measure**: `month3_emplvl` (third month of quarter), aliased as `employment` in clean.py
- **Avg annual wage**: `avg_wkly_wage * 52`, derived in clean.py
- **Location quotients**: `lq_month3_emplvl` and `lq_avg_wkly_wage` — pre-computed by BLS in QCEW CSV
- **Component pattern**: Each component exposes `render(df)` for Streamlit and `build_figure(...)` for the static build — both receive a pre-filtered county DataFrame
- **Streamlit-free build boundary**: `build.py` deliberately runs without importing streamlit (see `requirements-build.txt`). The duplicated KPI HTML helpers (`_delta_html`, `_secondary_row_html`) in `app.py` and `build.py` preserve this separation.
- **Data caching**: All 3 counties cached to `data/cache/qcew_data.parquet`; first load fetches from BLS (~3 min); subsequent loads read from disk.
- **BEA farm employment annotation**: Lubbock/Taylor/Howard are urban anchors of a heavily agricultural region. QCEW's UI-payroll coverage misses self-employed farmers and ranchers, dramatically undercounting the ag workforce. BEA REA table CAEMP25N (line 70, Farm employment) captures the full picture and is surfaced as an annotation under the Workforce Composition treemap.

## Data Pipeline

1. `fetch.py` → downloads BLS CSV for each year/quarter/county (3 counties × years × quarters), caches to `qcew_data.parquet`. Also fetches the U.S. national aggregate (area code `US000`, agglvl=10) once and caches to `qcew_national.parquet` for the firm-formation benchmark line.
2. `clean.py` → standardizes types, adds `employment`, `avg_annual_wage`, `is_suppressed`, `industry_label` columns.
3. `app.py` (or `build.py`) → filters `df[df["county_name"] == county]` for each tab, passes to components.
4. Filter helpers in `clean.py`: `get_total_covered(df)`, `get_naics_sectors(df)`, `get_latest_quarter(df)`.
5. `analysis.py` → `deseasonalize_trend(series, period=4, log_transform=False)` returns the STL trend component for use in projections.

For data source citations (BLS QCEW, FRED, IRS SOI, BEA), see the [root README](../README.md#data-sources).

## API Keys

- **QCEW**: unauthenticated; no key needed.
- **FRED** (county GDP + unemployment for the secondary KPI row): set `FRED_API_KEY` in the environment. Without it, secondary KPI cells render "—" but the rest of the dashboard works.
- **IRS SOI** (net migration): public download, no key.
- **BEA** (farm employment annotation): set `BEA_API_KEY` in the environment. Without it, the agriculture annotation does not appear but the rest of the dashboard works.

For local development, keys live in `.env` (already in `.gitignore`); loaded via `python-dotenv` at app/build entry points. For CI, set them as GitHub Actions secrets.

## Python Environment

- Python 3.14 (pinned via `.python-version` and `.github/workflows/update-data.yml`)
- venv at `.venv/` for local development
- Key packages: streamlit, plotly, pandas, requests, statsmodels, python-dotenv (see `requirements.txt`)
- `requirements-build.txt` is a slimmed-down subset omitting streamlit, used by the CI workflow

## Status

Initial West Texas adaptation, May 2026. The dashboard runs locally and the static build / GitHub Action / GitHub Pages publishing pipeline is inherited from the South Florida original and not yet re-tested end-to-end in the West Texas context.

## Change Log

**2026-05-27** — Initial adaptation from Bryan Cutsinger's South Florida Regional Economic Report. Swapped Palm Beach / Broward / Miami-Dade for Lubbock / Taylor / Howard. Replaced FAU color palette with a TTU-inspired scarlet-and-black palette (no institutional affiliation). Added BEA REA farm employment fetcher and annotation under the Workforce Composition treemap to close QCEW's coverage gap for self-employed farmers and ranchers. Renamed all `FAU_*` color constants to descriptive names (`SCARLET`, `BLACK`, etc.). Bumped Python pin from 3.11 to 3.14. Generalized the IRS migration fetcher to be state-agnostic.

### Inherited from South Florida original

**2026-05-15** — Added per-county KPI iframe embeds; treemap tiles now show share of private workforce alongside employment count.

**2026-05-13** — Repo cleanup for public/professional polish: added root README, LICENSE (MIT), `.python-version`; renamed `CLAUDE.md` to `docs/ARCHITECTURE.md`.

**2026-05-13** — Added iframe embed outputs via `build.py` and weekly auto-refresh workflow.
