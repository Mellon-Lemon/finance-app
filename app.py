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


APP_TABS = ["Dashboard", "Portfolio", "Transactie", "Saldi"]
DATA_MODE_LABELS = {
    "live": "Live Google Sheets",
    "demo": "Demo / Mockdata",
}

st.set_page_config(
    page_title=APP_CONFIG.page_title,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_data(force_mock: bool = False):
    return ensure_finance_data_contract(load_finance_data(force_mock=force_mock))


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


def render_data_mode_control() -> str:
    st.session_state.setdefault("data_mode", "live")
    with st.sidebar:
        st.radio(
            "Datamodus",
            options=list(DATA_MODE_LABELS.keys()),
            format_func=lambda value: DATA_MODE_LABELS[value],
            key="data_mode",
        )
        if st.session_state["data_mode"] == "demo":
            st.info("Demo mode gebruikt alleen mockdata en schrijft nooit naar Google Sheets.")
    return st.session_state["data_mode"]


def render_refresh_control(source_label: str, data_mode: str) -> None:
    _, data_col, portfolio_col = st.columns([1, 0.22, 0.24], gap="medium")
    with data_col:
        if st.button("Data opnieuw laden", type="secondary", key="reload_data_button"):
            refresh_data("Data opnieuw geladen.")
    with portfolio_col:
        if st.button("Portfolio bijwerken", type="secondary", key="refresh_portfolio_button"):
            update_portfolio_and_reload(source_label, data_mode)


def render_navigation() -> str:
    st.session_state.setdefault("active_tab", "Dashboard")
    return st.radio(
        "Navigatie",
        APP_TABS,
        horizontal=True,
        key="active_tab",
        label_visibility="collapsed",
    )


def update_portfolio_and_reload(source_label: str, data_mode: str) -> None:
    if data_mode == "demo":
        st.info("Portfolio bijwerken is uitgeschakeld in Demo / Mockdata mode.")
        return

    if source_label != "Live Google Sheets":
        st.info("Portfolio bijwerken is alleen beschikbaar in Live Google Sheets mode.")
        return

    if not is_apps_script_refresh_configured():
        st.info("Portfolio bijwerken is nog niet geconfigureerd.")
        return

    with st.spinner("Portfolio bijwerken..."):
        result = refresh_portfolio_via_apps_script()

    if result.ok:
        refresh_data("Portfolio bijgewerkt. Data opnieuw geladen.")
    else:
        st.error(result.message)


def handle_write_success(action_message: str) -> None:
    if not is_apps_script_refresh_configured():
        refresh_data(
            (
                f"{action_message} in Google Sheets. "
                "Portfolio bijwerken is nog niet geconfigureerd. Data opnieuw geladen."
            ),
            level="info",
        )
        return

    with st.spinner("Portfolio bijwerken..."):
        result = refresh_portfolio_via_apps_script()

    if result.ok:
        refresh_data(
            (
                f"{action_message} in Google Sheets. "
                "Portfolio bijgewerkt. Data opnieuw geladen."
            )
        )
        return

    refresh_data(
        (
            f"{action_message} in Google Sheets, maar Portfolio bijwerken mislukt. "
            f"Data opnieuw geladen. Gebruik Portfolio bijwerken om opnieuw te proberen. {result.message}"
        ),
        level="warning",
    )


def main() -> None:
    inject_global_styles()

    data_mode = render_data_mode_control()
    force_mock = data_mode == "demo"
    data = get_data(force_mock)
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
    render_refresh_control(data.source_label, data_mode)
    write_enabled = data_mode == "live" and data.source_label == "Live Google Sheets"

    active_tab = render_navigation()

    if active_tab == "Dashboard":
        render_dashboard(data.portfolio, data.saldi, data.historie, data.dividend_total)

    elif active_tab == "Portfolio":
        render_portfolio_table(data.portfolio, data.historie)

    elif active_tab == "Transactie":
        render_transaction_form(
            data.portfolio,
            data.transactions,
            write_enabled=write_enabled,
            on_write_success=lambda: handle_write_success("Transactie opgeslagen"),
            on_delete_success=lambda: handle_write_success("Transactie verwijderd"),
            refresh_configured=data_mode == "live" and is_apps_script_refresh_configured(),
        )

    elif active_tab == "Saldi":
        render_saldi_form(
            data.saldi,
            write_enabled=write_enabled,
            on_write_success=lambda: handle_write_success("Saldo opgeslagen"),
        )


if __name__ == "__main__":
    main()
