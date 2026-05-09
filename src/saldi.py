from __future__ import annotations

import pandas as pd
import streamlit as st

from src.formatting import format_currency, signed_currency
from src.ui import MetricCard, render_metric_card, render_metric_grid, render_section_header


def render_saldi_form(saldi: pd.DataFrame) -> None:
    render_section_header("Cash", "Saldo overzicht")
    _render_cash_overview(saldi)

    render_section_header("Aanpassen", "Saldo wijzigen")
    _render_adjustment_form(saldi)


def _render_cash_overview(saldi: pd.DataFrame) -> None:
    total_cash = float(saldi["Huidig Saldo"].sum())
    render_metric_card(MetricCard("Totaal cashsaldo", format_currency(total_cash)))

    cards = [
        MetricCard(row["Account"], format_currency(float(row["Huidig Saldo"])))
        for _, row in saldi.iterrows()
    ]
    render_metric_grid(cards)


def _render_adjustment_form(saldi: pd.DataFrame) -> None:
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

        confirmed = st.checkbox("Ik bevestig deze wijziging")
        if st.button("Bevestig mock-wijziging", disabled=not confirmed):
            st.success("Saldo-preview bevestigd. Er is niets opgeslagen in fase 2.")
