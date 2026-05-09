from __future__ import annotations


def format_currency(value: float, currency: str = "EUR", decimals: int = 0) -> str:
    value = _clean_zero(value, decimals)
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
    prefix = "\u20ac" if currency == "EUR" else currency
    return f"{prefix} {formatted}"


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 1) -> str:
    value = _clean_zero(value, decimals)
    return f"{value:.{decimals}f}%".replace(".", ",")


def signed_currency(value: float, currency: str = "EUR") -> str:
    value = _clean_zero(value, 0)
    if value == 0:
        return format_currency(0, currency)
    sign = "+" if value > 0 else "-"
    return f"{sign}{format_currency(abs(value), currency)}"


def _clean_zero(value: float, decimals: int) -> float:
    rounded = round(float(value), decimals)
    return 0.0 if rounded == 0 else float(value)
