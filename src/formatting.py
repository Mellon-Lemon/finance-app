from __future__ import annotations

import pandas as pd


def format_currency(value: float, currency: str = "EUR", decimals: int = 0) -> str:
    value = _clean_zero(value, decimals)
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
    prefix = "\u20ac" if currency == "EUR" else currency
    return f"{prefix} {formatted}"


def format_currency_eur(value: float, decimals: int = 0) -> str:
    return format_currency(value, "EUR", decimals)


def format_number(value: float, decimals: int = 2) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_percent(value: float, decimals: int = 1) -> str:
    value = _clean_zero(value, decimals)
    return f"{value:.{decimals}f}%".replace(".", ",")


def signed_currency(value: float, currency: str = "EUR") -> str:
    value = _clean_zero(value, 0)
    if value == 0:
        return format_currency(0, currency)
    sign = "+" if value > 0 else "-"
    return f"{sign}{format_currency(abs(value), currency)}"


def format_profit(value: float, decimals: int = 0) -> str:
    return signed_currency(value, "EUR") if decimals == 0 else _signed_currency_decimals(value, decimals)


def format_currency_delta(value: float, decimals: int = 0) -> str:
    return format_profit(value, decimals)


def format_quantity(value: float, ticker: str = "") -> str:
    decimals = 6 if ticker.upper() == "BTC" else 4
    rounded = round(float(value), decimals)
    if rounded == int(rounded):
        return str(int(rounded))
    formatted = f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
    return formatted.replace(".", ",")


def format_quantity_with_unit(value: float, ticker: str = "") -> str:
    quantity = format_quantity(value, ticker)
    return f"{quantity} BTC" if ticker.upper() == "BTC" else f"{quantity} stuks"


def format_date_short(value: object) -> str:
    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%d-%m-%Y")


def _clean_zero(value: float, decimals: int) -> float:
    rounded = round(float(value), decimals)
    return 0.0 if rounded == 0 else float(value)


def _signed_currency_decimals(value: float, decimals: int) -> str:
    value = _clean_zero(value, decimals)
    if value == 0:
        return format_currency(0, "EUR", decimals)
    sign = "+" if value > 0 else "-"
    return f"{sign}{format_currency(abs(value), 'EUR', decimals)}"
