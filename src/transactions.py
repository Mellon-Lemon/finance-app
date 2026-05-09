from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui import render_section_header


TRANSACTION_TYPES = ["Buy", "Sell", "Dividend", "Profit", "Initial"]
CURRENCIES = ["EUR", "USD"]


def render_transaction_form(portfolio: pd.DataFrame) -> None:
    render_section_header("Invoer", "Nieuwe transactie")
    _ensure_transaction_state()

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

        amount_col, price_col, total_col = st.columns(3, gap="medium")
        with amount_col:
            st.number_input(
                "Aantal",
                min_value=0.0,
                step=0.01,
                format="%.8f",
                key="tx_amount",
                on_change=_recalculate_from_amount,
            )
        with price_col:
            st.number_input(
                "Prijs per stuk",
                min_value=0.0,
                step=1.0,
                format="%.4f",
                key="tx_price",
                on_change=_recalculate_from_price,
            )
        with total_col:
            st.number_input(
                "Totaal",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="tx_total",
                on_change=_recalculate_from_total,
            )

    payload = {
        "Datum": datum.strftime("%d-%m-%Y"),
        "Ticker": ticker,
        "Type": transaction_type,
        "Aantal": float(st.session_state.tx_amount),
        "Prijs per stuk": float(st.session_state.tx_price),
        "Totaal": float(st.session_state.tx_total),
        "Valuta": currency,
    }
    _render_transaction_preview(payload)


def _ensure_transaction_state() -> None:
    st.session_state.setdefault("tx_amount", 0.0)
    st.session_state.setdefault("tx_price", 0.0)
    st.session_state.setdefault("tx_total", 0.0)


def _recalculate_from_amount() -> None:
    amount = float(st.session_state.tx_amount)
    price = float(st.session_state.tx_price)
    total = float(st.session_state.tx_total)

    if amount <= 0:
        return
    if price > 0:
        st.session_state.tx_total = round(amount * price, 2)
    elif total > 0:
        st.session_state.tx_price = round(total / amount, 4)


def _recalculate_from_price() -> None:
    amount = float(st.session_state.tx_amount)
    price = float(st.session_state.tx_price)

    if amount > 0 and price > 0:
        st.session_state.tx_total = round(amount * price, 2)


def _recalculate_from_total() -> None:
    amount = float(st.session_state.tx_amount)
    total = float(st.session_state.tx_total)

    if amount > 0 and total > 0:
        st.session_state.tx_price = round(total / amount, 4)


def _render_transaction_preview(payload: dict[str, object]) -> None:
    render_section_header("Preview", "Controle")
    errors = _validate_transaction(payload)

    with st.container(border=True):
        if errors:
            st.warning("Vul minimaal Aantal en Prijs per stuk of Totaal in.")
            for error in errors:
                st.caption(error)
            return

        st.dataframe(pd.DataFrame([payload]), hide_index=True, width="stretch")
        confirmed = st.checkbox("Ik bevestig deze preview", key="tx_confirmed")
        if st.button("Bevestig mock-transactie", disabled=not confirmed):
            st.success("Preview bevestigd. Er is niets opgeslagen in fase 2.")


def _validate_transaction(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    transaction_type = str(payload["Type"])
    amount = float(payload["Aantal"])
    price = float(payload["Prijs per stuk"])
    total = float(payload["Totaal"])

    if not str(payload["Ticker"]).strip():
        errors.append("Ticker is verplicht.")
    if transaction_type in {"Initial", "Buy", "Sell"} and amount <= 0:
        errors.append("Aantal moet groter zijn dan 0 voor Initial, Buy en Sell.")
    if transaction_type in {"Initial", "Buy", "Sell"} and price <= 0:
        errors.append("Prijs per stuk moet groter zijn dan 0 voor Initial, Buy en Sell.")
    if total <= 0:
        errors.append("Totaal moet groter zijn dan 0.")

    return errors
