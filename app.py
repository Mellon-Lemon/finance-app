import streamlit as st

from src.apps_script_client import (
    create_manual_snapshot_via_apps_script,
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
from src.ui import render_action_bar, render_app_header, render_icon_nav


APP_TABS = ["Dashboard", "Portfolio", "Transactie", "Saldi"]
NAV_LABELS = {
    "Dashboard": "\U0001f3e0 Dashboard",
    "Portfolio": "\U0001f4ca Portfolio",
    "Transactie": "\u2795 Transactie",
    "Saldi": "\U0001f4b0 Saldi",
}
DATA_MODE_LABELS = {
    "live": "Live Google Sheets",
    "demo": "Demo / Mockdata",
}

st.set_page_config(
    page_title=APP_CONFIG.page_title,
    layout="wide",
    initial_sidebar_state="collapsed",
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


def get_current_data_mode() -> str:
    st.session_state.setdefault("data_mode", "live")
    return st.session_state["data_mode"]


def render_navigation() -> str:
    st.session_state.setdefault("active_tab", "Dashboard")
    active_tab = st.session_state["active_tab"]
    if active_tab not in APP_TABS:
        active_tab = "Dashboard"
        st.session_state["active_tab"] = active_tab
    return render_icon_nav(active_tab, NAV_LABELS)


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


def request_manual_snapshot(source_label: str, data_mode: str) -> None:
    if data_mode == "demo":
        st.info("Snapshot maken is alleen beschikbaar in Live Google Sheets mode.")
        return

    if source_label != "Live Google Sheets":
        st.info("Snapshot maken is alleen beschikbaar in Live Google Sheets mode.")
        return

    if not is_apps_script_refresh_configured():
        st.info("Snapshot maken is nog niet geconfigureerd.")
        return

    st.session_state["show_manual_snapshot_confirmation"] = True


def render_manual_snapshot_confirmation(source_label: str, data_mode: str) -> None:
    if not st.session_state.get("show_manual_snapshot_confirmation", False):
        return

    with st.container(border=True):
        st.warning("Dit schrijft een nieuwe regel naar Historie, maar verstuurt geen e-mail.")
        st.caption(
            "Meerdere snapshots per dag zijn toegestaan, maar beinvloeden je historische grafieken."
        )

        if data_mode != "live" or source_label != "Live Google Sheets":
            st.info("Snapshot maken is alleen beschikbaar in Live Google Sheets mode.")
            return

        if not is_apps_script_refresh_configured():
            st.info("Snapshot maken is nog niet geconfigureerd.")
            return

        confirmed = st.checkbox(
            "Ik bevestig dat ik handmatig een Historie-snapshot wil maken.",
            key="manual_snapshot_confirmed",
        )
        action_col, cancel_col = st.columns([1, 1], gap="small")
        with action_col:
            if st.button(
                "Snapshot definitief maken",
                type="primary",
                key="manual_snapshot_confirm_button",
                disabled=not confirmed or st.session_state.get("manual_snapshot_in_progress", False),
            ):
                create_manual_snapshot_and_reload()
        with cancel_col:
            if st.button("Annuleren", type="secondary", key="manual_snapshot_cancel_button"):
                st.session_state["show_manual_snapshot_confirmation"] = False
                st.session_state["manual_snapshot_confirmed"] = False
                st.rerun()


def create_manual_snapshot_and_reload() -> None:
    try:
        st.session_state["manual_snapshot_in_progress"] = True
        with st.spinner("Snapshot maken..."):
            result = create_manual_snapshot_via_apps_script()
    except Exception:
        st.error("Snapshot maken is mislukt. Controleer de Apps Script configuratie en probeer opnieuw.")
        return
    finally:
        st.session_state["manual_snapshot_in_progress"] = False

    if not result.ok:
        st.error(result.message)
        return

    st.session_state["show_manual_snapshot_confirmation"] = False
    st.session_state["manual_snapshot_confirmed"] = False
    timestamp = f" Tijdstip: {result.timestamp}." if result.timestamp else ""
    refresh_data(f"Snapshot gemaakt.{timestamp} Data opnieuw geladen.")


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

    data_mode = get_current_data_mode()
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
    render_action_bar(
        data_mode_labels=DATA_MODE_LABELS,
        source_label=data.source_label,
        on_reload=lambda: refresh_data("Data opnieuw geladen."),
        on_refresh=lambda: update_portfolio_and_reload(data.source_label, get_current_data_mode()),
        on_snapshot_request=lambda: request_manual_snapshot(
            data.source_label,
            get_current_data_mode(),
        ),
        render_snapshot_confirmation=lambda: render_manual_snapshot_confirmation(
            data.source_label,
            get_current_data_mode(),
        ),
        refresh_disabled=data_mode != "live" or data.source_label != "Live Google Sheets",
        snapshot_disabled=(
            data_mode != "live"
            or data.source_label != "Live Google Sheets"
            or not is_apps_script_refresh_configured()
        ),
    )
    write_enabled = data_mode == "live" and data.source_label == "Live Google Sheets"

    active_tab = render_navigation()

    if active_tab == "Dashboard":
        render_dashboard(
            data.portfolio,
            data.saldi,
            data.historie,
            data.dividend_total,
            data.price_quotes,
        )

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
