"""
Methodology content for the West Texas Regional Economic Report.

A plain-language guide to every data series in the dashboard — what each
measure is, why it matters, and where it comes from. Modeled on the
methodology tab of the awsalter/texas-trends dashboard.

Content lives as raw HTML so it can be used identically by the Streamlit
app (via st.markdown(unsafe_allow_html=True)) and by the static build.

NOTE: lines must NOT be indented. Streamlit's markdown engine treats lines
with 4+ leading spaces as code blocks even inside an HTML block, so the
content below is intentionally left-aligned.
"""
from __future__ import annotations


def methodology_html() -> str:
    """Return the full Methodology section as HTML (no leading whitespace)."""
    return """
<div class="methodology-content">
<div class="section-header">
<h2>Methodology</h2>
<p class="section-desc">A plain-language guide to the data series used in this dashboard &mdash; what each measure is, why it matters, and where it comes from.</p>
</div>
<div class="methodology-section">
<h3>Geographic Coverage</h3>
<div class="methodology-item">
<h4>Why Lubbock, Taylor, and Howard counties?</h4>
<p>These are the three most populous counties of Texas's 19th congressional district (TX-19). Lubbock County (~316,000 people) anchors the South Plains region. Taylor County (~146,000) contains Abilene. Howard County (~37,000) contains Big Spring and is the third-largest county in TX-19. The remaining 28 counties of the district are smaller and predominantly rural &mdash; only a handful (Hale, Gaines, Hockley) exceed 20,000 in population, and BLS QCEW often suppresses industry-level employment for the smaller counties due to disclosure rules. Focusing on the three urban-anchor counties gives the cleanest data while still spanning the district's main economic centers.</p>
</div>
</div>
<div class="methodology-section">
<h3>Regional Snapshot</h3>
<div class="methodology-item">
<h4>Total Employment</h4>
<p>The number of jobs reported by employers covered under the unemployment insurance (UI) system. This includes essentially every job <em>outside</em> small-scale agriculture, private households, and self-employment. The figure is the average employment count in the third month of the quarter. Year-over-year (YoY) change compares the latest quarter to the same quarter one year prior.</p>
<p><strong>Source:</strong> U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages (QCEW). Updated quarterly, with roughly a six-month publication lag.</p>
</div>
<div class="methodology-item">
<h4>Establishments</h4>
<p>A count of distinct business locations covered by UI. A single firm operating multiple offices, branches, or stores in the county counts each as a separate establishment. This is a different unit of analysis than &ldquo;number of firms.&rdquo;</p>
<p><strong>Source:</strong> BLS QCEW.</p>
</div>
<div class="methodology-item">
<h4>Average Salary</h4>
<p>Total quarterly wages divided by average employment, annualized by multiplying the weekly figure by 52. Covers all workers in the QCEW universe. Because QCEW excludes the self-employed, this measure reflects W-2 payroll workers only.</p>
<p><strong>Source:</strong> BLS QCEW.</p>
</div>
<div class="methodology-item">
<h4>Real GDP</h4>
<p>County-level real gross domestic product in chained 2017 dollars &mdash; BEA's measure of total economic output for the county, with inflation removed so figures across years are comparable. BEA publishes county GDP annually each December, so the figure lags by roughly a year.</p>
<p><em>Note on cross-county comparison:</em> Howard County's real GDP is large relative to its small population because Big Spring sits at the eastern edge of the Permian Basin. Capital-intensive oil and gas extraction, refining, and pipeline activity produce extraordinary output per worker &mdash; Howard's per-capita GDP runs roughly five times that of Lubbock or Taylor. By contrast, Lubbock's economy is led by healthcare, higher education, and agriculture services, while Taylor's leans on services, higher education, and the Dyess Air Force Base. Differences in industry composition drive the per-capita GDP spread far more than differences in population do.</p>
<p><strong>Source:</strong> U.S. Bureau of Economic Analysis (BEA), Regional Economic Accounts, retrieved via FRED.</p>
</div>
<div class="methodology-item">
<h4>Unemployment Rate</h4>
<p>The share of the labor force that is jobless and actively looking for work. The county-level series shown here is monthly and <em>not</em> seasonally adjusted &mdash; BLS does not publish seasonally adjusted unemployment at the county level. The YoY change is shown in percentage points (pp), with color inverted so that <em>rising</em> unemployment shows as red and <em>falling</em> unemployment shows as green (lower-is-better).</p>
<p><strong>Source:</strong> BLS Local Area Unemployment Statistics (LAUS), retrieved via FRED. Updated monthly.</p>
</div>
<div class="methodology-item">
<h4>Net Migration</h4>
<p>The net change in tax-filer exemptions (a proxy for people) between two consecutive tax filing years. Positive values indicate net inflows; negative values indicate net outflows. Inclusive of both U.S.-domestic and foreign origins/destinations, following the convention used in most regional economic studies. The year label refers to the destination filing year.</p>
<p><strong>Source:</strong> Internal Revenue Service, Statistics of Income (SOI) county-to-county migration data. Updated annually.</p>
</div>
</div>
<div class="methodology-section">
<h3>Employment &amp; Salary Trends</h3>
<div class="methodology-item">
<h4>STL Trend Decomposition</h4>
<p>The chart shows a smoothed trend line derived from the raw quarterly employment (and average salary) series, with seasonal swings removed. The decomposition uses STL (&ldquo;Seasonal-Trend decomposition using Loess&rdquo;) with a four-quarter seasonal period and a robust fit to dampen outliers. BLS does not publish seasonally adjusted QCEW series at the county level &mdash; this trend is a custom estimate. For the salary chart, the input is log-transformed because wage growth is multiplicative rather than additive.</p>
<p><strong>Source:</strong> BLS QCEW. STL implementation via Python <code>statsmodels</code>.</p>
</div>
<div class="methodology-item">
<h4>Linear Projection</h4>
<p>The dotted segment extends the trend forward to the current calendar quarter using a linear fit through the last four trend points. QCEW data publishes with a ~6-month lag, so the projection bridges the gap between the latest available quarter and the present. The projection horizon shrinks automatically as BLS releases newer data.</p>
<p><strong>Source:</strong> Derived internally from the STL trend.</p>
</div>
</div>
<div class="methodology-section">
<h3>Workforce Composition</h3>
<div class="methodology-item">
<h4>Treemap (QCEW 2-digit NAICS)</h4>
<p>Each rectangle is a 2-digit NAICS industry sector; the area is proportional to total private (own_code=5) employment in the snapshot quarter. Tile color groups the sector into a broader industry domain (Goods-producing, Trade &amp; Logistics, etc.). Sectors with BLS-suppressed data and the &ldquo;Unclassified&rdquo; bucket are excluded. The year-selector buttons below the chart let you view earlier snapshots.</p>
<p><strong>Source:</strong> BLS QCEW.</p>
</div>
<div class="methodology-item">
<h4>Farm Proprietors' Income (BEA)</h4>
<p>Net annual earnings of self-employed farmers and ranchers in the county, reported by BEA in thousands of dollars (shown here in millions). The figure can be <em>negative</em> when operating costs exceed receipts &mdash; common in drought years or when commodity prices crash. This series exists precisely to capture the slice of agricultural activity that QCEW misses: QCEW's UI-payroll coverage excludes proprietors entirely. (BEA retired the older CAEMP25N farm-employment-count table from their API after a 2024 restructure, so we use the income series in its place.)</p>
<p><strong>Source:</strong> BEA Regional Economic Accounts, table CAINC5N line 71. Updated annually.</p>
</div>
<div class="methodology-item">
<h4>USDA Census of Agriculture (2022 headcounts)</h4>
<p>Number of farms, number of producers, and total land in farms for the county. &ldquo;Producers&rdquo; is the modern USDA term for what was historically called &ldquo;farm operators&rdquo; &mdash; anyone making management decisions on the farm, which is typically two to three people per farm (the owner plus partners or family members). The Census of Agriculture is conducted every five years; the most recent (2022) was published in February 2024, with the next expected in 2029.</p>
<p><strong>Source:</strong> USDA National Agricultural Statistics Service (NASS), 2022 Census of Agriculture.</p>
</div>
</div>
<div class="methodology-section">
<h3>Industry Landscape</h3>
<div class="methodology-item">
<h4>Growth Quadrant Scatter</h4>
<p>For each 2-digit NAICS industry, the chart plots year-over-year employment growth (x-axis) against year-over-year wage growth (y-axis). Bubble size is proportional to total employment in that sector. Bubble color groups the sector into a broad industry domain. The four quadrants tell distinct stories:</p>
<p><strong>NE:</strong> growing in both jobs and pay &mdash; the local strengths.<br><strong>NW:</strong> wages rising while jobs shrinking &mdash; productivity, automation, or downsizing pressure.<br><strong>SW:</strong> declining on both &mdash; sectors in distress.<br><strong>SE:</strong> jobs growing while wages falling &mdash; often hospitality and services in expansion mode.</p>
<p><strong>Source:</strong> BLS QCEW. Growth rates compare the latest quarter to the same quarter one year prior.</p>
</div>
</div>
<div class="methodology-section">
<h3>Firm Openings &amp; Closings</h3>
<div class="methodology-item">
<h4>Quarterly Establishment Churn</h4>
<p>The black bars sum the quarter-over-quarter establishment additions across all industries that grew in that quarter; the red bars sum the losses across industries that shrank. The dark overlay line shows the county's total private-sector (own_code=5) net establishment change as published by BLS, which does not equal the sum of the bars because BLS suppresses small-cell industries from the per-sector view.</p>
<p><strong>Source:</strong> BLS QCEW.</p>
</div>
<div class="methodology-item">
<h4>U.S. Benchmark Line</h4>
<p>The dashed tan line shows the U.S. national private-sector quarter-over-quarter establishment growth rate, <em>rescaled</em> to the county's establishment base. This converts a national percentage change into an apples-to-apples count: &ldquo;how many establishments would this county have added if it had grown at the national rate this quarter?&rdquo; Trailing quarters with no benchmark mean the national figure hasn't been published yet.</p>
<p><strong>Source:</strong> Derived from U.S. QCEW national aggregate (area code US000).</p>
</div>
<div class="methodology-item">
<h4>Q1 Pattern Caveat</h4>
<p>Q1 typically shows a large negative establishment-count pattern across <em>all</em> counties. This is an artifact of QCEW's year-end reporting cycle: businesses that closed during Q4 of the prior year are formally removed from the register in Q1. The chart is therefore not a clean measure of &ldquo;gross firm openings and closings&rdquo; &mdash; BLS does not publish that at the county level.</p>
</div>
</div>
<div class="methodology-section">
<h3>Data Refresh</h3>
<div class="methodology-item">
<h4>Update cadence</h4>
<p>The dashboard is regenerated automatically every Monday at 1:00 AM Eastern via a GitHub Actions workflow. The action pulls fresh data from BLS QCEW, FRED, IRS SOI, and BEA, regenerates the static HTML pages, and pushes the result to GitHub Pages. New QCEW quarters appear about six months after the quarter ends; FRED unemployment is monthly; IRS migration and BEA income are annual.</p>
</div>
</div>
</div>
"""
