from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from src.formatting import format_currency, signed_currency
from src.sheets_client import GoogleSheetsClient
from src.ui import MetricCard, render_metric_card, render_metric_grid, render_section_header


LOGGER = logging.getLogger(__name__)


def render_saldi_form(
    saldi: pd.DataFrame,
    *,
    write_enabled: bool = False,
    on_write_success=None,
) -> None:
    render_section_header("Cash", "Saldo overzicht")
    _render_cash_overview(saldi)

    render_section_header("Aanpassen", "Saldo wijzigen")
    _render_adjustment_form(saldi, write_enabled, on_write_success)


def _render_cash_overview(saldi: pd.DataFrame) -> None:
    total_cash = float(saldi["Huidig Saldo"].sum())
    render_metric_card(MetricCard("Totaal cashsaldo", format_currency(total_cash)))

    cards = [
        MetricCard(row["Account"], format_currency(float(row["Huidig Saldo"])))
        for _, row in saldi.iterrows()
    ]
    render_metric_grid(cards)


def _render_adjustment_form(
    saldi: pd.DataFrame,
    write_enabled: bool,
    on_write_success,
) -> None:
    with st.container(border=True):
        account = st.selectbox("Account", saldi["Account"].tolist())
        current_balance = float(
            saldi.loc[saldi["Account"] == account, "Huidig Saldo"].iloc[0]
        )
        new_balance = st.number_input(
            "Nieuwe waarde",
            min_value=0.0,
            value=current_balance,
            step=50.0,
            format="%.2f",
        )
        difference = new_balance - current_balance

        current_col, new_col, diff_col = st.columns(3, gap="medium")
        with current_col:
            st.metric("Huidige waarde", format_currency(current_balance))
        with new_col:
            st.metric("Nieuwe waarde", format_currency(new_balance))
        with diff_col:
            st.metric("Verschil", signed_currency(difference))

        preview = build_saldo_preview(account, current_balance, new_balance)
        errors = validate_saldo_update(saldi, account, new_balance)
        st.dataframe(pd.DataFrame([preview]), hide_index=True, width="stretch")

        if errors:
            st.warning("Controleer de wijziging voordat je opslaat.")
            for error in errors:
                st.caption(error)
            return

        if not write_enabled:
            st.info("Opslaan is alleen beschikbaar met Live Google Sheets data.")

        preview_key = (account, round(float(new_balance), 2))
        already_saved = st.session_state.get("saldo_last_saved") == preview_key
        if already_saved:
            st.success("Deze saldo-wijziging is opgeslagen.")

        confirmed = st.checkbox("Ik bevestig deze saldo-wijziging")
        disabled = not confirmed or not write_enabled or already_saved
        if st.button("Saldo opslaan", disabled=disabled):
            _save_saldo(account, float(new_balance), preview_key, on_write_success)


def build_saldo_preview(
    account: str,
    current_balance: float,
    new_balance: float,
) -> dict[str, object]:
    return {
        "Account": account,
        "Huidige waarde": current_balance,
        "Nieuwe waarde": new_balance,
        "Verschil": new_balance - current_balance,
    }


def validate_saldo_update(
    saldi: pd.DataFrame,
    account: str,
    new_value: float | None,
) -> list[str]:
    errors: list[str] = []
    if account not in set(saldi["Account"].tolist()):
        errors.append("Account bestaat niet in Saldi.")
    if new_value is None:
        errors.append("Nieuwe waarde is verplicht.")
    elif float(new_value) < 0:
        errors.append("Nieuwe waarde mag niet negatief zijn.")
    return errors


def _save_saldo(
    account: str,
    new_value: float,
    preview_key: tuple[object, ...],
    on_write_success,
) -> None:
    try:
        GoogleSheetsClient.from_environment().update_saldo(account, new_value)
    except Exception as exc:
        LOGGER.warning("Saldo opslaan faalt veilig: %s", exc)
        st.error("Saldo kon niet worden opgeslagen. Controleer schrijfrechten en tabblad Saldi.")
        return

    st.session_state["saldo_last_saved"] = preview_key
    if on_write_success:
        on_write_success()
    st.success("Saldo opgeslagen in Google Sheets.")
