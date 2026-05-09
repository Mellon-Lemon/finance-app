from __future__ import annotations

import logging
import os
import re
from dataclasses import replace
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.mock_data import MockFinanceData, load_mock_data
from src.sheets_client import GoogleSheetsReadOnlyClient


LOGGER = logging.getLogger(__name__)

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
]


def load_finance_data() -> MockFinanceData:
    _load_local_env()

    try:
        client = GoogleSheetsReadOnlyClient.from_environment()
        data = load_google_sheets_data(client)
        return replace(
            data,
            source_label="Live Google Sheets",
            source_message="Read-only data",
            source_warning="",
        )
    except Exception as exc:
        LOGGER.info("Google Sheets data unavailable; using mockdata fallback: %s", exc)
        warning = ""
        if _google_config_present():
            warning = "Google Sheets kon niet worden gelezen. Mockdata fallback is actief."
        return replace(
            load_mock_data(),
            source_label="Mockdata" if not warning else "Fallback actief",
            source_message="Lokale fallback",
            source_warning=warning,
        )


def load_google_sheets_data(client: GoogleSheetsReadOnlyClient) -> MockFinanceData:
    portfolio = parse_portfolio_sheet(client.get_records("Portfolio"))
    saldi = parse_saldi_sheet(client.get_records("Saldi"))
    historie = parse_historie_sheet(client.get_records("Historie"))
    if portfolio.empty or saldi.empty or historie.empty:
        raise ValueError("Een of meer verplichte Google Sheets tabs bevatten geen data.")

    transactions = client.try_get_records("Transacties")
    dividend_total = calculate_dividend_total(transactions)

    if dividend_total is None:
        dividend_total = load_mock_data().dividend_total

    return MockFinanceData(
        portfolio=portfolio,
        saldi=saldi,
        historie=historie,
        dividend_total=dividend_total,
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
            row[column] = parse_number(_get_cell(record, [column])) or 0.0
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

    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
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


def _load_local_env() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _google_config_present() -> bool:
    return bool(
        os.getenv("GOOGLE_SHEET_ID")
        or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
