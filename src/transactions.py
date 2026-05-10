from __future__ import annotations

import logging
from datetime import date

import pandas as pd
import streamlit as st

from src.formatting import format_currency, format_currency_eur, format_quantity, format_quantity_with_unit
from src.sheets_client import GoogleSheetsClient, TRANSACTION_COLUMNS
from src.ui import (
    render_empty_state,
    render_price_result_card,
    render_section_header,
    render_transaction_item,
)


LOGGER = logging.getLogger(__name__)
TRANSACTION_TYPES = ["Buy", "Sell", "Dividend", "Profit", "Initial"]
CURRENCIES = ["EUR", "USD"]
POSITION_TYPES = {"Buy", "Sell", "Initial"}
CASHFLOW_TYPES = {"Dividend", "Profit"}


def render_transaction_form(
    portfolio: pd.DataFrame,
    transactions: pd.DataFrame,
    *,
    write_enabled: bool = False,
    on_write_success=None,
    on_delete_success=None,
    refresh_configured: bool = False,
) -> None:
    _apply_transaction_reset()
    _ensure_transaction_defaults()
    render_section_header("Invoer", "Nieuwe transactie")

    ticker_options = sorted(portfolio["Ticker"].unique())
    with st.container(border=True):
        datum = st.date_input(
            "Datum",
            format="DD-MM-YYYY",
            key="tx_date",
        )
        ticker_col, type_col, currency_col = st.columns(3, gap="medium")
        with ticker_col:
            ticker = st.selectbox("Ticker", ticker_options, key="tx_ticker")
        with type_col:
            transaction_type = st.selectbox("Type", TRANSACTION_TYPES, key="tx_type")
        with currency_col:
            currency = st.selectbox("Valuta", CURRENCIES, key="tx_currency")

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
    _render_recent_transactions(transactions, write_enabled)
    _render_delete_transaction(transactions, write_enabled, refresh_configured, on_delete_success)


def _apply_transaction_reset() -> None:
    if not st.session_state.pop("tx_reset_after_save", False):
        return
    st.session_state["tx_date"] = date.today()
    st.session_state["tx_type"] = "Buy"
    st.session_state["tx_currency"] = "EUR"
    st.session_state["tx_amount_position"] = 0.0
    st.session_state["tx_total_position"] = 0.0
    st.session_state["tx_total_cashflow"] = 0.0
    st.session_state["tx_confirmed"] = False


def _ensure_transaction_defaults() -> None:
    st.session_state.setdefault("tx_date", date.today())
    st.session_state.setdefault("tx_type", "Buy")
    st.session_state.setdefault("tx_currency", "EUR")


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
        render_price_result_card(
            "Prijs per stuk",
            format_currency(price, currency, decimals=2),
            "Berekend uit Aantal en Totaal.",
        )
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
    render_section_header("Controle", "Opslaan")
    errors = validate_transaction(payload)
    row = build_transaction_row(payload)
    row_key = tuple(row[column] for column in TRANSACTION_COLUMNS)

    with st.container(border=True):
        if errors:
            st.warning("Controleer de invoer voordat je opslaat.")
            for error in errors:
                st.caption(error)
            return

        _render_row_preview(row)
        with st.expander("Exacte rij-preview"):
            st.dataframe(pd.DataFrame([row], columns=TRANSACTION_COLUMNS), hide_index=True, width="stretch")
        if not write_enabled:
            st.info("Opslaan is alleen beschikbaar met Live Google Sheets data.")

        already_saved = st.session_state.get("tx_last_saved_row") == row_key
        if already_saved:
            st.success("Deze transactie is opgeslagen.")

        confirmed = st.checkbox("Ik bevestig deze transactie", key="tx_confirmed")
        disabled = (
            not confirmed
            or not write_enabled
            or already_saved
            or st.session_state.get("tx_save_in_progress", False)
        )
        if st.button("Transactie opslaan", disabled=disabled, key="tx_save_button", type="primary"):
            _save_transaction(row, row_key, on_write_success)


def _save_transaction(
    row: dict[str, object],
    row_key: tuple[object, ...],
    on_write_success,
) -> None:
    if st.session_state.get("tx_last_saved_row") == row_key:
        st.warning("Deze transactie is al opgeslagen.")
        return

    try:
        st.session_state["tx_save_in_progress"] = True
        GoogleSheetsClient.from_environment().append_transaction(row)
    except Exception as exc:
        LOGGER.warning("Transactie opslaan faalt veilig: %s", exc)
        st.error("Transactie kon niet worden opgeslagen. Controleer schrijfrechten en tabblad Transacties.")
        st.session_state["tx_save_in_progress"] = False
        return

    st.session_state["tx_last_saved_row"] = row_key
    st.session_state["tx_reset_after_save"] = True
    st.session_state["tx_save_in_progress"] = False
    if on_write_success:
        on_write_success()
    st.success("Transactie opgeslagen in Google Sheets.")


def _render_recent_transactions(transactions: pd.DataFrame, write_enabled: bool) -> None:
    render_section_header("Recent", "Recente transacties")
    with st.container(border=True):
        if transactions.empty:
            if write_enabled:
                render_empty_state("Geen transacties", "Er zijn nog geen transacties gevonden in Google Sheets.")
            else:
                render_empty_state("Geen live transacties", "Recente transacties zijn alleen beschikbaar met Live Google Sheets data.")
            return

        if not write_enabled:
            st.info("Mockdata preview. Er wordt niets naar Google Sheets geschreven of verwijderd.")

        recent = _sort_transactions_newest_first(transactions).head(10).reset_index(drop=True)
        for index, row in recent.iterrows():
            _render_recent_transaction_item(row, write_enabled, index)
        if write_enabled:
            if st.button("Correctie verwijderen", type="secondary", key="tx_delete_panel_open"):
                st.session_state["tx_show_delete_panel"] = True


def _render_delete_transaction(
    transactions: pd.DataFrame,
    write_enabled: bool,
    refresh_configured: bool,
    on_delete_success,
) -> None:
    if not st.session_state.get("tx_show_delete_panel", False):
        return

    render_section_header("Correctie", "Transactie verwijderen")
    with st.container(border=True):
        if st.button("Sluiten", type="secondary", key="tx_delete_panel_close"):
            st.session_state["tx_show_delete_panel"] = False
            st.rerun()
        if not write_enabled:
            st.info("Verwijderen is alleen beschikbaar met Live Google Sheets data.")
            return
        if transactions.empty:
            st.info("Geen transacties gevonden om te verwijderen.")
            return
        if not refresh_configured:
            st.info("Verwijderen is beschikbaar zodra Portfolio bijwerken is geconfigureerd.")
            return

        safe_transactions = transactions.loc[
            pd.to_numeric(transactions["Sheet rij"], errors="coerce").fillna(0).astype(int) >= 2
        ].copy()
        if safe_transactions.empty:
            st.warning("Rijnummers konden niet veilig worden bepaald. Verwijderen is uitgeschakeld.")
            return

        ticker_options = sorted(safe_transactions["Ticker"].dropna().astype(str).unique())
        prefill_ticker = st.session_state.get("tx_delete_prefill_ticker")
        if prefill_ticker in ticker_options:
            st.session_state["tx_delete_ticker_select"] = prefill_ticker
        ticker = st.selectbox("Ticker voor correctie", ticker_options, key="tx_delete_ticker_select")
        latest_for_ticker = (
            _sort_transactions_newest_first(
                safe_transactions.loc[safe_transactions["Ticker"].astype(str) == ticker]
            )
            .head(3)
            .reset_index(drop=True)
        )
        if latest_for_ticker.empty:
            st.info("Geen transacties gevonden voor deze ticker.")
            return

        st.dataframe(
            latest_for_ticker[
                ["Sheet rij", "Datum", "Ticker", "Type", "Aantal", "Totaal", "Valuta"]
            ],
            hide_index=True,
            width="stretch",
        )

        labels = [_delete_option_label(row) for _, row in latest_for_ticker.iterrows()]
        prefill_row = int(st.session_state.get("tx_delete_prefill_row", 0) or 0)
        default_index = 0
        if prefill_row:
            matches = latest_for_ticker.index[latest_for_ticker["Sheet rij"].astype(int) == prefill_row].tolist()
            if matches:
                default_index = int(matches[0])
        selected_label = st.radio(
            "Kies exact een transactie",
            labels,
            index=default_index,
            key=f"tx_delete_selection_{_safe_key_part(ticker)}",
        )
        selected_index = labels.index(selected_label)
        selected = latest_for_ticker.iloc[selected_index].to_dict()
        selected_sheet_row = int(selected.get("Sheet rij", 0))

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Sheet rij": selected.get("Sheet rij", ""),
                        "Datum": selected.get("Datum", ""),
                        "Ticker": selected.get("Ticker", ""),
                        "Type": selected.get("Type", ""),
                        "Aantal": selected.get("Aantal", ""),
                        "Totaal": selected.get("Totaal", ""),
                        "Valuta": selected.get("Valuta", ""),
                    }
                ]
            ),
            hide_index=True,
            width="stretch",
        )

        confirmed = st.checkbox(
            "Ik begrijp dat deze transactie uit Google Sheets wordt verwijderd.",
            key=f"tx_delete_confirmed_{selected_sheet_row}",
        )
        disabled = not confirmed or st.session_state.get("tx_delete_in_progress", False)
        if st.button(
            "Transactie verwijderen",
            disabled=disabled,
            type="secondary",
            key=f"tx_delete_confirm_button_{selected_sheet_row}",
        ):
            _delete_transaction(selected, on_delete_success)


def _prepare_recent_transactions_view(transactions: pd.DataFrame) -> pd.DataFrame:
    view = transactions[["Datum", "Ticker", "Type", "Aantal", "Totaal", "Valuta"]].copy()
    view["Aantal"] = [
        format_quantity(_parse_float(amount), str(ticker))
        for amount, ticker in zip(view["Aantal"], view["Ticker"])
    ]
    view["Totaal"] = [
        format_currency_eur(_parse_float(total))
        if str(currency).upper() == "EUR"
        else f"{currency} {_parse_float(total):,.0f}"
        for total, currency in zip(view["Totaal"], view["Valuta"])
    ]
    return view


def _render_row_preview(row: dict[str, object]) -> None:
    ticker = str(row.get("Ticker", ""))
    amount = _parse_float(row.get("Aantal", 0))
    total = _parse_float(row.get("Totaal", 0))
    currency = str(row.get("Valuta", "EUR"))
    total_label = format_currency_eur(total) if currency.upper() == "EUR" else f"{currency} {total:,.0f}"
    detail = (
        f"{row.get('Type', '')} · {row.get('Datum', '')} · "
        f"{format_quantity_with_unit(amount, ticker)}"
    )
    render_transaction_item(ticker=ticker, detail=detail, amount=total_label)


def _render_recent_transaction_item(row: pd.Series, write_enabled: bool, index: int) -> None:
    sheet_row = int(row.get("Sheet rij", 0) or 0)
    ticker = str(row.get("Ticker", ""))
    amount = _parse_float(row.get("Aantal", 0))
    total = _parse_float(row.get("Totaal", 0))
    currency = str(row.get("Valuta", "EUR"))
    total_label = format_currency_eur(total) if currency.upper() == "EUR" else f"{currency} {total:,.0f}"
    detail = f"{row.get('Type', '')} · {row.get('Datum', '')} · {format_quantity_with_unit(amount, ticker)}"

    item_col, action_col = st.columns([1, 0.16], gap="small")
    with item_col:
        render_transaction_item(ticker=ticker, detail=detail, amount=total_label)
    with action_col:
        if write_enabled and sheet_row >= 2:
            if st.button(
                "\U0001f5d1",
                key=f"tx_recent_delete_{sheet_row}_{index}",
                help="Transactie verwijderen",
                type="secondary",
            ):
                st.session_state["tx_show_delete_panel"] = True
                st.session_state["tx_delete_prefill_ticker"] = ticker
                st.session_state["tx_delete_prefill_row"] = sheet_row


def _sort_transactions_newest_first(transactions: pd.DataFrame) -> pd.DataFrame:
    sorted_transactions = transactions.copy()
    sorted_transactions["Sheet rij"] = pd.to_numeric(
        sorted_transactions["Sheet rij"], errors="coerce"
    ).fillna(0).astype(int)
    return sorted_transactions.sort_values("Sheet rij", ascending=False)


def _delete_option_label(row: pd.Series) -> str:
    return (
        f"Rij {row.get('Sheet rij')} - {row.get('Datum')} - "
        f"{row.get('Ticker')} {row.get('Type')} - {row.get('Totaal')} {row.get('Valuta')}"
    )


def _parse_float(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip().replace("\u20ac", "").replace("EUR", "").replace(" ", "")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _safe_key_part(value: object) -> str:
    return "".join(character if character.isalnum() else "_" for character in str(value))


def _delete_transaction(
    selected: dict[str, object],
    on_delete_success,
) -> None:
    try:
        sheet_row = int(selected.get("Sheet rij", 0))
    except (TypeError, ValueError):
        st.error("Transactie kon niet veilig worden verwijderd: ongeldig rijnummer.")
        return

    expected_row = {column: selected.get(column, "") for column in TRANSACTION_COLUMNS}
    try:
        st.session_state["tx_delete_in_progress"] = True
        GoogleSheetsClient.from_environment().delete_transaction_row(sheet_row, expected_row)
    except Exception as exc:
        LOGGER.warning("Transactie verwijderen faalt veilig: %s", exc)
        st.error("Transactie kon niet worden verwijderd. Laad data opnieuw en controleer de preview.")
        st.session_state["tx_delete_in_progress"] = False
        return

    st.session_state["tx_delete_in_progress"] = False
    if on_delete_success:
        on_delete_success()
    st.success("Transactie verwijderd uit Google Sheets.")


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
