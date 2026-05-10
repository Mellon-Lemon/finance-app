from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    page_title: str = "Portfolio"
    phase_label: str = "Fase 4.5A"
    base_currency: str = "EUR"
    target_total_wealth: float = 100_000.0
    target_invested_value: float = 100_000.0
    target_btc_amount: float = 0.5


APP_CONFIG = AppConfig()
