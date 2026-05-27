# West Texas Regional Economic Report

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An interactive dashboard tracking employment, wages, firm formation, industry composition, and farm workforce across **Lubbock, Taylor, and Howard counties** — the three largest counties of Texas's 19th congressional district (TX-19), centered on Lubbock, Abilene, and Big Spring.

## What it is

A single-page Streamlit + Plotly application that ships in two forms: a fully interactive Streamlit app for local exploration, and a static HTML build published to GitHub Pages. The static build also produces standalone iframe-embeddable chart pages — the combined regional snapshot, one snapshot per county, and per-section chart pages — that can be embedded on any host page.

Data comes from:

- **BLS Quarterly Census of Employment and Wages (QCEW)** — county-level employment, wages, establishments, and industry composition
- **Federal Reserve Bank of St. Louis (FRED)** — county real GDP and unemployment rate
- **IRS Statistics of Income (SOI)** — county-to-county migration
- **BEA Regional Economic Accounts (CAINC5N)** — farm proprietors' income (net earnings of self-employed farmers and ranchers; closes QCEW's UI-payroll coverage gap)

## Quick start (developers)

```bash
git clone https://github.com/awsalter/west-texas-economic-report.git
cd west-texas-economic-report
python -m venv .venv
.venv\Scripts\activate          # PowerShell on Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```
FRED_API_KEY=your_fred_key_here
BEA_API_KEY=your_bea_key_here
```

Then run:

```bash
streamlit run app.py
```

First load fetches ~3 minutes of QCEW data and caches to `data/cache/`. Subsequent runs load from disk. Without API keys, FRED and BEA fields render as "—" but the rest of the dashboard works.

## Building the static embeds

```bash
python build.py
```

This writes `docs/index.html` and the chart embeds under `docs/embeds/`. The GitHub Actions workflow at `.github/workflows/update-data.yml` runs this command automatically every Monday at 1:00 AM Eastern and commits the refreshed HTML back to the repo.

## Project layout

```
app.py            Streamlit application (interactive dashboard)
build.py          Static HTML generator (produces docs/index.html + docs/embeds/*)
data/             QCEW, FRED, IRS SOI, BEA fetch + clean + analysis modules
components/       Plotly chart builders (one per dashboard section)
utils/            Number formatting + narrative text helpers
docs/             Published GitHub Pages output
.github/workflows Weekly auto-refresh workflow
```

Internal architecture details live in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Data refresh schedule

Every Monday at 1:00 AM Eastern, the GitHub Action regenerates all HTML files from fresh BLS QCEW, FRED, IRS SOI, and BEA data and commits the result. GitHub Pages serves the updated versions within ~10 minutes.

## Data sources

- **U.S. Bureau of Labor Statistics**, Quarterly Census of Employment and Wages (QCEW). https://www.bls.gov/cew/
- **Federal Reserve Bank of St. Louis**, FRED economic data — county real GDP and unemployment rate series. https://fred.stlouisfed.org/
- **Internal Revenue Service**, Statistics of Income (SOI) county-to-county migration data. https://www.irs.gov/statistics/soi-tax-stats-migration-data
- **U.S. Bureau of Economic Analysis**, Regional Economic Accounts, table CAINC5N (Personal income by major component and earnings by NAICS industry, line 71 — Farm proprietors' income). https://apps.bea.gov/regional/

## Credits

This dashboard is a derivative of the [South Florida Regional Economic Report](https://github.com/bryanpcutsinger/south-florida-economic-report) by Bryan Cutsinger (Florida Atlantic University). All chart components, data pipeline patterns, and the static-build approach were adapted from his MIT-licensed original. Significant modifications: replaced South Florida counties with West Texas counties, retuned color palette, and added BEA farm proprietors' income to address QCEW's underrepresentation of agricultural activity in this region.

## Author

Alexander W. Salter — Texas Tech University.
Personal site: https://www.awsalter.com

## License

MIT — see [`LICENSE`](LICENSE). Includes the original copyright by Bryan Cutsinger.
