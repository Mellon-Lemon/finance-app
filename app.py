import streamlit as st

from src.apps_script_client import (
    is_apps_script_refresh_configured,
    refresh_portfolio_via_apps_script,
)
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


def queue_status_message(level: str, message: str) -> None:
    st.session_state["status_message"] = {"level": level, "message": message}


def refresh_data(message: str = "Data opnieuw geladen.", level: str = "success") -> None:
    get_data.clear()
    queue_status_message(level, message)
    st.rerun()


def render_status_message() -> None:
    status = st.session_state.pop("status_message", None)
    if not status:
        return

    level = status.get("level", "info")
    message = status.get("message", "")
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def render_refresh_control(source_label: str) -> None:
    _, data_col, portfolio_col = st.columns([1, 0.22, 0.24], gap="medium")
    with data_col:
        if st.button("Data verversen", type="secondary"):
            refresh_data()
    with portfolio_col:
        if st.button("Portfolio bijwerken", type="secondary"):
            update_portfolio_and_reload(source_label)


def update_portfolio_and_reload(source_label: str) -> None:
    if source_label != "Live Google Sheets":
        st.info("Portfolio bijwerken is alleen beschikbaar in Live Google Sheets mode.")
        return

    if not is_apps_script_refresh_configured():
        st.info("Apps Script refresh is nog niet geconfigureerd.")
        return

    with st.spinner("Portfolio bijwerken..."):
        result = refresh_portfolio_via_apps_script()

    if result.ok:
        refresh_data("Portfolio bijgewerkt. Data opnieuw geladen.")
    else:
        st.error(result.message)


def handle_write_success(action_label: str) -> None:
    if not is_apps_script_refresh_configured():
        refresh_data(
            f"{action_label} opgeslagen. Portfolio bijwerken is nog niet geconfigureerd.",
            level="info",
        )
        return

    with st.spinner("Portfolio bijwerken..."):
        result = refresh_portfolio_via_apps_script()

    if result.ok:
        refresh_data(f"{action_label} opgeslagen. Portfolio bijgewerkt en data opnieuw geladen.")
        return

    refresh_data(
        f"{action_label} opgeslagen, maar Portfolio bijwerken faalde. Data opnieuw geladen. {result.message}",
        level="warning",
    )


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
    render_status_message()
    if is_google_debug_ui_enabled() and data.google_debug:
        with st.expander("Debug Google Sheets"):
            st.caption("Veilige diagnostiek. Secrets en volledige Sheet-ID worden niet getoond.")
            st.json(data.google_debug)
    render_refresh_control(data.source_label)
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
            on_write_success=lambda: handle_write_success("Transactie"),
        )

    with saldi_tab:
        render_saldi_form(
            data.saldi,
            write_enabled=write_enabled,
            on_write_success=lambda: handle_write_success("Saldo"),
        )


if __name__ == "__main__":
    main()
