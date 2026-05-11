from __future__ import annotations

import logging
import os
import re
from dataclasses import replace
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv

from src.mock_data import MockFinanceData, load_mock_data
from src.sheets_client import GoogleSheetsClient, TRANSACTION_COLUMNS


LOGGER = logging.getLogger(__name__)
ATTEMPTED_SHEETS = ["Portfolio", "Saldi", "Historie", "Transacties (optioneel)"]
DEBUG_UI_ENV = "PORTFOLIO_DEBUG_GOOGLE"
load_dotenv()

PORTFOLIO_COLUMNS = [
    "Categorie",
    "Ticker",
    "Aantal",
    "Inleg",
    "Koers",
    "Waarde",
    "Winst",
    "ROI %",
]
SALDI_COLUMNS = ["Account", "Huidig Saldo"]
HISTORIE_COLUMNS = [
    "Datum",
    "Totaal",
    "Spaar",
    "Vakanties",
    "Vrije Ruimte",
    "Belegd Vermogen",
    "Crypto W.",
    "Crypto I.",
    "DeGiro W.",
    "DeGiro I.",
    "BTC Aant.",
    "Inleg Tot.",
    "BTC Koers",
    "TSWE Koers",
]
TRANSACTION_VIEW_COLUMNS = ["Sheet rij", "Datum", "Ticker", "Type", "Aantal", "Totaal", "Valuta"]
PRICE_QUOTE_TICKERS = ("BTC", "TSWE")
PRICE_QUOTE_LABELS = {
    "BTC": "Bitcoin",
    "TSWE": "TSWE",
}
PRICE_HISTORY_COLUMNS = {
    "BTC": "BTC Koers",
    "TSWE": "TSWE Koers",
}
PRICE_PERFORMANCE_PERIODS = {
    "24u": 1,
    "7d": 7,
    "30d": 30,
}


def load_finance_data(force_mock: bool = False) -> MockFinanceData:
    if force_mock:
        return ensure_finance_data_contract(
            load_mock_data(),
            source_label="Demo / Mockdata",
            source_message="Veilige demo",
            source_warning="Demo mode actief. Er wordt niets gelezen uit of geschreven naar Google Sheets.",
            google_debug={},
        )

    diagnostics = build_google_sheets_diagnostics()
    _log_google_sheets_diagnostics(diagnostics)

    try:
        client = GoogleSheetsClient.from_environment()
        data = load_google_sheets_data(client)
        return ensure_finance_data_contract(
            data,
            source_label="Live Google Sheets",
            source_message="Read-only data",
            source_warning="",
            google_debug=diagnostics,
        )
    except Exception as exc:
        safe_error = _safe_error_message(exc)
        LOGGER.warning("Google Sheets laden faalt veilig: %s", safe_error)
        warning = ""
        if _google_config_present():
            warning = "Google Sheets kon niet worden gelezen. Mockdata fallback is actief."
        return ensure_finance_data_contract(
            load_mock_data(),
            source_label="Mockdata" if not warning else "Fallback actief",
            source_message="Lokale fallback",
            source_warning=warning,
            google_debug={**diagnostics, "Foutmelding": safe_error},
        )


def load_google_sheets_data(client: GoogleSheetsClient) -> MockFinanceData:
    portfolio = parse_portfolio_sheet(client.get_records("Portfolio"))
    saldi = parse_saldi_sheet(client.get_records("Saldi"))
    historie = parse_historie_sheet(client.get_records("Historie"))
    if portfolio.empty or saldi.empty or historie.empty:
        raise ValueError("Een of meer verplichte Google Sheets tabs bevatten geen data.")

    transactions = client.try_get_transaction_rows()
    dividend_total = calculate_dividend_total(transactions)

    if dividend_total is None:
        dividend_total = load_mock_data().dividend_total

    return MockFinanceData(
        portfolio=portfolio,
        saldi=saldi,
        historie=historie,
        dividend_total=dividend_total,
        transactions=parse_transaction_sheet(transactions),
        price_quotes=build_price_quotes(portfolio, historie),
    )


def ensure_finance_data_contract(
    data: MockFinanceData,
    *,
    source_label: str | None = None,
    source_message: str | None = None,
    source_warning: str | None = None,
    google_debug: dict[str, str] | None = None,
) -> MockFinanceData:
    values = {
        "source_label": source_label
        if source_label is not None
        else getattr(data, "source_label", "Mockdata"),
        "source_message": source_message
        if source_message is not None
        else getattr(data, "source_message", "Lokale fallback"),
        "source_warning": source_warning
        if source_warning is not None
        else getattr(data, "source_warning", ""),
        "google_debug": google_debug if google_debug is not None else getattr(data, "google_debug", {}),
        "transactions": getattr(data, "transactions", pd.DataFrame(columns=TRANSACTION_VIEW_COLUMNS)),
        "price_quotes": _normalise_price_quotes(
            getattr(data, "price_quotes", None),
            data.portfolio,
            data.historie,
        ),
    }
    try:
        return replace(data, **values)
    except (TypeError, ValueError):
        return MockFinanceData(
            portfolio=data.portfolio,
            saldi=data.saldi,
            historie=data.historie,
            dividend_total=data.dividend_total,
            **values,
        )


def extract_price_quotes(portfolio: pd.DataFrame) -> dict[str, float]:
    return {ticker: float(quote["price"]) for ticker, quote in build_price_quotes(portfolio).items()}


def build_price_quotes(
    portfolio: pd.DataFrame,
    historie: pd.DataFrame | None = None,
) -> dict[str, dict[str, object]]:
    current_prices = _extract_current_prices(portfolio)
    return {
        ticker: {
            "ticker": ticker,
            "label": PRICE_QUOTE_LABELS[ticker],
            "price": current_prices[ticker],
            "performance": _build_price_performance(historie, PRICE_HISTORY_COLUMNS[ticker]),
        }
        for ticker in PRICE_QUOTE_TICKERS
    }


def _extract_current_prices(portfolio: pd.DataFrame) -> dict[str, float]:
    if portfolio.empty or "Ticker" not in portfolio.columns or "Koers" not in portfolio.columns:
        return {ticker: 0.0 for ticker in PRICE_QUOTE_TICKERS}

    quotes: dict[str, float] = {}
    tickers = portfolio["Ticker"].astype(str).str.upper()
    for ticker in PRICE_QUOTE_TICKERS:
        rows = portfolio.loc[tickers == ticker]
        quotes[ticker] = float(rows["Koers"].iloc[0]) if not rows.empty else 0.0
    return quotes


def _normalise_price_quotes(
    price_quotes: object,
    portfolio: pd.DataFrame,
    historie: pd.DataFrame,
) -> dict[str, dict[str, object]]:
    if not isinstance(price_quotes, dict):
        return build_price_quotes(portfolio, historie)

    normalised = build_price_quotes(portfolio, historie)
    for ticker in PRICE_QUOTE_TICKERS:
        quote = price_quotes.get(ticker)
        if isinstance(quote, int | float):
            normalised[ticker]["price"] = float(quote)
        elif isinstance(quote, dict):
            normalised[ticker] = {
                **normalised[ticker],
                **quote,
                "performance": quote.get("performance") or normalised[ticker]["performance"],
            }
    return normalised


def _build_price_performance(
    historie: pd.DataFrame | None,
    column: str,
) -> dict[str, dict[str, object]]:
    empty = {
        label: {"delta": None, "percentage": None, "tone": "neutral"}
        for label in (*PRICE_PERFORMANCE_PERIODS.keys(), "YTD")
    }
    if historie is None or historie.empty or column not in historie.columns:
        return empty

    latest = _get_latest_valid_history_point(historie, column)
    if latest is None:
        return empty

    latest_date, latest_value = latest
    performance: dict[str, dict[str, object]] = {}
    for label, days_back in PRICE_PERFORMANCE_PERIODS.items():
        target_date = latest_date - pd.Timedelta(days=days_back)
        performance[label] = _build_performance_entry(
            latest_value,
            _get_valid_history_value_on_or_before(historie, column, target_date),
        )

    performance["YTD"] = _build_performance_entry(
        latest_value,
        _get_valid_history_value_on_or_before(historie, column, _ytd_reference_date(latest_date)),
    )
    return performance


def _build_performance_entry(
    current_value: float,
    reference_value: float | None,
) -> dict[str, object]:
    if reference_value is None or reference_value == 0:
        return {"delta": None, "percentage": None, "tone": "neutral"}
    delta = current_value - reference_value
    percentage = (delta / reference_value) * 100
    return {
        "delta": delta,
        "percentage": percentage,
        "tone": _value_tone(delta),
    }


def _get_latest_valid_history_point(
    historie: pd.DataFrame,
    column: str,
) -> tuple[pd.Timestamp, float] | None:
    series = pd.to_numeric(historie[column], errors="coerce")
    valid = historie.loc[historie["Datum"].notna() & series.notna() & (series > 0)].copy()
    if valid.empty:
        return None
    valid["_value"] = series.loc[valid.index]
    row = valid.sort_values("Datum").iloc[-1]
    return pd.Timestamp(row["Datum"]), float(row["_value"])


def _get_valid_history_value_on_or_before(
    historie: pd.DataFrame,
    column: str,
    target_date: pd.Timestamp,
) -> float | None:
    series = pd.to_numeric(historie[column], errors="coerce")
    valid = historie.loc[
        historie["Datum"].notna()
        & series.notna()
        & (series > 0)
        & (historie["Datum"] <= target_date)
    ].copy()
    if valid.empty:
        return None
    valid["_value"] = series.loc[valid.index]
    return float(valid.sort_values("Datum")["_value"].iloc[-1])


def _ytd_reference_date(latest_date: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=int(latest_date.year), month=1, day=31)


def _value_tone(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def build_google_sheets_diagnostics() -> dict[str, str]:
    credentials_path = _credentials_path()
    return {
        "GOOGLE_SHEET_ID gevonden": _yes_no(bool(os.getenv("GOOGLE_SHEET_ID", "").strip())),
        "GOOGLE_SERVICE_ACCOUNT_FILE gevonden": _yes_no(
            bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip())
        ),
        "Credentials-pad gevonden": _yes_no(bool(credentials_path)),
        "Credentials-pad": str(credentials_path) if credentials_path else "n.v.t.",
        "Credentials-bestand bestaat": _yes_no(
            credentials_path.exists() if credentials_path else False
        ),
        "Geprobeerde tabbladen": ", ".join(ATTEMPTED_SHEETS),
        "Foutmelding": "",
    }


def is_google_debug_ui_enabled() -> bool:
    return os.getenv(DEBUG_UI_ENV, "").strip().lower() in {"1", "true", "yes", "ja"}


def _log_google_sheets_diagnostics(diagnostics: dict[str, str]) -> None:
    LOGGER.warning(
        "Google Sheets debug: GOOGLE_SHEET_ID gevonden=%s; "
        "credentials-pad gevonden=%s; credentials-bestand bestaat=%s",
        diagnostics["GOOGLE_SHEET_ID gevonden"],
        diagnostics["Credentials-pad gevonden"],
        diagnostics["Credentials-bestand bestaat"],
    )


def parse_portfolio_sheet(records: Iterable[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in records:
        ticker = str(_get_cell(record, ["Ticker"]) or "").strip()
        if not ticker:
            continue

        category = _normalise_category(str(_get_cell(record, ["Categorie"]) or ""), ticker)
        amount = parse_number(_get_cell(record, ["Aantal"]))
        invested = parse_number(_get_cell(record, ["Inleg", "Ingelegd vermogen"]))
        price = parse_number(_get_cell(record, ["Koers", "Koers (EUR)"]))
        value = parse_number(_get_cell(record, ["Waarde", "Waarde (EUR)"]))
        profit = parse_number(_get_cell(record, ["Winst", "Winst (EUR)"]))
        roi = parse_number(_get_cell(record, ["ROI %", "ROI", "Rendement"]))

        if value is None and amount is not None and price is not None:
            value = amount * price
        if profit is None and value is not None and invested is not None:
            profit = value - invested
        if invested is None and value is not None and profit is not None:
            invested = value - profit
        if price is None and value is not None and amount:
            price = value / amount
        if roi is None and invested not in (None, 0) and profit is not None:
            roi = (profit / invested) * 100

        rows.append(
            {
                "Categorie": category,
                "Ticker": ticker,
                "Aantal": amount or 0.0,
                "Inleg": invested or 0.0,
                "Koers": price or 0.0,
                "Waarde": value or 0.0,
                "Winst": profit or 0.0,
                "ROI %": roi or 0.0,
            }
        )

    return pd.DataFrame(rows, columns=PORTFOLIO_COLUMNS)


def parse_saldi_sheet(records: Iterable[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in records:
        account = str(_get_cell(record, ["Account"]) or "").strip()
        if not account:
            continue
        rows.append(
            {
                "Account": account,
                "Huidig Saldo": parse_number(_get_cell(record, ["Huidig Saldo"])) or 0.0,
            }
        )
    return pd.DataFrame(rows, columns=SALDI_COLUMNS)


def parse_historie_sheet(records: Iterable[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in records:
        parsed_date = parse_date(_get_cell(record, ["Datum"]))
        if pd.isna(parsed_date):
            continue

        row = {"Datum": parsed_date}
        for column in HISTORIE_COLUMNS:
            if column == "Datum":
                continue
            value = parse_number(_get_cell(record, [column]))
            row[column] = value if column in PRICE_HISTORY_COLUMNS.values() else value or 0.0
        rows.append(row)

    historie = pd.DataFrame(rows, columns=HISTORIE_COLUMNS)
    if not historie.empty:
        historie = historie.sort_values("Datum").reset_index(drop=True)
    return historie


def calculate_dividend_total(records: Iterable[dict[str, object]]) -> float | None:
    total = 0.0
    found_dividend = False
    for record in records:
        transaction_type = str(_get_cell(record, ["Type"]) or "").strip().lower()
        if transaction_type != "dividend":
            continue
        found_dividend = True
        total += parse_number(_get_cell(record, ["Totaal"])) or 0.0
    return total if found_dividend else None


def parse_transaction_sheet(records: Iterable[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in records:
        ticker = str(_get_cell(record, ["Ticker"]) or "").strip()
        if not ticker:
            continue

        rows.append(
            {
                "Sheet rij": _parse_sheet_row(record.get("Sheet rij")),
                "Datum": str(_get_cell(record, ["Datum"]) or "").strip(),
                "Ticker": ticker,
                "Type": str(_get_cell(record, ["Type"]) or "").strip(),
                "Aantal": _get_cell(record, ["Aantal"]) or "",
                "Prijs per stuk": _get_cell(record, ["Prijs per stuk"]) or "",
                "Kosten": _get_cell(record, ["Kosten"]) or "",
                "Totaal": _get_cell(record, ["Totaal"]) or "",
                "Valuta": str(_get_cell(record, ["Valuta"]) or "").strip(),
            }
        )

    columns = ["Sheet rij", *TRANSACTION_COLUMNS]
    return pd.DataFrame(rows, columns=columns)


def parse_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    text = (
        text.replace("\u20ac", "")
        .replace("\u00e2\u201a\u00ac", "")
        .replace("EUR", "")
        .replace("\u00a0", "")
        .replace(" ", "")
        .strip()
    )
    is_percentage = text.endswith("%")
    text = text.rstrip("%")
    text = text.replace("'", "")

    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif "." in text and _looks_like_dutch_thousands(text):
        text = text.replace(".", "")

    try:
        parsed = float(text)
    except ValueError:
        return None

    return parsed if not is_percentage else parsed


def _looks_like_dutch_thousands(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d{1,3}(\.\d{3})+", value))


def parse_date(value: object):
    if value is None or str(value).strip() == "":
        return pd.NaT
    if isinstance(value, int | float):
        return pd.to_datetime(value, unit="D", origin="1899-12-30", errors="coerce")
    return pd.to_datetime(value, dayfirst=True, errors="coerce")


def _parse_sheet_row(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _credentials_path() -> Path | None:
    credentials_file = (
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    )
    if not credentials_file:
        return None
    return Path(credentials_file).expanduser()


def _safe_error_message(exc: Exception) -> str:
    message = str(exc) or exc.__class__.__name__
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
    if sheet_id:
        message = message.replace(sheet_id, "[GOOGLE_SHEET_ID verborgen]")
    return message


def _yes_no(value: bool) -> str:
    return "ja" if value else "nee"


def _get_cell(record: dict[str, object], candidates: list[str]) -> object | None:
    normalised_record = {_normalise_key(key): value for key, value in record.items()}
    for candidate in candidates:
        value = normalised_record.get(_normalise_key(candidate))
        if value not in ("", None):
            return value
    return None


def _normalise_key(value: object) -> str:
    return (
        str(value)
        .lower()
        .replace("\u20ac", "")
        .replace("\u00e2\u201a\u00ac", "")
        .replace("(eur)", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .strip()
    )


def _normalise_category(category: str, ticker: str) -> str:
    if category.strip().lower() == "crypto" or ticker.upper() == "BTC":
        return "Crypto"
    return "Aandelen"


def _google_config_present() -> bool:
    return bool(
        os.getenv("GOOGLE_SHEET_ID")
        or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
