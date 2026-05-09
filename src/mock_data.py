from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MockFinanceData:
    portfolio: pd.DataFrame
    saldi: pd.DataFrame
    historie: pd.DataFrame


def load_mock_data() -> MockFinanceData:
    return MockFinanceData(
        portfolio=_build_portfolio(),
        saldi=_build_saldi(),
        historie=_build_historie(),
    )


def _build_portfolio() -> pd.DataFrame:
    rows = [
        {
            "Categorie": "Crypto",
            "Ticker": "BTC",
            "Aantal": 0.1842,
            "Inleg": 7800.0,
            "Koers": 53250.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "GOOGL",
            "Aantal": 8.0,
            "Inleg": 1050.0,
            "Koers": 152.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "AMZN",
            "Aantal": 10.0,
            "Inleg": 1550.0,
            "Koers": 168.0,
        },
        {
            "Categorie": "Aandelen",
            "Ticker": "MSFT",
            "Aantal": 5.0,
            "Inleg": 1700.0,
            "Koers": 390.0,
        },
        {
            "Categorie": "ETF",
            "Ticker": "TSWE",
            "Aantal": 34.0,
            "Inleg": 960.0,
            "Koers": 31.5,
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
            {"Account": "Spaar", "Huidig Saldo": 4350.0},
            {"Account": "Vakanties", "Huidig Saldo": 1250.0},
            {"Account": "Vrije ruimte", "Huidig Saldo": 780.0},
        ]
    )


def _build_historie() -> pd.DataFrame:
    dates = pd.date_range("2025-02-28", periods=15, freq="ME")
    spaar = [3100, 3200, 3350, 3300, 3400, 3500, 3650, 3750, 3900, 4000, 4100, 4200, 4250, 4300, 4350]
    vakanties = [850, 900, 940, 980, 1020, 1050, 1100, 1125, 1150, 1180, 1200, 1220, 1235, 1240, 1250]
    vrije_ruimte = [500, 560, 620, 480, 530, 650, 700, 760, 620, 690, 730, 760, 790, 820, 780]
    crypto = [6100, 5900, 6400, 7050, 7200, 7600, 7350, 7900, 8250, 8700, 9100, 8900, 9400, 9600, 9810]
    degiro = [4050, 4300, 4550, 4700, 4900, 5100, 5350, 5480, 5660, 5830, 6010, 6160, 6350, 6550, 5917]
    crypto_inleg = [5200, 5400, 5600, 5800, 6000, 6200, 6400, 6600, 6800, 7000, 7200, 7400, 7600, 7700, 7800]
    degiro_inleg = [3600, 3800, 4000, 4200, 4400, 4600, 4800, 5000, 5150, 5300, 5450, 5600, 5750, 5900, 5260]

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
            "BTC Aant.": [0.12, 0.125, 0.13, 0.135, 0.14, 0.145, 0.15, 0.155, 0.16, 0.165, 0.17, 0.174, 0.178, 0.181, 0.1842],
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
