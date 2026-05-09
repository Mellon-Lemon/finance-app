from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import streamlit as st


@dataclass(frozen=True)
class MetricCard:
    label: str
    value: str
    helper: str = ""
    delta: str | None = None


def render_app_header(title: str, phase_label: str) -> None:
    st.caption(f"{phase_label} / Mockdata")
    st.title(title)
    st.divider()


def render_section_header(kicker: str, title: str) -> None:
    st.caption(kicker.upper())
    st.subheader(title)


def render_metric_card(card: MetricCard) -> None:
    with st.container(border=True):
        st.metric(label=card.label, value=card.value, delta=card.delta)
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
