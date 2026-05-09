from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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


HEADER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "header-placeholder.svg"


def render_app_header(
    title: str,
    phase_label: str,
    source_label: str = "Mockdata",
    source_message: str = "Lokale fallback",
) -> None:
    with st.container(border=True):
        st.image(str(HEADER_IMAGE), width="stretch")
        title_col, status_col = st.columns([1, 0.36], gap="medium")
        with title_col:
            st.title(title, anchor=False)
        with status_col:
            st.caption(source_label)


def render_section_header(kicker: str, title: str) -> None:
    st.subheader(title, anchor=False)


def render_metric_card(card: MetricCard) -> None:
    with st.container(border=True):
        st.caption(card.label)
        st.markdown(
            f'<div class="fc-kpi-value fc-kpi-value--{card.variant}">{card.value}</div>',
            unsafe_allow_html=True,
        )
        if card.delta:
            tone = "positive" if card.delta.startswith("+") else "neutral"
            if card.delta.startswith("-"):
                tone = "negative"
            st.markdown(
                f'<div class="fc-kpi-badge fc-kpi-badge--{tone}">{card.delta}</div>',
                unsafe_allow_html=True,
            )
        if card.performance:
            cols = st.columns(len(card.performance), gap="small")
            for col, metric in zip(cols, card.performance):
                with col:
                    st.markdown(
                        (
                            '<div class="fc-submetric">'
                            f'<span>{metric.label}</span>'
                            f'<strong>{metric.value}</strong>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )
        if card.helper:
            st.caption(card.helper)


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
    with st.container(border=True):
        st.caption(title)
        st.markdown(
            f'<div class="fc-target-value">{current_value}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="fc-target-percent">{progress:.0%}</div>',
            unsafe_allow_html=True,
        )
        st.progress(bounded_progress)
        st.caption(f"Doel: {target_value}")
