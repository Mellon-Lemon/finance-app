from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from src.formatting import (
    format_currency_eur,
    format_percent,
    format_profit,
    format_quantity,
    format_quantity_with_unit,
)
from src.ui import render_section_header


def render_portfolio_table(portfolio: pd.DataFrame, historie: pd.DataFrame) -> None:
    portfolio_view = _prepare_portfolio(portfolio)
    category_summary = _build_category_summary(portfolio_view)

    render_section_header("Holdings", "Portfolio tabel")
    _render_holdings_table(portfolio_view)

    render_section_header("Detail", "Portfolio analyse")
    _render_category_visuals(category_summary)
    _render_history_visuals(category_summary, historie)


def _prepare_portfolio(portfolio: pd.DataFrame) -> pd.DataFrame:
    prepared = portfolio.copy()
    prepared["Inleg"] = prepared["Waarde"] - prepared["Winst"]
    return prepared


def _build_category_summary(portfolio: pd.DataFrame) -> pd.DataFrame:
    return (
        portfolio.groupby("Categorie", as_index=False)
        .agg(
            Waarde=("Waarde", "sum"),
            Ingelegd=("Inleg", "sum"),
            Winst=("Winst", "sum"),
        )
        .sort_values("Waarde", ascending=False)
    )


def _render_holdings_table(portfolio_view: pd.DataFrame) -> None:
    with st.container(border=True):
        filter_col, view_col = st.columns([1, 0.7], gap="medium")
        with filter_col:
            categories = ["Alles", "Crypto", "Aandelen"]
            selected_category = st.radio(
                "Categorie",
                categories,
                horizontal=True,
                key="portfolio_category_filter",
            )
        with view_col:
            compact_view = st.toggle("Compacte weergave", value=True, key="portfolio_compact_view")

        filtered = (
            portfolio_view
            if selected_category == "Alles"
            else portfolio_view.loc[portfolio_view["Categorie"] == selected_category]
        )

        if compact_view:
            _render_holdings_cards(filtered)
            return

        table = _format_holdings_table(filtered)
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Aantal": st.column_config.TextColumn("Aantal", width="medium"),
                "Inleg": st.column_config.TextColumn("Inleg", width="medium"),
                "Waarde": st.column_config.TextColumn("Waarde", width="medium"),
                "Winst": st.column_config.TextColumn("Winst", width="medium"),
                "ROI": st.column_config.TextColumn("ROI", width="small"),
            },
        )


def _format_holdings_table(portfolio_view: pd.DataFrame) -> pd.DataFrame:
    table = portfolio_view[
        [
            "Ticker",
            "Aantal",
            "Inleg",
            "Waarde",
            "Winst",
            "ROI %",
        ]
    ].copy()
    table["Aantal"] = [
        format_quantity(amount, ticker)
        for amount, ticker in zip(table["Aantal"], table["Ticker"])
    ]
    table["Inleg"] = table["Inleg"].map(format_currency_eur)
    table["Waarde"] = table["Waarde"].map(format_currency_eur)
    table["Winst"] = table["Winst"].map(format_profit)
    table["ROI %"] = table["ROI %"].map(lambda value: format_percent(float(value), 1))
    return table.rename(columns={"ROI %": "ROI"})


def _render_holdings_cards(portfolio_view: pd.DataFrame) -> None:
    for _, row in portfolio_view.iterrows():
        ticker = str(row["Ticker"])
        profit = float(row["Winst"])
        tone = "positive" if profit > 0 else "neutral"
        if profit < 0:
            tone = "negative"
        st.markdown(
            (
                '<div class="fc-holding-card">'
                '<div class="fc-holding-head">'
                f'<strong>{escape(ticker)}</strong>'
                f'<span>{escape(format_quantity_with_unit(float(row["Aantal"]), ticker))}</span>'
                '</div>'
                '<div class="fc-holding-grid">'
                f'<span>Inleg</span><strong>{escape(format_currency_eur(float(row["Inleg"])))}</strong>'
                f'<span>Waarde</span><strong>{escape(format_currency_eur(float(row["Waarde"])))}</strong>'
                f'<span>Winst</span><strong class="fc-holding-profit--{tone}">{escape(format_profit(float(row["Winst"])))}</strong>'
                f'<span>ROI</span><strong>{escape(format_percent(float(row["ROI %"]), 1))}</strong>'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )


def _render_category_visuals(summary: pd.DataFrame) -> None:
    value_col, input_col = st.columns([1, 1], gap="medium")
    with value_col:
        with st.container(border=True):
            st.caption("WAARDE PER CATEGORIE")
            st.plotly_chart(_build_value_distribution(summary), width="stretch")
    with input_col:
        with st.container(border=True):
            st.caption("INLEG")
            st.plotly_chart(_build_invested_by_category(summary), width="stretch")

    with st.container(border=True):
        st.caption("WINST / VERLIES PER CATEGORIE")
        st.plotly_chart(_build_profit_by_category(summary), width="stretch")


def _render_history_visuals(summary: pd.DataFrame, historie: pd.DataFrame) -> None:
    invested_col, history_col = st.columns([1, 1], gap="medium")
    with invested_col:
        with st.container(border=True):
            st.caption("BELEGD VS INLEG")
            st.plotly_chart(_build_invested_total(summary), width="stretch")
    with history_col:
        with st.container(border=True):
            st.caption("EQUITY CURVE")
            st.plotly_chart(_build_history_chart(historie), width="stretch")


def _build_value_distribution(summary: pd.DataFrame):
    fig = px.pie(
        summary,
        names="Categorie",
        values="Waarde",
        hole=0.58,
        color="Categorie",
        color_discrete_map={
            "Crypto": "#d97706",
            "Aandelen": "#2563eb",
        },
    )
    fig.update_layout(
        height=260,
        legend_title_text="",
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _build_invested_by_category(summary: pd.DataFrame):
    fig = px.bar(
        summary,
        x="Categorie",
        y="Ingelegd",
        color="Categorie",
        color_discrete_map={
            "Crypto": "#d97706",
            "Aandelen": "#2563eb",
        },
    )
    _apply_bar_layout(fig)
    return fig


def _build_profit_by_category(summary: pd.DataFrame):
    fig = px.bar(
        summary,
        x="Categorie",
        y="Winst",
        color="Winst",
        color_continuous_scale=["#dc2626", "#94a3b8", "#16a34a"],
    )
    fig.update_layout(coloraxis_showscale=False)
    _apply_bar_layout(fig)
    return fig


def _build_invested_total(summary: pd.DataFrame):
    totals = pd.DataFrame(
        {
            "Type": ["Inleg", "Belegd vermogen"],
            "Waarde": [summary["Ingelegd"].sum(), summary["Waarde"].sum()],
        }
    )
    fig = px.bar(
        totals,
        x="Type",
        y="Waarde",
        color="Type",
        color_discrete_map={
            "Inleg": "#94a3b8",
            "Belegd vermogen": "#2563eb",
        },
    )
    _apply_bar_layout(fig)
    return fig


def _build_history_chart(historie: pd.DataFrame):
    chart_data = historie.rename(
        columns={
            "Crypto W.": "Crypto",
            "DeGiro W.": "Aandelen",
            "Belegd Vermogen": "Belegd",
        }
    )
    long_data = chart_data.melt(
        id_vars="Datum",
        value_vars=["Totaal", "Belegd", "Crypto", "Aandelen"],
        var_name="Reeks",
        value_name="Waarde",
    )

    fig = px.line(
        long_data,
        x="Datum",
        y="Waarde",
        color="Reeks",
        color_discrete_map={
            "Totaal": "#16a34a",
            "Belegd": "#2563eb",
            "Crypto": "#d97706",
            "Aandelen": "#64748b",
        },
    )
    fig.update_traces(line_width=2.5)
    fig.update_layout(
        height=260,
        hovermode="x unified",
        legend_title_text="",
        legend=dict(orientation="h", y=-0.28, x=0, xanchor="left"),
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False, tickformat="%b %y")
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="€ ")
    return fig


def _apply_bar_layout(fig) -> None:
    fig.update_layout(
        height=260,
        showlegend=False,
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="€ ")
