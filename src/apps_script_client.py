from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.config import get_apps_script_refresh_secret, get_apps_script_refresh_url


DEFAULT_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class AppsScriptRefreshResult:
    ok: bool
    configured: bool
    message: str
    status_code: int | None = None
    timestamp: str = ""


def is_apps_script_refresh_configured() -> bool:
    return bool(_refresh_url() and _refresh_secret())


def refresh_portfolio_via_apps_script(
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    action: str = "refresh",
) -> AppsScriptRefreshResult:
    return _call_apps_script_action(action, timeout, "Portfolio bijwerken")


def create_manual_snapshot_via_apps_script(
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> AppsScriptRefreshResult:
    return _call_apps_script_action("manual_snapshot", timeout, "Snapshot maken")


def _call_apps_script_action(
    action: str,
    timeout: int,
    action_label: str,
) -> AppsScriptRefreshResult:
    refresh_url = _refresh_url()
    refresh_secret = _refresh_secret()

    if not refresh_url or not refresh_secret:
        return AppsScriptRefreshResult(
            ok=False,
            configured=False,
            message="Apps Script endpoint is nog niet geconfigureerd.",
        )

    payload = json.dumps({"secret": refresh_secret, "action": action}).encode("utf-8")

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
            message=f"{action_label} faalde met HTTP {exc.code}.",
            status_code=exc.code,
        )
    except (TimeoutError, socket.timeout):
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message=f"{action_label} duurde te lang.",
        )
    except URLError:
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message=f"{action_label} kon het Apps Script endpoint niet bereiken.",
        )

    parsed_body = _parse_json_response(response_body)
    script_ok = _script_response_ok(parsed_body)

    if not 200 <= status_code < 300 or script_ok is False:
        return AppsScriptRefreshResult(
            ok=False,
            configured=True,
            message=f"Apps Script gaf een fout terug bij {action_label.lower()}.",
            status_code=status_code,
        )

    return AppsScriptRefreshResult(
        ok=True,
        configured=True,
        message=_success_message(action),
        status_code=status_code,
        timestamp=_response_timestamp(parsed_body),
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


def _response_timestamp(parsed_body: dict[str, Any] | None) -> str:
    if not parsed_body:
        return ""

    for key in ("completedAt", "timestamp", "time", "createdAt", "created_at"):
        value = parsed_body.get(key)
        if value not in ("", None):
            return str(value)

    return ""


def _success_message(action: str) -> str:
    if action == "manual_snapshot":
        return "Snapshot gemaakt via Apps Script."

    return "Portfolio bijgewerkt via Apps Script."


def _refresh_url() -> str:
    return (get_apps_script_refresh_url() or "").strip()


def _refresh_secret() -> str:
    return (get_apps_script_refresh_secret() or "").strip()