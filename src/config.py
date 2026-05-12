from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    page_title: str = "Portfolio"
    phase_label: str = "Fase 5B"
    base_currency: str = "EUR"
    target_total_wealth: float = 100_000.0
    target_invested_value: float = 100_000.0
    target_btc_amount: float = 0.5


APP_CONFIG = AppConfig()


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read config from environment first, then Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    return default


def get_google_sheet_id() -> str | None:
    return get_secret("GOOGLE_SHEET_ID")


def get_apps_script_refresh_url() -> str | None:
    return get_secret("APPS_SCRIPT_REFRESH_URL")


def get_apps_script_refresh_secret() -> str | None:
    return get_secret("APPS_SCRIPT_REFRESH_SECRET")


def get_service_account_info() -> dict[str, Any] | None:
    """
    Supports:
    - local file via GOOGLE_SERVICE_ACCOUNT_FILE
    - cloud JSON string via GOOGLE_SERVICE_ACCOUNT_JSON
    """
    json_string = get_secret("GOOGLE_SERVICE_ACCOUNT_JSON")
    if json_string:
        return json.loads(json_string)

    file_path = get_secret("GOOGLE_SERVICE_ACCOUNT_FILE")
    if file_path and Path(file_path).exists():
        with open(file_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    return None