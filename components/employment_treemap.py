"""
Workforce Composition — treemap of private employment by NAICS sector,
with year-selector buttons that switch the snapshot to the latest published
quarter of any year for which BLS QCEW data is available.

Implementation: one Plotly Treemap trace per year, all attached to the same
figure; only the newest trace is visible by default. Plotly's `updatemenus`
buttons toggle which trace is visible AND update the chart title to confirm
the active snapshot in plain text.
"""
from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from data.clean import get_treemap_snapshots
from data.constants import (
    INDUSTRY_DOMAIN_COLORS, CHARCOAL, LIGHT_GRAY, OLIVE, SAND, COUNTY_COLORS,
    USDA_CENSUS_OF_AG_2022,
)
from data.fetch_bea import latest_farm_income
from utils.narratives import source_citation, format_industry_list


METHODOLOGY_NOTE = (
    "Each rectangle is a 2-digit NAICS sector; size is total private employment "
    "in the displayed quarter. Use the buttons below the chart to view earlier "
    "years; the narrative reflects the most recent quarter. Colors group "
    "sectors into broad industry domains (matching the Industry Landscape "
    "chart). Sectors with suppressed BLS data and 'Unclassified' are excluded."
)


def _text_color_for(domain_color: str) -> str:
    """Pick contrast text color: dark gray on SAND (light), white otherwise."""
    return CHARCOAL if domain_color == SAND else "white"


def build_figure(snapshots: list) -> go.Figure:
    """Multi-trace treemap with year-selector updatemenus.

    `snapshots` is a list of (year, qtr, plot_data) tuples sorted ASCENDING
    by year. The LAST trace (newest year) starts visible; buttons render
    left-to-right with year-only labels (oldest on the left). The chart title
    above and the trace `name` retain the full "YYYY QQ" form for textual
    confirmation of the active snapshot.
    """
    fig = go.Figure()
    n = len(snapshots)
    default_idx = n - 1  # newest year is the last item in ascending order

    for idx, (year, qtr, plot_data) in enumerate(snapshots):
        domain_colors = [
            INDUSTRY_DOMAIN_COLORS.get(label, OLIVE)
            for label in plot_data["industry_label"]
        ]
        text_colors = [_text_color_for(c) for c in domain_colors]
        fig.add_trace(go.Treemap(
            labels=plot_data["industry_label"],
            parents=[""] * len(plot_data),
            values=plot_data["employment"],
            customdata=plot_data[["share", "qtrly_estabs", "avg_annual_wage"]].values,
            marker=dict(colors=domain_colors, line=dict(width=2, color="white")),
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>%{value:,.0f} (%{customdata[0]:.1%})",
            textfont=dict(
                family="Source Sans Pro, sans-serif",
                size=12,
                color=text_colors,
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Employment: %{value:,.0f}<br>"
                "Establishments: %{customdata[1]:,.0f}<br>"
                "Average salary: $%{customdata[2]:,.0f}<br>"
                "Share of private workforce: %{customdata[0]:.1%}"
                "<extra></extra>"
            ),
            sort=True,
            visible=(idx == default_idx),
            name=f"{year} Q{qtr}",
        ))

    # Year-only button labels (e.g., "2019" .. "2025"). Buttons silently
    # toggle which trace is visible; the button row is the only active-snapshot
    # cue (no above-chart title).
    buttons = [
        dict(
            label=f"{year}",
            method="update",
            args=[{"visible": [i == idx for i in range(n)]}],
        )
        for idx, (year, qtr, _) in enumerate(snapshots)
    ]

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=560,
        margin=dict(t=30, b=70, l=10, r=10),
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5, xanchor="center",
            y=-0.05, yanchor="top",
            pad=dict(t=8, b=4),
            bgcolor="white",
            bordercolor=LIGHT_GRAY,
            borderwidth=1,
            font=dict(color=CHARCOAL, size=11),
            active=default_idx,
            buttons=buttons,
        )],
    )
    return fig


def _format_dollars_millions(thousands: float) -> str:
    """Format a thousands-of-dollars value as $X.XM (or −$X.XM if negative)."""
    millions = thousands / 1000.0
    sign = "−" if millions < 0 else ""
    return f"{sign}${abs(millions):.1f}M"


def _ag_intro_markdown(
    latest_snapshot: pd.DataFrame,
    bea_latest: dict | None,
    county_name: str,
) -> str | None:
    """Short intro paragraph above the farm income time-series chart."""
    if not bea_latest:
        return None
    ag_rows = latest_snapshot[latest_snapshot["industry_label"] == "Agriculture"]
    qcew_str = (
        f"only **{int(ag_rows.iloc[0]['employment']):,}**" if not ag_rows.empty
        else "**no disclosable** (BLS-suppressed)"
    )
    dollars = _format_dollars_millions(bea_latest["value_thousands"])
    usda = USDA_CENSUS_OF_AG_2022.get(county_name)
    usda_clause = (
        (
            f" For headcount context, USDA's 2022 Census of Agriculture reports "
            f"**{usda['producers']:,} producers** operating **{usda['farms']:,} "
            f"farms** in this county across **{usda['land_acres']:,} acres**."
        )
        if usda else ""
    )
    return (
        f"**Farm proprietors' income** — net annual earnings of self-employed "
        f"farmers and ranchers, who fall entirely outside QCEW's UI-based "
        f"coverage. QCEW NAICS 11 captured {qcew_str} wage-and-salary jobs in "
        f"the latest quarter for this county.{usda_clause} The trend below "
        f"shows the proprietor side of the ag economy in dollars (BEA REA, "
        f"annual). Latest ({bea_latest['year']}): **{dollars}**."
    )


def build_farm_income_figure(bea_df: pd.DataFrame, county_name: str, county_color: str) -> go.Figure:
    """Annual time series of BEA farm proprietors' income for one county, $M."""
    sub = bea_df[bea_df["county_name"] == county_name].sort_values("year")
    fig = go.Figure()
    if sub.empty:
        return fig

    years = sub["year"].tolist()
    values_m = [v / 1000.0 for v in sub["value_thousands"].tolist()]
    hover_labels = [
        f"−${abs(v):.1f}M" if v < 0 else f"${v:.1f}M" for v in values_m
    ]

    # Zero reference line — important when income dips negative (Taylor, drought years).
    fig.add_hline(y=0, line=dict(color=LIGHT_GRAY, width=1, dash="dash"))

    fig.add_trace(go.Scatter(
        x=years,
        y=values_m,
        customdata=hover_labels,
        mode="lines+markers",
        line=dict(color=county_color, width=2.5),
        marker=dict(size=5, color=county_color),
        name="Farm proprietors' income",
        hovertemplate="%{x}<br>%{customdata}<extra></extra>",
    ))

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=300,
        margin=dict(t=20, b=60, l=80, r=20),
        showlegend=False,
        xaxis=dict(
            title=dict(text="Year", standoff=10),
            showgrid=False,
            showline=True, linecolor="black", linewidth=2, mirror=False,
            ticks="outside", tickcolor="black", ticklen=4,
        ),
        yaxis=dict(
            title=dict(text="Farm proprietors' income ($M)", standoff=10),
            tickprefix="$", ticksuffix="M",
            tickformat=",.0f",
            showgrid=False,
            showline=True, linecolor="black", linewidth=2, mirror=False,
            ticks="outside", tickcolor="black", ticklen=4,
            zeroline=False,
        ),
    )
    return fig


def render(df: pd.DataFrame, bea_farm_df: pd.DataFrame | None = None):
    """Workforce Composition treemap with year-selector buttons."""
    import streamlit as st

    st.header("Workforce Composition")

    snapshots = get_treemap_snapshots(df)
    if not snapshots:
        st.info("No disclosable employment data for this quarter.")
        return

    # Narrative reflects the most recent (default-visible) snapshot.
    year, qtr, latest = snapshots[-1]
    top3 = latest.head(3)
    items = [
        f"{r['industry_label']} ({r['share']*100:.1f}%)"
        for _, r in top3.iterrows()
    ]
    narrative = (
        f"In {year} Q{qtr}, the county's largest private-sector employers are "
        f"{format_industry_list(items)}."
    )

    st.markdown(narrative)
    fig = build_figure(snapshots)
    st.plotly_chart(fig, use_container_width=True)

    # Farm proprietors' income — closes QCEW's coverage gap for self-employed
    # farmers and ranchers. Annual time series (BEA REA CAINC5N line 71).
    if bea_farm_df is not None and not bea_farm_df.empty and not df.empty:
        county_name = str(df["county_name"].iloc[0])
        intro = _ag_intro_markdown(
            latest, latest_farm_income(bea_farm_df, county_name), county_name,
        )
        if intro:
            st.markdown(intro)
            color = COUNTY_COLORS.get(county_name, CHARCOAL)
            st.plotly_chart(
                build_farm_income_figure(bea_farm_df, county_name, color),
                use_container_width=True,
            )

    st.caption(source_citation("BLS QCEW", "https://www.bls.gov/cew/", "Quarterly"))
    if bea_farm_df is not None and not bea_farm_df.empty:
        st.caption(source_citation(
            "BEA REA CAINC5N (Farm proprietors' income)",
            "https://apps.bea.gov/regional/", "Annual",
        ))
        st.caption(source_citation(
            "USDA 2022 Census of Agriculture",
            "https://www.nass.usda.gov/AgCensus/",
            "Every 5 years",
        ))
    st.caption(f"_{METHODOLOGY_NOTE}_")
