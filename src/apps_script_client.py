from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


REFRESH_URL_ENV = "APPS_SCRIPT_REFRESH_URL"
REFRESH_SECRET_ENV = "APPS_SCRIPT_REFRESH_SECRET"
DEFAULT_TIMEOUT_SECONDS = 60

load_dotenv()


@dataclass(frozen=True)
class AppsScriptRefreshResult:
    ok: bool
    configured: bool
    message: str
    status_code: int | None = None


def is_apps_script_refresh_configured() -> bool:
    return bool(_refresh_url() and _refresh_secret())


def refresh_portfolio_via_apps_script(
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> AppsScriptRefreshResult:
    refresh_url = _refresh_url()
    refresh_secret = _refresh_secret()
    if not refresh_url or not refresh_secret:
        return AppsScriptRefreshResult(
            ok=False,
            configured=False,
            message="Apps Script refresh is nog niet geconfigureerd.",
        )

    payload = json.dumps({"secret": refresh_secret}).encode("utf-8")
    request = Request(
        refresh_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message=f"Portfolio bijwerken faalde met HTTP {exc.code}.",
            status_code=exc.code,
        )
    except (TimeoutError, socket.timeout):
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message="Portfolio bijwerken duurde te lang.",
        )
    except URLError:
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message="Portfolio bijwerken kon het Apps Script endpoint niet bereiken.",
        )

    parsed_body = _parse_json_response(response_body)
    script_ok = _script_response_ok(parsed_body)
    if not 200 <= status_code < 300 or script_ok is False:
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message="Apps Script refresh gaf een fout terug.",
            status_code=status_code,
        )

    return AppsScriptRefreshResult(
        ok=True,
        configured=True,
        message="Portfolio bijgewerkt via Apps Script.",
        status_code=status_code,
    )


def _parse_json_response(response_body: str) -> dict[str, Any] | None:
    if not response_body.strip():
        return None
    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _script_response_ok(parsed_body: dict[str, Any] | None) -> bool | None:
    if not parsed_body:
        return None
    for key in ("ok", "success"):
        value = parsed_body.get(key)
        if isinstance(value, bool):
            return value
    return None


def _refresh_url() -> str:
    return os.getenv(REFRESH_URL_ENV, "").strip()


def _refresh_secret() -> str:
    return os.getenv(REFRESH_SECRET_ENV, "").strip()
