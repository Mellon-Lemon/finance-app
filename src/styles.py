import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --fc-border: rgba(148, 163, 184, 0.28);
                --fc-border-soft: rgba(148, 163, 184, 0.18);
                --fc-muted: #8a94a6;
                --fc-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            }

            [data-testid="stAppViewContainer"] {
                background:
                    linear-gradient(180deg, rgba(37, 99, 235, 0.05), transparent 18rem),
                    var(--background-color);
            }

            .block-container {
                max-width: 1160px;
                padding: 1rem 0.9rem 2.5rem;
            }

            @media (min-width: 768px) {
                .block-container {
                    padding: 1.35rem 1.75rem 3rem;
                }
            }

            .block-container h1 {
                font-size: 2rem;
                line-height: 1.1;
                margin: 0;
            }

            .block-container h3 {
                font-size: 1.25rem;
                line-height: 1.2;
                margin-bottom: 0.65rem;
            }

            [data-testid="stCaptionContainer"] {
                color: var(--fc-muted);
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0;
            }

            hr {
                margin: 0.85rem 0 1rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: var(--secondary-background-color);
                border: 1px solid var(--fc-border);
                border-radius: 8px;
                box-shadow: var(--fc-shadow);
                padding: 1.05rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
                gap: 0.45rem;
            }

            div[data-testid="stMetric"] {
                background: transparent;
                border: 0;
                padding: 0;
            }

            div[data-testid="stMetricLabel"] p {
                color: var(--fc-muted);
                font-size: 0.82rem;
                font-weight: 760;
            }

            div[data-testid="stMetricValue"] {
                font-size: 1.75rem;
                font-weight: 850;
                line-height: 1.12;
            }

            div[data-testid="stMetricDelta"] {
                font-weight: 760;
            }

            .fc-kpi-value {
                color: var(--text-color);
                font-size: 1.8rem;
                font-weight: 850;
                line-height: 1.08;
                margin: 0.1rem 0 0.45rem;
                white-space: nowrap;
            }

            .fc-kpi-value--primary {
                font-size: 2.55rem;
                letter-spacing: 0;
                margin-top: 0.18rem;
            }

            .fc-kpi-value--secondary {
                font-size: 1.7rem;
            }

            .fc-kpi-badge {
                align-items: center;
                border: 1px solid var(--fc-border-soft);
                border-radius: 999px;
                display: inline-flex;
                font-size: 0.84rem;
                font-weight: 800;
                line-height: 1;
                margin: 0 0 0.45rem;
                padding: 0.36rem 0.58rem;
                width: fit-content;
            }

            .fc-kpi-badge--positive {
                background: rgba(22, 163, 74, 0.1);
                color: #15803d;
            }

            .fc-kpi-badge--negative {
                background: rgba(220, 38, 38, 0.1);
                color: #b91c1c;
            }

            .fc-kpi-badge--neutral {
                background: rgba(148, 163, 184, 0.12);
                color: var(--fc-muted);
            }

            .fc-submetric {
                background: rgba(148, 163, 184, 0.09);
                border: 1px solid var(--fc-border-soft);
                border-radius: 8px;
                min-height: 3.1rem;
                padding: 0.46rem 0.5rem;
            }

            .fc-submetric span {
                color: var(--fc-muted);
                display: block;
                font-size: 0.72rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 0.18rem;
            }

            .fc-submetric strong {
                color: var(--text-color);
                display: block;
                font-size: 0.78rem;
                font-weight: 800;
                line-height: 1.18;
            }

            .fc-target-value {
                color: var(--text-color);
                font-size: 1.45rem;
                font-weight: 850;
                line-height: 1.12;
                margin: 0.08rem 0 0.15rem;
            }

            .fc-target-percent {
                color: var(--fc-muted);
                font-size: 0.88rem;
                font-weight: 850;
                line-height: 1;
                margin-bottom: 0.1rem;
            }

            div[data-testid="stHorizontalBlock"] {
                gap: 0.75rem;
            }

            div[data-testid="column"] {
                min-width: 0;
            }

            div[data-testid="stHorizontalBlock"] div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] {
                height: 100%;
                min-height: 8rem;
            }

            @media (max-width: 700px) {
                .block-container h1 {
                    font-size: 1.65rem;
                }

                .block-container h3 {
                    font-size: 1.14rem;
                }

                div[data-testid="stHorizontalBlock"] {
                    flex-direction: column;
                }

                div[data-testid="column"] {
                    width: 100% !important;
                }

                .fc-kpi-value--primary {
                    font-size: 2.05rem;
                }

                .fc-kpi-value {
                    white-space: normal;
                }
            }

            [data-testid="stTabs"] [role="tablist"] {
                gap: 0.35rem;
                margin-bottom: 0.45rem;
                overflow-x: auto;
            }

            [data-testid="stTabs"] [role="tab"] {
                border-radius: 8px;
                min-height: 2.55rem;
                padding: 0.4rem 0.75rem;
            }

            div[role="radiogroup"] {
                gap: 0.35rem;
            }

            div[data-testid="stForm"] {
                background: var(--secondary-background-color);
                border: 1px solid var(--fc-border);
                border-radius: 8px;
                box-shadow: var(--fc-shadow);
                padding: 1rem;
            }

            [data-testid="stFormSubmitButton"] button,
            .stButton > button {
                border-radius: 8px;
                font-weight: 760;
                min-height: 2.85rem;
                width: 100%;
            }

            div[data-baseweb="input"],
            div[data-baseweb="select"] > div {
                border-radius: 8px;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid var(--fc-border-soft);
                border-radius: 8px;
                overflow: hidden;
            }

            [data-testid="stImage"] img {
                border-radius: 8px;
                max-height: 220px;
                object-fit: cover;
            }

            .fc-holding-card {
                border: 1px solid var(--fc-border-soft);
                border-radius: 8px;
                margin-bottom: 0.55rem;
                padding: 0.78rem 0.85rem;
            }

            .fc-holding-head {
                align-items: baseline;
                display: flex;
                justify-content: space-between;
                gap: 0.7rem;
                margin-bottom: 0.55rem;
            }

            .fc-holding-head strong {
                color: var(--text-color);
                font-size: 1.08rem;
                font-weight: 850;
                line-height: 1.1;
            }

            .fc-holding-head span {
                color: var(--fc-muted);
                font-size: 0.86rem;
                font-weight: 760;
                text-align: right;
            }

            .fc-holding-grid {
                display: grid;
                grid-template-columns: minmax(4.5rem, 0.7fr) minmax(0, 1.3fr);
                row-gap: 0.28rem;
            }

            .fc-holding-grid span {
                color: var(--fc-muted);
                font-size: 0.8rem;
                font-weight: 750;
            }

            .fc-holding-grid strong {
                color: var(--text-color);
                font-size: 0.88rem;
                font-weight: 820;
                text-align: right;
            }

            .fc-holding-profit--positive {
                color: #15803d !important;
            }

            .fc-holding-profit--negative {
                color: #b91c1c !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
