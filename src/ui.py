from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Callable, Iterable

import streamlit as st


@dataclass(frozen=True)
class PerformanceMetric:
    label: str
    value: str


@dataclass(frozen=True)
class MetricCard:
    label: str
    value: str
    helper: str = ""
    delta: str | None = None
    performance: tuple[PerformanceMetric, ...] = ()
    variant: str = "standard"


def render_app_header(
    title: str,
    phase_label: str,
    source_label: str = "Mockdata",
    source_message: str = "Lokale fallback",
) -> None:
    st.markdown(
        (
            '<div class="fc-app-header">'
            '<div>'
            f'<div class="fc-app-title">{escape(title)}</div>'
            '<div class="fc-app-subtitle">Vermogen, holdings en snelle invoer</div>'
            '</div>'
            f'{_status_pill_html(source_label)}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_status_pill(source_label: str) -> None:
    st.markdown(_status_pill_html(source_label), unsafe_allow_html=True)


def render_action_bar(
    *,
    data_mode_labels: dict[str, str],
    source_label: str,
    on_reload: Callable[[], None],
    on_refresh: Callable[[], None],
    refresh_disabled: bool,
) -> str:
    with st.container(border=True):
        st.markdown(
            (
                '<div class="fc-action-caption">'
                f'{_status_pill_html(source_label)}'
                '<span>Data opnieuw laden leest alleen opnieuw. Portfolio bijwerken draait refreshPortfolioOnly().</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
        mode_col, reload_col, refresh_col = st.columns([1.45, 0.82, 0.9], gap="small")
        with mode_col:
            selected_mode = st.radio(
                "Datamodus",
                options=list(data_mode_labels.keys()),
                format_func=lambda value: data_mode_labels[value],
                key="data_mode",
                horizontal=True,
            )
        with reload_col:
            if st.button("Data opnieuw laden", type="secondary", key="reload_data_button"):
                on_reload()
        with refresh_col:
            if st.button(
                "Portfolio bijwerken",
                type="secondary",
                key="refresh_portfolio_button",
                disabled=refresh_disabled,
            ):
                on_refresh()

        if selected_mode == "demo":
            st.caption("Demo / Mockdata gebruikt alleen fictieve data en schrijft nooit naar Google Sheets.")
        elif source_label != "Live Google Sheets":
            st.caption("Fallback actief: write-back, delete en Portfolio bijwerken blijven uitgeschakeld.")

    return selected_mode


def render_icon_nav(active_tab: str, labels: dict[str, str]) -> str:
    selected = active_tab
    with st.container(border=True):
        columns = st.columns(len(labels), gap="small")
        for column, (tab, label) in zip(columns, labels.items()):
            with column:
                is_active = tab == active_tab
                if st.button(
                    label,
                    key=f"nav_{_safe_key(tab)}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    selected = tab
                    st.session_state["active_tab"] = tab
    return selected


def render_section_header(kicker: str, title: str) -> None:
    st.markdown(
        (
            '<div class="fc-section-header">'
            f'<span>{escape(kicker)}</span>'
            f'<h3>{escape(title)}</h3>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_primary_metric_card(label: str, value: str, helper: str = "") -> None:
    render_metric_card(MetricCard(label, value, helper, variant="primary"))


def render_metric_card(card: MetricCard) -> None:
    tone = _delta_tone(card.delta or "")
    performance = "".join(
        (
            '<div class="fc-chip">'
            f'<span>{escape(metric.label)}</span>'
            f'<strong>{escape(metric.value)}</strong>'
            '</div>'
        )
        for metric in card.performance
    )
    delta = (
        f'<div class="fc-kpi-badge fc-kpi-badge--{tone}">{escape(card.delta)}</div>'
        if card.delta
        else ""
    )
    helper = f'<div class="fc-card-helper">{escape(card.helper)}</div>' if card.helper else ""
    st.markdown(
        (
            f'<div class="fc-card fc-card--{card.variant}">'
            f'<div class="fc-card-label">{escape(card.label)}</div>'
            f'<div class="fc-kpi-value fc-kpi-value--{card.variant}">{escape(card.value)}</div>'
            f'{delta}'
            f'{helper}'
            f'<div class="fc-chip-row">{performance}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_balance_card(label: str, value: str, helper: str = "", icon: str = "") -> None:
    icon_markup = f'<div class="fc-balance-icon">{escape(icon)}</div>' if icon else ""
    helper_markup = f'<div class="fc-card-helper">{escape(helper)}</div>' if helper else ""
    st.markdown(
        (
            '<div class="fc-balance-card">'
            f'{icon_markup}'
            f'<div class="fc-card-label">{escape(label)}</div>'
            f'<div class="fc-kpi-value">{escape(value)}</div>'
            f'{helper_markup}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_metric_grid(cards: Iterable[MetricCard], columns: int = 3) -> None:
    card_list = list(cards)
    for start in range(0, len(card_list), columns):
        row = card_list[start : start + columns]
        cols = st.columns(len(row), gap="medium")
        for col, card in zip(cols, row):
            with col:
                render_metric_card(card)


def render_target_card(
    title: str,
    current_value: str,
    target_value: str,
    progress: float,
    helper: str,
) -> None:
    bounded_progress = max(0.0, min(progress, 1.0))
    st.markdown(
        (
            '<div class="fc-card fc-target-card">'
            f'<div class="fc-target-title">{escape(title)}</div>'
            '<div class="fc-target-row">'
            f'<strong>{escape(current_value)}</strong>'
            f'<span>{escape(target_value)}</span>'
            '</div>'
            f'<div class="fc-progress"><div style="width:{bounded_progress:.0%}"></div></div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_holding_card(
    *,
    ticker: str,
    quantity: str,
    invested: str,
    value: str,
    profit: str,
    roi: str,
    profit_value: float = 0.0,
) -> None:
    tone = _value_tone(profit_value)
    st.markdown(
        (
            '<div class="fc-holding-card">'
            '<div class="fc-holding-head">'
            f'<strong>{escape(ticker)}</strong>'
            f'<span>{escape(quantity)}</span>'
            '</div>'
            '<div class="fc-holding-grid">'
            f'<span>Inleg</span><strong>{escape(invested)}</strong>'
            f'<span>Waarde</span><strong>{escape(value)}</strong>'
            f'<span>Winst</span><strong class="fc-holding-profit--{tone}">{escape(profit)}</strong>'
            f'<span>ROI</span><strong>{escape(roi)}</strong>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_transaction_item(
    *,
    ticker: str,
    detail: str,
    amount: str,
    sub_amount: str = "",
) -> None:
    sub_amount_markup = f'<span>{escape(sub_amount)}</span>' if sub_amount else ""
    st.markdown(
        (
            '<div class="fc-transaction-item">'
            '<div>'
            f'<strong>{escape(ticker)}</strong>'
            f'<span>{escape(detail)}</span>'
            '</div>'
            '<div class="fc-transaction-amount">'
            f'{escape(amount)}'
            f'{sub_amount_markup}'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_price_result_card(label: str, value: str, helper: str) -> None:
    st.markdown(
        (
            '<div class="fc-price-card">'
            f'<span>{escape(label)}</span>'
            f'<strong>{escape(value)}</strong>'
            f'<small>{escape(helper)}</small>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_success_panel(label: str, value: str, helper: str) -> None:
    st.markdown(
        (
            '<div class="fc-success-panel">'
            f'<span>{escape(label)}</span>'
            f'<strong>{escape(value)}</strong>'
            f'<small>{escape(helper)}</small>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, helper: str) -> None:
    st.markdown(
        (
            '<div class="fc-empty-state">'
            f'<strong>{escape(title)}</strong>'
            f'<span>{escape(helper)}</span>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def _delta_tone(value: str) -> str:
    if value.startswith("+"):
        return "positive"
    if value.startswith("-"):
        return "negative"
    return "neutral"


def _value_tone(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def _status_tone(source_label: str) -> str:
    if source_label == "Live Google Sheets":
        return "live"
    if source_label == "Demo / Mockdata":
        return "demo"
    return "fallback"


def _status_pill_html(source_label: str) -> str:
    tone = _status_tone(source_label)
    return f'<div class="fc-status-pill fc-status-pill--{tone}">{escape(source_label)}</div>'


def _safe_key(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in value)
