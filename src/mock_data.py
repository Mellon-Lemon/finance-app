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
    source_label: str = "Mockdata"
    source_message: str = "Lokale fallback"
    source_warning: str = ""
    google_debug: dict[str, str] = field(default_factory=dict)


def load_mock_data() -> MockFinanceData:
    return MockFinanceData(
        portfolio=_build_portfolio(),
        saldi=_build_saldi(),
        historie=_build_historie(),
        dividend_total=84.20,
        transactions=_build_transactions(),
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
            "Ticker": "VWRL",
            "Aantal": 36.0,
            "Inleg": 3400.0,
            "Koers": 108.75,
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
        ]
    ]


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
