from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui import render_section_header


TRANSACTION_TYPES = ["Initial", "Buy", "Sell", "Dividend", "Profit"]
CURRENCIES = ["EUR", "USD"]


def render_transaction_form(portfolio: pd.DataFrame) -> None:
    render_section_header("Invoer", "Nieuwe transactie")

    ticker_options = sorted(portfolio["Ticker"].unique())
    with st.form("transaction_form", clear_on_submit=False):
        datum = st.date_input("Datum", value=date.today())
        ticker = st.selectbox("Ticker", ticker_options)
        transaction_type = st.selectbox("Type", TRANSACTION_TYPES)

        col_a, col_b = st.columns(2)
        with col_a:
            amount = st.number_input("Aantal", min_value=0.0, step=0.01, format="%.8f")
            price = st.number_input("Prijs per stuk", min_value=0.0, step=1.0, format="%.2f")
        with col_b:
            costs = st.number_input("Kosten", min_value=0.0, step=1.0, format="%.2f")
            total = st.number_input("Totaal", min_value=0.0, step=10.0, format="%.2f")

        currency = st.selectbox("Valuta", CURRENCIES)
        confirmed = st.checkbox("Ik bevestig deze mock-preview")
        submitted = st.form_submit_button("Toon preview", use_container_width=True)

    if not submitted:
        return

    payload = {
        "Datum": datum.isoformat(),
        "Ticker": ticker,
        "Type": transaction_type,
        "Aantal": amount,
        "Prijs per stuk": price,
        "Kosten": costs,
        "Totaal": total,
        "Valuta": currency,
    }
    errors = _validate_transaction(payload)

    if errors:
        st.error("Controleer de invoer:\n\n" + "\n".join(f"- {error}" for error in errors))
        return

    st.dataframe(pd.DataFrame([payload]), hide_index=True, use_container_width=True)
    if confirmed:
        st.success("Preview bevestigd. Er is niets opgeslagen in fase 2.")
    else:
        st.warning("Preview getoond. Vink bevestiging aan voordat write-back in latere fases wordt gebruikt.")


def _validate_transaction(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    transaction_type = str(payload["Type"])
    amount = float(payload["Aantal"])
    price = float(payload["Prijs per stuk"])
    costs = float(payload["Kosten"])
    total = float(payload["Totaal"])

    if not str(payload["Ticker"]).strip():
        errors.append("Ticker is verplicht.")
    if transaction_type in {"Initial", "Buy", "Sell"} and amount <= 0:
        errors.append("Aantal moet groter zijn dan 0 voor Initial, Buy en Sell.")
    if transaction_type in {"Initial", "Buy", "Sell"} and price <= 0:
        errors.append("Prijs per stuk moet groter zijn dan 0 voor Initial, Buy en Sell.")
    if costs < 0:
        errors.append("Kosten mogen niet negatief zijn.")
    if total <= 0:
        errors.append("Totaal moet groter zijn dan 0.")

    return errors
