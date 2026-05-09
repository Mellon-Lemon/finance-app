from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ui import render_section_header


def render_portfolio_table(portfolio: pd.DataFrame) -> None:
    render_section_header("Holdings", "Portfolio")

    with st.container(border=True):
        categories = ["Alles", *sorted(portfolio["Categorie"].unique())]
        selected_category = st.selectbox("Categorie", categories, index=0)
        filtered = (
            portfolio
            if selected_category == "Alles"
            else portfolio.loc[portfolio["Categorie"] == selected_category]
        )

        table = filtered[["Ticker", "Categorie", "Aantal", "Waarde", "Winst", "ROI %"]].copy()
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Categorie": st.column_config.TextColumn("Categorie", width="medium"),
                "Aantal": st.column_config.NumberColumn("Aantal", format="%.6f"),
                "Waarde": st.column_config.NumberColumn("Waarde", format="EUR %.2f"),
                "Winst": st.column_config.NumberColumn("Winst", format="EUR %.2f"),
                "ROI %": st.column_config.NumberColumn("ROI", format="%.1f%%"),
            },
        )
