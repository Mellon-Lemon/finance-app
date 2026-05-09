from __future__ import annotations

import pandas as pd
import streamlit as st

from src.formatting import format_currency, signed_currency
from src.ui import MetricCard, render_metric_card, render_section_header


def render_saldi_form(saldi: pd.DataFrame) -> None:
    render_section_header("Cash", "Saldi aanpassen")

    account = st.selectbox("Account", saldi["Account"].tolist())
    current_balance = float(
        saldi.loc[saldi["Account"] == account, "Huidig Saldo"].iloc[0]
    )

    render_metric_card(MetricCard("Huidig saldo", format_currency(current_balance)))

    with st.form("saldi_form", clear_on_submit=False):
        new_balance = st.number_input(
            "Nieuw saldo",
            min_value=0.0,
            value=current_balance,
            step=50.0,
            format="%.2f",
        )
        confirmed = st.checkbox("Ik bevestig deze mock-preview")
        submitted = st.form_submit_button("Toon saldo-preview", use_container_width=True)

    if not submitted:
        return

    difference = new_balance - current_balance
    preview = pd.DataFrame(
        [
            {
                "Account": account,
                "Huidig Saldo": current_balance,
                "Nieuw Saldo": new_balance,
                "Verschil": difference,
            }
        ]
    )

    render_metric_card(MetricCard("Verschil", signed_currency(difference)))
    st.dataframe(
        preview,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Huidig Saldo": st.column_config.NumberColumn(
                "Huidig Saldo", format="EUR %.2f"
            ),
            "Nieuw Saldo": st.column_config.NumberColumn(
                "Nieuw Saldo", format="EUR %.2f"
            ),
            "Verschil": st.column_config.NumberColumn("Verschil", format="EUR %.2f"),
        },
    )
    if confirmed:
        st.success("Saldo-preview bevestigd. Er is niets opgeslagen in fase 2.")
    else:
        st.warning("Preview getoond. Vink bevestiging aan voordat write-back in latere fases wordt gebruikt.")
