import streamlit as st

from src.config import APP_CONFIG
from src.dashboard import render_dashboard
from src.mock_data import load_mock_data
from src.portfolio import render_portfolio_table
from src.saldi import render_saldi_form
from src.styles import inject_global_styles
from src.transactions import render_transaction_form
from src.ui import render_app_header


st.set_page_config(
    page_title=APP_CONFIG.page_title,
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def get_data():
    return load_mock_data()


def main() -> None:
    inject_global_styles()

    data = get_data()
    render_app_header(APP_CONFIG.page_title, APP_CONFIG.phase_label)

    dashboard_tab, portfolio_tab, transaction_tab, saldi_tab = st.tabs(
        ["Dashboard", "Portfolio", "Transactie", "Saldi"]
    )

    with dashboard_tab:
        render_dashboard(data.portfolio, data.saldi, data.historie)

    with portfolio_tab:
        render_portfolio_table(data.portfolio)

    with transaction_tab:
        render_transaction_form(data.portfolio)

    with saldi_tab:
        render_saldi_form(data.saldi)


if __name__ == "__main__":
    main()
