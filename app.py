import streamlit as st

from src.config import APP_CONFIG
from src.data_loader import (
    ensure_finance_data_contract,
    is_google_debug_ui_enabled,
    load_finance_data,
)
from src.dashboard import render_dashboard
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
    return ensure_finance_data_contract(load_finance_data())


def main() -> None:
    inject_global_styles()

    data = get_data()
    render_app_header(
        APP_CONFIG.page_title,
        APP_CONFIG.phase_label,
        data.source_label,
        data.source_message,
    )
    if data.source_warning:
        st.warning(data.source_warning)
    if is_google_debug_ui_enabled() and data.google_debug:
        with st.expander("Debug Google Sheets"):
            st.caption("Veilige diagnostiek. Secrets en volledige Sheet-ID worden niet getoond.")
            st.json(data.google_debug)
    write_enabled = data.source_label == "Live Google Sheets"

    dashboard_tab, portfolio_tab, transaction_tab, saldi_tab = st.tabs(
        ["Dashboard", "Portfolio", "Transactie", "Saldi"]
    )

    with dashboard_tab:
        render_dashboard(data.portfolio, data.saldi, data.historie, data.dividend_total)

    with portfolio_tab:
        render_portfolio_table(data.portfolio, data.historie)

    with transaction_tab:
        render_transaction_form(
            data.portfolio,
            write_enabled=write_enabled,
            on_write_success=get_data.clear,
        )

    with saldi_tab:
        render_saldi_form(
            data.saldi,
            write_enabled=write_enabled,
            on_write_success=get_data.clear,
        )


if __name__ == "__main__":
    main()
