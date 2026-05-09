from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.formatting import format_currency
from src.ui import render_section_header


TRANSACTION_TYPES = ["Buy", "Sell", "Dividend", "Profit", "Initial"]
CURRENCIES = ["EUR", "USD"]
POSITION_TYPES = {"Buy", "Sell", "Initial"}


def render_transaction_form(portfolio: pd.DataFrame) -> None:
    render_section_header("Invoer", "Nieuwe transactie")

    ticker_options = sorted(portfolio["Ticker"].unique())
    with st.container(border=True):
        datum = st.date_input("Datum", value=date.today(), format="DD-MM-YYYY")
        ticker_col, type_col, currency_col = st.columns(3, gap="medium")
        with ticker_col:
            ticker = st.selectbox("Ticker", ticker_options)
        with type_col:
            transaction_type = st.selectbox("Type", TRANSACTION_TYPES)
        with currency_col:
            currency = st.selectbox("Valuta", CURRENCIES)

        amount, price, total = _render_transaction_amounts(transaction_type, currency)

    payload = {
        "Datum": datum.strftime("%d-%m-%Y"),
        "Ticker": ticker,
        "Type": transaction_type,
        "Aantal": amount,
        "Prijs per stuk": price,
        "Totaal": total,
        "Valuta": currency,
    }
    _render_transaction_preview(payload)


def _render_transaction_amounts(
    transaction_type: str,
    currency: str,
) -> tuple[float, float, float]:
    if transaction_type in POSITION_TYPES:
        amount_col, total_col = st.columns(2, gap="medium")
        with amount_col:
            amount = st.number_input(
                "Aantal",
                min_value=0.0,
                step=0.01,
                format="%.8f",
                key="tx_amount_position",
            )
        with total_col:
            total = st.number_input(
                "Totaal",
                min_value=0.0,
                step=25.0,
                format="%.2f",
                key="tx_total_position",
                help="Inclusief eventuele transactiekosten.",
            )

        price = _calculate_price_per_unit(amount, total)
        st.metric("Prijs per stuk", format_currency(price, currency, decimals=4))
        st.caption("Berekend uit Aantal en Totaal.")
        return float(amount), price, float(total)

    total = st.number_input(
        "Totaal",
        min_value=0.0,
        step=25.0,
        format="%.2f",
        key="tx_total_cashflow",
        help="Inclusief eventuele kosten.",
    )
    with st.expander("Optioneel"):
        amount = st.number_input(
            "Aantal",
            min_value=0.0,
            step=0.01,
            format="%.8f",
            key="tx_amount_cashflow",
        )
    price = _calculate_price_per_unit(amount, total)
    return float(amount), price, float(total)


def _calculate_price_per_unit(amount: float, total: float) -> float:
    if amount <= 0 or total <= 0:
        return 0.0
    return round(total / amount, 4)


def _render_transaction_preview(payload: dict[str, object]) -> None:
    render_section_header("Preview", "Controle")
    errors = _validate_transaction(payload)

    with st.container(border=True):
        if errors:
            st.warning("Controleer de invoer voordat je de preview bevestigt.")
            for error in errors:
                st.caption(error)
            return

        st.dataframe(pd.DataFrame([payload]), hide_index=True, width="stretch")
        confirmed = st.checkbox("Ik bevestig deze preview", key="tx_confirmed")
        if st.button("Bevestig preview", disabled=not confirmed):
            st.success("Preview bevestigd. Er is niets opgeslagen.")


def _validate_transaction(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    transaction_type = str(payload["Type"])
    amount = float(payload["Aantal"])
    total = float(payload["Totaal"])

    if not str(payload["Ticker"]).strip():
        errors.append("Ticker is verplicht.")
    if total <= 0:
        errors.append("Totaal moet groter zijn dan 0.")
    if transaction_type in POSITION_TYPES and amount <= 0:
        errors.append("Aantal moet groter zijn dan 0 voor Buy, Sell en Initial.")

    return errors
