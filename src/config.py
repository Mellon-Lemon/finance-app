from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    page_title: str = "Finance Companion"
    phase_label: str = "Fase 2"
    base_currency: str = "EUR"
    target_wealth: float = 30_000.0


APP_CONFIG = AppConfig()
