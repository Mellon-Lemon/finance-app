from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import APP_CONFIG
from src.formatting import format_currency, format_number, format_percent
from src.ui import MetricCard, render_metric_grid, render_section_header


def render_dashboard(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    historie: pd.DataFrame,
) -> None:
    metrics = _calculate_metrics(portfolio, saldi)
    _render_summary(metrics)

    render_section_header("Verdeling", "Portfolio overzicht")
    _render_portfolio_metrics(metrics)

    render_section_header("Historie", "Equity curve")
    with st.container(border=True):
        st.plotly_chart(_build_history_chart(historie), use_container_width=True)


def _calculate_metrics(portfolio: pd.DataFrame, saldi: pd.DataFrame) -> dict[str, float]:
    invested_value = float(portfolio["Waarde"].sum())
    cash_total = float(saldi["Huidig Saldo"].sum())
    total_wealth = invested_value + cash_total
    crypto_value = float(portfolio.loc[portfolio["Categorie"] == "Crypto", "Waarde"].sum())
    stock_value = invested_value - crypto_value
    total_profit = float(portfolio["Winst"].sum())
    btc_row = portfolio.loc[portfolio["Ticker"] == "BTC"].iloc[0]
    target_progress = total_wealth / APP_CONFIG.target_wealth

    return {
        "total_wealth": total_wealth,
        "invested_value": invested_value,
        "cash_total": cash_total,
        "crypto_value": crypto_value,
        "stock_value": stock_value,
        "total_profit": total_profit,
        "btc_amount": float(btc_row["Aantal"]),
        "btc_value": float(btc_row["Waarde"]),
        "target": APP_CONFIG.target_wealth,
        "target_progress": target_progress,
    }


def _render_summary(metrics: dict[str, float]) -> None:
    profit_delta = f"{format_currency(metrics['total_profit'])} winst"
    capped_progress = max(0.0, min(metrics["target_progress"], 1.0))

    summary_col, target_col = st.columns([1.45, 1], gap="medium")
    with summary_col:
        with st.container(border=True):
            st.metric(
                label="Totaal vermogen",
                value=format_currency(metrics["total_wealth"]),
                delta=profit_delta,
            )
            detail_cols = st.columns(2, gap="medium")
            with detail_cols[0]:
                st.caption("Belegd vermogen")
                st.write(format_currency(metrics["invested_value"]))
            with detail_cols[1]:
                st.caption("Cash totaal")
                st.write(format_currency(metrics["cash_total"]))

    with target_col:
        with st.container(border=True):
            st.metric(
                label="Target progressie",
                value=format_percent(metrics["target_progress"] * 100, 0),
            )
            st.progress(
                capped_progress,
                text=f"Doel {format_currency(metrics['target'])}",
            )
            st.caption("Richting het mockdoel voor totaal vermogen.")


def _render_portfolio_metrics(metrics: dict[str, float]) -> None:
    cards = [
        MetricCard("Belegd vermogen", format_currency(metrics["invested_value"]), "Portfolio waarde"),
        MetricCard("Cash totaal", format_currency(metrics["cash_total"]), "Saldi samen"),
        MetricCard("Crypto waarde", format_currency(metrics["crypto_value"]), "BTC positie"),
        MetricCard("Aandelen waarde", format_currency(metrics["stock_value"]), "Aandelen + ETF"),
        MetricCard(
            "Winst totaal",
            format_currency(metrics["total_profit"]),
            "Mock portfolio resultaat",
        ),
        MetricCard(
            "BTC positie",
            f"{format_number(metrics['btc_amount'], 4)} BTC",
            format_currency(metrics["btc_value"]),
        ),
    ]
    render_metric_grid(cards)


def _build_history_chart(historie: pd.DataFrame):
    chart_data = historie.rename(
        columns={
            "Crypto W.": "Crypto waarde",
            "DeGiro W.": "Aandelen waarde",
        }
    )
    long_data = chart_data.melt(
        id_vars="Datum",
        value_vars=["Totaal", "Belegd Vermogen", "Crypto waarde", "Aandelen waarde"],
        var_name="Reeks",
        value_name="Waarde",
    )

    fig = px.line(
        long_data,
        x="Datum",
        y="Waarde",
        color="Reeks",
        markers=True,
        color_discrete_map={
            "Totaal": "#22c55e",
            "Belegd Vermogen": "#38bdf8",
            "Crypto waarde": "#f59e0b",
            "Aandelen waarde": "#a78bfa",
        },
    )
    fig.update_traces(line_width=3, marker_size=6)
    fig.update_layout(
        height=350,
        hovermode="x unified",
        legend_title_text="",
        legend=dict(orientation="h", y=-0.2, x=0, xanchor="left"),
        margin=dict(l=4, r=4, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, tickformat="%b %y")
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="EUR ")
    return fig
