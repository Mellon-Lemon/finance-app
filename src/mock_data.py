from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class MockFinanceData:
    portfolio: pd.DataFrame
    saldi: pd.DataFrame
    historie: pd.DataFrame
    dividend_total: float
    transactions: pd.DataFrame = field(default_factory=pd.DataFrame)
    price_quotes: dict[str, object] = field(default_factory=dict)
    source_label: str = "Mockdata"
    source_message: str = "Lokale fallback"
    source_warning: str = ""
    google_debug: dict[str, str] = field(default_factory=dict)


def load_mock_data() -> MockFinanceData:
    portfolio = _build_portfolio()
    historie = _build_historie()
    return MockFinanceData(
        portfolio=portfolio,
        saldi=_build_saldi(),
        historie=historie,
        dividend_total=84.20,
        transactions=_build_transactions(),
        price_quotes=_build_price_quotes(portfolio, historie),
    )


def _build_portfolio() -> pd.DataFrame:
    rows = [
        {
            "Categorie": "Crypto",
            "Ticker": "BTC",
            "Aantal": 0.082345,
            "Inleg": 4200.0,
            "Koers": 70500.0,
        },
        {
            "Categorie": "Crypto",
            "Ticker": "ETH",
            "Aantal": 1.75,
            "Inleg": 3900.0,
            "Koers": 3100.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "TSWE",
            "Aantal": 86.0,
            "Inleg": 3300.0,
            "Koers": 40.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "ASML",
            "Aantal": 4.0,
            "Inleg": 2300.0,
            "Koers": 710.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "AAPL",
            "Aantal": 18.0,
            "Inleg": 2800.0,
            "Koers": 205.0,
        },
    ]
    portfolio = pd.DataFrame(rows)
    portfolio["Waarde"] = portfolio["Aantal"] * portfolio["Koers"]
    portfolio["Winst"] = portfolio["Waarde"] - portfolio["Inleg"]
    portfolio["ROI %"] = (portfolio["Winst"] / portfolio["Inleg"]) * 100
    return portfolio[
        ["Categorie", "Ticker", "Aantal", "Inleg", "Koers", "Waarde", "Winst", "ROI %"]
    ]


def _build_saldi() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Account": "Spaar", "Huidig Saldo": 5200.0},
            {"Account": "Vakanties", "Huidig Saldo": 1800.0},
            {"Account": "Vrije ruimte", "Huidig Saldo": 950.0},
        ]
    )


def _build_price_quotes(portfolio: pd.DataFrame, historie: pd.DataFrame) -> dict[str, dict[str, object]]:
    quotes: dict[str, float] = {}
    for ticker in ("BTC", "TSWE"):
        rows = portfolio.loc[portfolio["Ticker"].astype(str).str.upper() == ticker]
        quotes[ticker] = float(rows["Koers"].iloc[0]) if not rows.empty else 0.0
    return {
        "BTC": {
            "ticker": "BTC",
            "label": "Bitcoin",
            "price": quotes["BTC"],
            "performance": _build_demo_performance(historie, "BTC Koers"),
        },
        "TSWE": {
            "ticker": "TSWE",
            "label": "TSWE",
            "price": quotes["TSWE"],
            "performance": _build_demo_performance(historie, "TSWE Koers"),
        },
    }


def _build_historie() -> pd.DataFrame:
    dates = pd.to_datetime(
        [
            "2025-07-31",
            "2025-08-31",
            "2025-09-30",
            "2025-10-31",
            "2025-11-30",
            "2025-12-31",
            "2026-01-31",
            "2026-02-28",
            "2026-03-31",
            "2026-04-30",
            "2026-05-09",
        ]
    )
    spaar = [3600, 3725, 3900, 4100, 4325, 4550, 4700, 4875, 5000, 5100, 5200]
    vakanties = [900, 960, 1025, 1100, 1180, 1260, 1360, 1480, 1600, 1700, 1800]
    vrije_ruimte = [420, 455, 500, 540, 590, 630, 700, 760, 820, 890, 950]
    crypto = [5600, 5900, 6250, 6800, 7350, 7900, 8400, 9050, 9800, 10550, 11230.32]
    degiro = [7800, 8050, 8300, 8620, 8900, 9200, 9480, 9820, 10100, 10320, 10445.00]
    crypto_inleg = [6200, 6500, 6800, 7000, 7200, 7500, 7700, 7900, 8100, 8100, 8100]
    degiro_inleg = [6200, 6500, 6900, 7200, 7600, 8000, 8300, 8500, 8500, 8500, 8500]
    btc_koers = [46000, 48500, 51000, 54800, 58400, 62000, 64200, 66800, 69000, 68200, 70500]
    tswe_koers = [31.8, 32.6, 33.4, 34.9, 36.1, 37.0, 37.6, 38.4, 39.1, 39.6, 40.0]

    historie = pd.DataFrame(
        {
            "Datum": dates,
            "Spaar": spaar,
            "Vakanties": vakanties,
            "Vrije Ruimte": vrije_ruimte,
            "Crypto W.": crypto,
            "Crypto I.": crypto_inleg,
            "DeGiro W.": degiro,
            "DeGiro I.": degiro_inleg,
            "BTC Aant.": [0.025, 0.03, 0.036, 0.044, 0.052, 0.061, 0.068, 0.074, 0.079, 0.081, 0.082345],
            "BTC Koers": btc_koers,
            "TSWE Koers": tswe_koers,
        }
    )
    historie["Belegd Vermogen"] = historie["Crypto W."] + historie["DeGiro W."]
    historie["Inleg Tot."] = historie["Crypto I."] + historie["DeGiro I."]
    historie["Totaal"] = (
        historie["Spaar"]
        + historie["Vakanties"]
        + historie["Vrije Ruimte"]
        + historie["Belegd Vermogen"]
    )
    return historie[
        [
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
    ]


def _build_demo_performance(historie: pd.DataFrame, column: str) -> dict[str, dict[str, object]]:
    latest = float(historie[column].iloc[-1])
    periods = {
        "24u": float(historie[column].iloc[-2]),
        "7d": float(historie[column].iloc[-2]),
        "30d": float(historie[column].iloc[-2]),
        "YTD": float(historie.loc[historie["Datum"] <= pd.Timestamp("2026-01-31"), column].iloc[-1]),
    }
    return {
        label: _demo_performance_entry(latest, reference)
        for label, reference in periods.items()
    }


def _demo_performance_entry(current: float, reference: float) -> dict[str, object]:
    if reference == 0:
        return {"delta": None, "percentage": None, "tone": "neutral"}
    delta = current - reference
    return {
        "delta": delta,
        "percentage": (delta / reference) * 100,
        "tone": "positive" if delta > 0 else "negative" if delta < 0 else "neutral",
    }


def _build_transactions() -> pd.DataFrame:
    rows = [
        {"Sheet rij": 11, "Datum": "06-05-2026", "Ticker": "VWRL", "Type": "Buy", "Aantal": 4.0, "Totaal": 435.0, "Valuta": "EUR"},
        {"Sheet rij": 12, "Datum": "07-05-2026", "Ticker": "ETH", "Type": "Buy", "Aantal": 0.15, "Totaal": 465.0, "Valuta": "EUR"},
        {"Sheet rij": 13, "Datum": "08-05-2026", "Ticker": "ASML", "Type": "Buy", "Aantal": 1.0, "Totaal": 710.0, "Valuta": "EUR"},
        {"Sheet rij": 14, "Datum": "09-05-2026", "Ticker": "AAPL", "Type": "Dividend", "Aantal": 0.0, "Totaal": 14.2, "Valuta": "EUR"},
        {"Sheet rij": 15, "Datum": "10-05-2026", "Ticker": "BTC", "Type": "Buy", "Aantal": 0.006, "Totaal": 423.0, "Valuta": "EUR"},
    ]
    return pd.DataFrame(
        rows,
        columns=["Sheet rij", "Datum", "Ticker", "Type", "Aantal", "Totaal", "Valuta"],
    )
