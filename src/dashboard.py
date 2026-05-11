from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import APP_CONFIG
from src.formatting import format_currency, format_number, format_percent, format_quantity, signed_currency
from src.ui import (
    MetricCard,
    PerformanceMetric,
    render_metric_grid,
    render_primary_metric_card,
    render_section_header,
    render_target_card,
)


YTD_START_DATE = pd.Timestamp("2026-01-31")


def render_dashboard(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    historie: pd.DataFrame,
    dividend_total: float,
    price_quotes: dict[str, object],
) -> None:
    metrics = _calculate_metrics(portfolio, saldi, dividend_total)
    performance = _calculate_performance_metrics(metrics, historie)

    render_section_header("Vandaag", "Cockpit")
    _render_kpis(metrics, performance)
    _render_price_quotes(price_quotes)

    render_section_header("Doelen", "Voortgang")
    _render_targets(metrics, historie)


def _calculate_metrics(
    portfolio: pd.DataFrame,
    saldi: pd.DataFrame,
    dividend_total: float,
) -> dict[str, float]:
    crypto_mask = portfolio["Categorie"] == "Crypto"
    stock_mask = portfolio["Categorie"] == "Aandelen"
    btc_rows = portfolio.loc[portfolio["Ticker"] == "BTC"]
    btc_amount = float(btc_rows["Aantal"].iloc[0]) if not btc_rows.empty else 0.0
    btc_value = float(btc_rows["Waarde"].iloc[0]) if not btc_rows.empty else 0.0

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
        "btc_amount": btc_amount,
        "btc_value": btc_value,
        "dividend_total": float(dividend_total),
    }


def _render_kpis(
    metrics: dict[str, float],
    performance: dict[str, tuple[PerformanceMetric, ...]],
) -> None:
    render_primary_metric_card(
        "Totaal vermogen",
        format_currency(metrics["total_wealth"]),
        "Cash + actuele beleggingswaarde",
    )

    performance_cards = [
        MetricCard(
            "Belegd vermogen",
            format_currency(metrics["invested_value"]),
            "",
            signed_currency(metrics["total_profit"]),
            performance["invested"],
            "performance",
        ),
        MetricCard(
            "Cash",
            format_currency(metrics["cash_total"]),
            "",
            None,
            (),
            "standard",
        ),
        MetricCard(
            "Crypto",
            format_currency(metrics["crypto_value"]),
            "",
            signed_currency(metrics["crypto_profit"]),
            performance["crypto"],
            "performance",
        ),
        MetricCard(
            "Aandelen",
            format_currency(metrics["stock_value"]),
            "",
            signed_currency(metrics["stock_profit"]),
            performance["stocks"],
            "performance",
        ),
        MetricCard(
            "Dividend totaal",
            format_currency(metrics["dividend_total"], decimals=2),
            "",
            None,
            (),
            "standard",
        ),
    ]
    render_metric_grid(performance_cards, columns=2)


def _render_price_quotes(price_quotes: dict[str, object]) -> None:
    cards = [
        _build_price_quote_card(price_quotes.get("BTC", {}), decimals=0),
        _build_price_quote_card(price_quotes.get("TSWE", {}), decimals=2),
    ]
    render_metric_grid(cards, columns=2)


def _build_price_quote_card(quote: object, decimals: int) -> MetricCard:
    quote_data = quote if isinstance(quote, dict) else {"price": quote}
    label = str(quote_data.get("label") or quote_data.get("ticker") or "Koers")
    price = _safe_float(quote_data.get("price"))
    performance = quote_data.get("performance") if isinstance(quote_data.get("performance"), dict) else {}
    return MetricCard(
        label if label.endswith("koers") else f"{label} koers",
        format_currency(price, decimals=decimals),
        "",
        None,
        tuple(
            _price_performance_metric(period, performance.get(period))
            for period in ("24u", "7d", "30d", "YTD")
        ),
        "performance",
    )


def _price_performance_metric(label: str, entry: object) -> PerformanceMetric:
    if not isinstance(entry, dict) or entry.get("percentage") is None:
        return PerformanceMetric(label, "n.v.t.", "neutral")
    percentage = _safe_float(entry.get("percentage"))
    tone = str(entry.get("tone") or _value_tone(percentage))
    return PerformanceMetric(label, _signed_percent(percentage), tone)


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
            _build_performance_from_history("7d", historie, column, days_back=7),
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
    value = f"{signed_currency(delta)} / {_signed_percent(percentage)}"
    return PerformanceMetric(label, value, _value_tone(delta))


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


def _signed_percent(value: float) -> str:
    if value > 0:
        return f"+{format_percent(value, 1)}"
    return format_percent(value, 1)


def _value_tone(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def _safe_float(value: object) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if pd.isna(parsed) else parsed


def _render_targets(metrics: dict[str, float], historie: pd.DataFrame) -> None:
    total_wealth = metrics["total_wealth"]
    invested_value = metrics["invested_value"]
    btc_amount = metrics["btc_amount"]

    targets = [
        (
            "\u20ac100k totaal vermogen",
            format_currency(total_wealth),
            format_currency(APP_CONFIG.target_total_wealth),
            total_wealth / APP_CONFIG.target_total_wealth,
            "",
        ),
        (
            "\u20ac100k belegd vermogen",
            format_currency(invested_value),
            format_currency(APP_CONFIG.target_invested_value),
            invested_value / APP_CONFIG.target_invested_value,
            "",
        ),
        (
            "0.5 BTC",
            f"{format_quantity(btc_amount, 'BTC')} BTC",
            f"{format_number(APP_CONFIG.target_btc_amount, 1)} BTC",
            btc_amount / APP_CONFIG.target_btc_amount,
            "",
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
    fig.update_yaxes(title="", gridcolor="rgba(148, 163, 184, 0.18)", tickprefix="\u20ac ")
    return fig
