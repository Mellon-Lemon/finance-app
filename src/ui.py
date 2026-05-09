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


HEADER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "header-placeholder.svg"


def render_app_header(title: str, phase_label: str) -> None:
    with st.container(border=True):
        text_col, image_col = st.columns([1.15, 1], gap="large")
        with text_col:
            st.caption(f"{phase_label} / Mockdata")
            st.title(title)
            st.write("Mobiel dashboard voor vermogen, holdings en snelle invoer.")
        with image_col:
            st.image(str(HEADER_IMAGE), width="stretch")


def render_section_header(kicker: str, title: str) -> None:
    st.caption(kicker.upper())
    st.subheader(title)


def render_metric_card(card: MetricCard) -> None:
    with st.container(border=True):
        st.metric(label=card.label, value=card.value, delta=card.delta)
        if card.helper:
            st.caption(card.helper)
        if card.performance:
            performance_line = " | ".join(
                f"{metric.label}: {metric.value}" for metric in card.performance
            )
            st.caption(performance_line)


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
        st.metric(title, current_value)
        st.caption(f"Doel: {target_value}")
        st.progress(bounded_progress, text=f"{progress:.0%}")
        st.caption(helper)
