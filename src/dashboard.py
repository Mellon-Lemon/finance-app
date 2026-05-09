from __future__ import annotations

import pandas as pd
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
MOCK_24H_CHANGES = {
    "invested": 128.45,
    "crypto": 210.30,
    "stocks": -81.85,
}


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
    _render_targets(metrics)


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
            _build_performance_metric(
                "24u",
                MOCK_24H_CHANGES[key],
                current_value - MOCK_24H_CHANGES[key],
            ),
            _build_performance_metric(
                "30d",
                current_value - _get_previous_snapshot_value(historie, column),
                _get_previous_snapshot_value(historie, column),
            ),
            _build_performance_metric(
                "YTD",
                current_value - _get_ytd_start_value(historie, column),
                _get_ytd_start_value(historie, column),
            ),
        )
        for key, (column, current_value) in definitions.items()
    }


def _build_performance_metric(
    label: str,
    delta: float,
    reference_value: float,
) -> PerformanceMetric:
    percentage = delta / reference_value * 100 if reference_value else 0.0
    value = f"{signed_currency(delta)} ({format_percent(percentage, 1)})"
    return PerformanceMetric(label, value)


def _get_previous_snapshot_value(historie: pd.DataFrame, column: str) -> float:
    sorted_history = historie.sort_values("Datum")
    if len(sorted_history) < 2:
        return float(sorted_history[column].iloc[-1])
    return float(sorted_history[column].iloc[-2])


def _get_ytd_start_value(historie: pd.DataFrame, column: str) -> float:
    sorted_history = historie.sort_values("Datum")
    exact_match = sorted_history.loc[sorted_history["Datum"] == YTD_START_DATE]
    if not exact_match.empty:
        return float(exact_match[column].iloc[0])

    earlier_snapshots = sorted_history.loc[sorted_history["Datum"] <= YTD_START_DATE]
    if not earlier_snapshots.empty:
        return float(earlier_snapshots[column].iloc[-1])

    return float(sorted_history[column].iloc[0])


def _render_targets(metrics: dict[str, float]) -> None:
    targets = [
        (
            "EUR 100.000 totaal vermogen",
            format_currency(metrics["total_wealth"]),
            format_currency(APP_CONFIG.target_total_wealth),
            metrics["total_wealth"] / APP_CONFIG.target_total_wealth,
            "Cash en beleggingen samen.",
        ),
        (
            "EUR 100.000 belegd vermogen",
            format_currency(metrics["invested_value"]),
            format_currency(APP_CONFIG.target_invested_value),
            metrics["invested_value"] / APP_CONFIG.target_invested_value,
            "Alleen actuele portfolio waarde.",
        ),
        (
            "0.5 BTC",
            f"{format_number(metrics['btc_amount'], 8)} BTC",
            f"{format_number(APP_CONFIG.target_btc_amount, 1)} BTC",
            metrics["btc_amount"] / APP_CONFIG.target_btc_amount,
            "Opbouw van de BTC positie.",
        ),
    ]

    columns = st.columns(3, gap="medium")
    for column, target in zip(columns, targets):
        with column:
            render_target_card(*target)
