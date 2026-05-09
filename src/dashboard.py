from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import APP_CONFIG
from src.formatting import format_currency, format_number, format_percent, signed_currency
from src.ui import (
    MetricCard,
    PerformanceMetric,
    render_metric_grid,
    render_section_header,
    render_target_card,
)


YTD_START_DATE = pd.Timestamp("2026-01-31")


def render_dashboard(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    historie: pd.DataFrame,
    dividend_total: float,
) -> None:
    metrics = _calculate_metrics(portfolio, saldi, dividend_total)
    performance = _calculate_performance_metrics(metrics, historie)

    render_section_header("Dashboard", "KPI overzicht")
    _render_kpis(metrics, performance)

    render_section_header("Targets", "Voortgang")
    _render_targets(metrics, historie)

    render_section_header("Historie", "Equity curve")
    with st.container(border=True):
        st.plotly_chart(_build_history_chart(historie), width="stretch")


def _calculate_metrics(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    dividend_total: float,
) -> dict[str, float]:
    crypto_mask = portfolio["Categorie"] == "Crypto"
    stock_mask = portfolio["Categorie"] == "Aandelen"
    btc_row = portfolio.loc[portfolio["Ticker"] == "BTC"].iloc[0]

    invested_value = float(portfolio["Waarde"].sum())
    invested_input = float(portfolio["Inleg"].sum())
    cash_total = float(saldi["Huidig Saldo"].sum())
    total_wealth = cash_total + invested_value
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


def _render_kpis(
    metrics: dict[str, float],
    performance: dict[str, tuple[PerformanceMetric, ...]],
) -> None:
    cards = [
        MetricCard(
            "Totaal vermogen",
            format_currency(metrics["total_wealth"]),
            "Cash + actuele beleggingswaarde",
        ),
        MetricCard(
            "Totaal belegd vermogen",
            format_currency(metrics["invested_value"]),
            "Winst/verlies op portfolio",
            signed_currency(metrics["total_profit"]),
            performance["invested"],
        ),
        MetricCard(
            "Crypto",
            format_currency(metrics["crypto_value"]),
            "Winst/verlies crypto",
            signed_currency(metrics["crypto_profit"]),
            performance["crypto"],
        ),
        MetricCard(
            "Aandelen",
            format_currency(metrics["stock_value"]),
            "Inclusief TSWE",
            signed_currency(metrics["stock_profit"]),
            performance["stocks"],
        ),
        MetricCard(
            "Dividend totaal",
            format_currency(metrics["dividend_total"], decimals=2),
            "Ontvangen dividend",
        ),
    ]
    render_metric_grid(cards)


def _calculate_performance_metrics(
    metrics: dict[str, float],
    historie: pd.DataFrame,
) -> dict[str, tuple[PerformanceMetric, ...]]:
    definitions = {
        "invested": ("Belegd Vermogen", metrics["invested_value"]),
        "crypto": ("Crypto W.", metrics["crypto_value"]),
        "stocks": ("DeGiro W.", metrics["stock_value"]),
    }

    return {
        key: (
            _build_performance_from_history("24u", historie, column, days_back=1),
            _build_performance_from_history("30d", historie, column, days_back=30),
            _build_performance_from_history("YTD", historie, column, reference_date=YTD_START_DATE),
        )
        for key, (column, current_value) in definitions.items()
    }


def _build_performance_from_history(
    label: str,
    historie: pd.DataFrame,
    column: str,
    days_back: int | None = None,
    reference_date: pd.Timestamp | None = None,
) -> PerformanceMetric:
    latest = _get_latest_history_point(historie, column)
    if latest is None:
        return PerformanceMetric(label, "n.v.t.")

    latest_date, latest_value = latest
    target_date = reference_date if reference_date is not None else latest_date - pd.Timedelta(days=days_back or 0)
    reference_value = _get_history_value_on_or_before(historie, column, target_date)
    if reference_value is None:
        return PerformanceMetric(label, "n.v.t.")

    delta = latest_value - reference_value
    percentage = delta / reference_value * 100 if reference_value else 0.0
    value = f"{signed_currency(delta)} ({format_percent(percentage, 1)})"
    return PerformanceMetric(label, value)


def _get_latest_history_point(
    historie: pd.DataFrame,
    column: str,
) -> tuple[pd.Timestamp, float] | None:
    if historie.empty or column not in historie.columns:
        return None
    sorted_history = historie.dropna(subset=["Datum", column]).sort_values("Datum")
    if sorted_history.empty:
        return None
    row = sorted_history.iloc[-1]
    return pd.Timestamp(row["Datum"]), float(row[column])


def _get_history_value_on_or_before(
    historie: pd.DataFrame,
    column: str,
    target_date: pd.Timestamp,
) -> float | None:
    if historie.empty or column not in historie.columns:
        return None
    sorted_history = historie.dropna(subset=["Datum", column]).sort_values("Datum")
    earlier_snapshots = sorted_history.loc[sorted_history["Datum"] <= target_date]
    if earlier_snapshots.empty:
        return None
    return float(earlier_snapshots[column].iloc[-1])


def _render_targets(metrics: dict[str, float], historie: pd.DataFrame) -> None:
    total_wealth = _get_latest_history_value(historie, "Totaal") or metrics["total_wealth"]
    invested_value = (
        _get_latest_history_value(historie, "Belegd Vermogen") or metrics["invested_value"]
    )
    btc_amount = _get_latest_history_value(historie, "BTC Aant.") or metrics["btc_amount"]

    targets = [
        (
            "EUR 100.000 totaal vermogen",
            format_currency(total_wealth),
            format_currency(APP_CONFIG.target_total_wealth),
            total_wealth / APP_CONFIG.target_total_wealth,
            "Cash en beleggingen samen.",
        ),
        (
            "EUR 100.000 belegd vermogen",
            format_currency(invested_value),
            format_currency(APP_CONFIG.target_invested_value),
            invested_value / APP_CONFIG.target_invested_value,
            "Alleen actuele portfolio waarde.",
        ),
        (
            "0.5 BTC",
            f"{format_number(btc_amount, 8)} BTC",
            f"{format_number(APP_CONFIG.target_btc_amount, 1)} BTC",
            btc_amount / APP_CONFIG.target_btc_amount,
            "Opbouw van de BTC positie.",
        ),
    ]

    columns = st.columns(3, gap="medium")
    for column, target in zip(columns, targets):
        with column:
            render_target_card(*target)


def _get_latest_history_value(historie: pd.DataFrame, column: str) -> float | None:
    latest = _get_latest_history_point(historie, column)
    return None if latest is None else latest[1]


def _build_history_chart(historie: pd.DataFrame):
    if historie.empty:
        return px.line(pd.DataFrame({"Datum": [], "Waarde": [], "Reeks": []}))

    chart_data = historie.rename(
        columns={
            "Crypto W.": "Crypto",
            "DeGiro W.": "Aandelen",
            "Belegd Vermogen": "Belegd",
        }
    )
    long_data = chart_data.melt(
        id_vars="Datum",
        value_vars=[
            column
            for column in ["Totaal", "Belegd", "Crypto", "Aandelen"]
            if column in chart_data.columns
        ],
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
        height=280,
        hovermode="x unified",
        legend_title_text="",
        legend=dict(orientation="h", y=-0.25, x=0, xanchor="left"),
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title="", showgrid=False, tickformat="%b %y")
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="EUR ")
    return fig
