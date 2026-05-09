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
                padding: 0.95rem;
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

            div[data-testid="stHorizontalBlock"] {
                gap: 0.75rem;
            }

            div[data-testid="column"] {
                min-width: 0;
            }

            div[data-testid="stHorizontalBlock"] div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] {
                height: 100%;
                min-height: 7.6rem;
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
        </style>
        """,
        unsafe_allow_html=True,
    )
