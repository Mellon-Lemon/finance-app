from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import APP_CONFIG
from src.formatting import format_currency, format_number, format_percent, signed_currency
from src.ui import MetricCard, render_metric_grid, render_section_header, render_target_card


def render_dashboard(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    historie: pd.DataFrame,
    dividend_total: float,
) -> None:
    metrics = _calculate_metrics(portfolio, saldi, dividend_total)

    render_section_header("Dashboard", "KPI overzicht")
    _render_kpis(metrics)

    render_section_header("Targets", "Voortgang")
    _render_targets(metrics)

    render_section_header("Rendement", "Compacte analyse")
    _render_compact_visuals(metrics)

    render_section_header("Historie", "Equity curve")
    with st.container(border=True):
        st.plotly_chart(_build_history_chart(historie), width="stretch")


def _calculate_metrics(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    dividend_total: float,
) -> dict[str, float]:
    crypto_mask = portfolio["Categorie"] == "Crypto"
    stock_mask = ~crypto_mask
    btc_row = portfolio.loc[portfolio["Ticker"] == "BTC"].iloc[0]

    invested_value = float(portfolio["Waarde"].sum())
    invested_input = float(portfolio["Inleg"].sum())
    cash_total = float(saldi["Huidig Saldo"].sum())
    total_wealth = invested_value + cash_total
    crypto_value = float(portfolio.loc[crypto_mask, "Waarde"].sum())
    crypto_input = float(portfolio.loc[crypto_mask, "Inleg"].sum())
    stock_value = float(portfolio.loc[stock_mask, "Waarde"].sum())
    stock_input = float(portfolio.loc[stock_mask, "Inleg"].sum())
    total_profit = invested_value - invested_input
    crypto_profit = crypto_value - crypto_input
    stock_profit = stock_value - stock_input

    return {
        "total_wealth": total_wealth,
        "invested_value": invested_value,
        "invested_input": invested_input,
        "cash_total": cash_total,
        "crypto_value": crypto_value,
        "crypto_input": crypto_input,
        "stock_value": stock_value,
        "stock_input": stock_input,
        "total_profit": total_profit,
        "crypto_profit": crypto_profit,
        "stock_profit": stock_profit,
        "btc_amount": float(btc_row["Aantal"]),
        "btc_value": float(btc_row["Waarde"]),
        "dividend_total": float(dividend_total),
    }


def _render_kpis(metrics: dict[str, float]) -> None:
    cards = [
        MetricCard(
            "Totaal vermogen",
            format_currency(metrics["total_wealth"]),
            "Cash + belegd vermogen",
        ),
        MetricCard(
            "Totaal belegd vermogen",
            format_currency(metrics["invested_value"]),
            "Winst/verlies op portfolio",
            signed_currency(metrics["total_profit"]),
        ),
        MetricCard(
            "Crypto",
            format_currency(metrics["crypto_value"]),
            "Winst/verlies crypto",
            signed_currency(metrics["crypto_profit"]),
        ),
        MetricCard(
            "Aandelen",
            format_currency(metrics["stock_value"]),
            "Aandelen + ETF",
            signed_currency(metrics["stock_profit"]),
        ),
        MetricCard(
            "Dividend totaal",
            format_currency(metrics["dividend_total"]),
            "Ontvangen dividend in mockdata",
        ),
    ]
    render_metric_grid(cards)


def _render_targets(metrics: dict[str, float]) -> None:
    targets = [
        (
            "€100.000 totaal vermogen",
            format_currency(metrics["total_wealth"]),
            format_currency(APP_CONFIG.target_total_wealth),
            metrics["total_wealth"] / APP_CONFIG.target_total_wealth,
            "Cash en beleggingen samen.",
        ),
        (
            "€100.000 belegd vermogen",
            format_currency(metrics["invested_value"]),
            format_currency(APP_CONFIG.target_invested_value),
            metrics["invested_value"] / APP_CONFIG.target_invested_value,
            "Alleen huidige portfolio waarde.",
        ),
        (
            "0.5 BTC",
            f"{format_number(metrics['btc_amount'], 4)} BTC",
            f"{format_number(APP_CONFIG.target_btc_amount, 1)} BTC",
            metrics["btc_amount"] / APP_CONFIG.target_btc_amount,
            "Opbouw van de BTC positie.",
        ),
    ]

    columns = st.columns(3, gap="medium")
    for column, target in zip(columns, targets):
        with column:
            render_target_card(*target)


def _render_compact_visuals(metrics: dict[str, float]) -> None:
    left_col, right_col = st.columns(2, gap="medium")
    with left_col:
        with st.container(border=True):
            st.caption("BELEGD VS INGELEGD")
            st.plotly_chart(_build_invested_chart(metrics), width="stretch")
    with right_col:
        with st.container(border=True):
            st.caption("WINST / VERLIES")
            st.plotly_chart(_build_profit_chart(metrics), width="stretch")


def _build_invested_chart(metrics: dict[str, float]):
    data = pd.DataFrame(
        {
            "Type": ["Ingelegd vermogen", "Belegd vermogen"],
            "Waarde": [metrics["invested_input"], metrics["invested_value"]],
        }
    )
    fig = px.bar(
        data,
        x="Type",
        y="Waarde",
        color="Type",
        color_discrete_map={
            "Ingelegd vermogen": "#94a3b8",
            "Belegd vermogen": "#2563eb",
        },
    )
    fig.update_layout(
        height=230,
        showlegend=False,
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="€ ")
    return fig


def _build_profit_chart(metrics: dict[str, float]):
    data = pd.DataFrame(
        {
            "Type": ["Totaal", "Crypto", "Aandelen"],
            "Waarde": [
                metrics["total_profit"],
                metrics["crypto_profit"],
                metrics["stock_profit"],
            ],
        }
    )
    fig = px.bar(
        data,
        x="Type",
        y="Waarde",
        color="Waarde",
        color_continuous_scale=["#dc2626", "#94a3b8", "#16a34a"],
    )
    fig.update_layout(
        height=230,
        coloraxis_showscale=False,
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="€ ")
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
        height=310,
        hovermode="x unified",
        legend_title_text="",
        legend=dict(orientation="h", y=-0.24, x=0, xanchor="left"),
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False, tickformat="%b %y")
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="€ ")
    return fig
