from __future__ import annotations


def format_currency(value: float, currency: str = "EUR", decimals: int = 0) -> str:
    return f"{currency} {value:,.{decimals}f}"


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def signed_currency(value: float, currency: str = "EUR") -> str:
    sign = "+" if value >= 0 else "-"
    return f"{sign}{format_currency(abs(value), currency)}"
