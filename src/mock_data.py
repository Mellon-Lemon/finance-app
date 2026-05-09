from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class MockFinanceData:
    portfolio: pd.DataFrame
    saldi: pd.DataFrame
    historie: pd.DataFrame
    dividend_total: float
    source_label: str = "Mockdata"
    source_message: str = "Lokale fallback"
    source_warning: str = ""
    google_debug: dict[str, str] = field(default_factory=dict)


def load_mock_data() -> MockFinanceData:
    return MockFinanceData(
        portfolio=_build_portfolio(),
        saldi=_build_saldi(),
        historie=_build_historie(),
        dividend_total=166.51,
    )


def _build_portfolio() -> pd.DataFrame:
    rows = [
        {
            "Categorie": "Crypto",
            "Ticker": "BTC",
            "Aantal": 0.46499113,
            "Inleg": 22000.0,
            "Koers": 68036.56737280384,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "GOOGL",
            "Aantal": 24.0,
            "Inleg": 3400.0,
            "Koers": 172.35,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "AMZN",
            "Aantal": 18.0,
            "Inleg": 2900.0,
            "Koers": 184.20,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "MSFT",
            "Aantal": 12.0,
            "Inleg": 4100.0,
            "Koers": 421.30,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "TSWE",
            "Aantal": 144.0,
            "Inleg": 5200.0,
            "Koers": 41.86,
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
            {"Account": "Spaar", "Huidig Saldo": 15000.0},
            {"Account": "Vakanties", "Huidig Saldo": 3800.0},
            {"Account": "Vrije ruimte", "Huidig Saldo": 3023.16},
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
    spaar = [9800, 10250, 10800, 11250, 11800, 12500, 13200, 13800, 14350, 14800, 15000]
    vakanties = [2300, 2400, 2550, 2700, 2900, 3100, 3250, 3400, 3550, 3700, 3800]
    vrije_ruimte = [1780, 1920, 2050, 2190, 2350, 2500, 2680, 2825, 2920, 2980, 3023.16]
    crypto = [23800, 25150, 24300, 26750, 28100, 29550, 28900, 30150, 30900, 31420, 31636.40]
    degiro = [14200, 14800, 15150, 15850, 16250, 16900, 17200, 17680, 18150, 18410, 18535.44]
    crypto_inleg = [18500, 19000, 19500, 20000, 20500, 21200, 21600, 21800, 22000, 22000, 22000]
    degiro_inleg = [12500, 12900, 13200, 13600, 14000, 14500, 14900, 15200, 15400, 15600, 15600]

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
            "BTC Aant.": [0.36, 0.38, 0.39, 0.405, 0.42, 0.435, 0.445, 0.452, 0.458, 0.462, 0.46499113],
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
