from __future__ import annotations

import logging
from datetime import date

import pandas as pd
import streamlit as st

from src.formatting import format_currency
from src.sheets_client import GoogleSheetsClient, TRANSACTION_COLUMNS
from src.ui import render_section_header


LOGGER = logging.getLogger(__name__)
TRANSACTION_TYPES = ["Buy", "Sell", "Dividend", "Profit", "Initial"]
CURRENCIES = ["EUR", "USD"]
POSITION_TYPES = {"Buy", "Sell", "Initial"}
CASHFLOW_TYPES = {"Dividend", "Profit"}


def render_transaction_form(
    portfolio: pd.DataFrame,
    *,
    write_enabled: bool = False,
    on_write_success=None,
) -> None:
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
    _render_transaction_preview(payload, write_enabled, on_write_success)


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

    min_total = 0.0 if transaction_type == "Dividend" else None
    total = st.number_input(
        "Totaal",
        min_value=min_total,
        step=25.0,
        format="%.2f",
        key="tx_total_cashflow",
        help="Inclusief eventuele kosten.",
    )
    if transaction_type == "Dividend":
        st.caption("Dividend schrijft Aantal en Prijs per stuk als 0.")
    else:
        st.caption("Profit gebruikt de waarde zoals ingevoerd, positief of negatief.")
    return 0.0, 0.0, float(total)


def build_transaction_row(payload: dict[str, object]) -> dict[str, object]:
    transaction_type = str(payload["Type"])
    total = float(payload["Totaal"])

    if transaction_type in CASHFLOW_TYPES:
        amount = 0.0
        price = 0.0
    else:
        amount = float(payload["Aantal"])
        price = _calculate_price_per_unit(amount, total)

    return {
        "Datum": str(payload["Datum"]),
        "Ticker": str(payload["Ticker"]).strip(),
        "Type": transaction_type,
        "Aantal": amount,
        "Prijs per stuk": price,
        "Kosten": 0,
        "Totaal": total,
        "Valuta": str(payload["Valuta"]).strip(),
    }


def _calculate_price_per_unit(amount: float, total: float) -> float:
    if amount <= 0 or total <= 0:
        return 0.0
    return round(total / amount, 4)


def _render_transaction_preview(
    payload: dict[str, object],
    write_enabled: bool,
    on_write_success,
) -> None:
    render_section_header("Preview", "Controle")
    errors = validate_transaction(payload)
    row = build_transaction_row(payload)
    row_key = tuple(row[column] for column in TRANSACTION_COLUMNS)

    with st.container(border=True):
        if errors:
            st.warning("Controleer de invoer voordat je opslaat.")
            for error in errors:
                st.caption(error)
            return

        st.dataframe(pd.DataFrame([row], columns=TRANSACTION_COLUMNS), hide_index=True, width="stretch")
        if not write_enabled:
            st.info("Opslaan is alleen beschikbaar met Live Google Sheets data.")

        already_saved = st.session_state.get("tx_last_saved_row") == row_key
        if already_saved:
            st.success("Deze transactie is opgeslagen.")

        confirmed = st.checkbox("Ik bevestig deze transactie", key="tx_confirmed")
        disabled = not confirmed or not write_enabled or already_saved
        if st.button("Transactie opslaan", disabled=disabled):
            _save_transaction(row, row_key, on_write_success)


def _save_transaction(
    row: dict[str, object],
    row_key: tuple[object, ...],
    on_write_success,
) -> None:
    try:
        GoogleSheetsClient.from_environment().append_transaction(row)
    except Exception as exc:
        LOGGER.warning("Transactie opslaan faalt veilig: %s", exc)
        st.error("Transactie kon niet worden opgeslagen. Controleer schrijfrechten en tabblad Transacties.")
        return

    st.session_state["tx_last_saved_row"] = row_key
    if on_write_success:
        on_write_success()
    st.success("Transactie opgeslagen in Google Sheets.")
    st.dataframe(pd.DataFrame([row], columns=TRANSACTION_COLUMNS), hide_index=True, width="stretch")


def validate_transaction(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    transaction_type = str(payload.get("Type", ""))
    amount = float(payload.get("Aantal", 0) or 0)
    total = float(payload.get("Totaal", 0) or 0)

    if not str(payload.get("Datum", "")).strip():
        errors.append("Datum is verplicht.")
    if not str(payload.get("Ticker", "")).strip():
        errors.append("Ticker is verplicht.")
    if transaction_type not in TRANSACTION_TYPES:
        errors.append("Type is verplicht.")
    if not str(payload.get("Valuta", "")).strip():
        errors.append("Valuta is verplicht.")

    if transaction_type in POSITION_TYPES:
        if amount <= 0:
            errors.append("Aantal moet groter zijn dan 0 voor Buy, Sell en Initial.")
        if total <= 0:
            errors.append("Totaal moet groter zijn dan 0 voor Buy, Sell en Initial.")
        if amount > 0 and total > 0 and _calculate_price_per_unit(amount, total) <= 0:
            errors.append("Prijs per stuk kon niet worden berekend.")
    elif transaction_type == "Dividend":
        if total <= 0:
            errors.append("Totaal moet groter zijn dan 0 voor Dividend.")
    elif transaction_type == "Profit":
        if total == 0:
            errors.append("Totaal mag niet 0 zijn voor Profit.")

    return errors
