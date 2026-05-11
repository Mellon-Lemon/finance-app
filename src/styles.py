import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --fc-bg: #f6faf8;
                --fc-card: rgba(255, 255, 255, 0.92);
                --fc-card-soft: #f0fbf5;
                --fc-border: rgba(15, 23, 42, 0.09);
                --fc-border-soft: rgba(15, 23, 42, 0.06);
                --fc-muted: #6b7280;
                --fc-text: #102033;
                --fc-green: #08a66a;
                --fc-green-dark: #04784c;
                --fc-blue: #2563eb;
                --fc-orange: #f59e0b;
                --fc-red: #dc2626;
                --fc-shadow: 0 14px 34px rgba(16, 32, 51, 0.08);
                --fc-shadow-soft: 0 8px 18px rgba(16, 32, 51, 0.06);
            }

            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at 10% 0%, rgba(8, 166, 106, 0.09), transparent 28rem),
                    radial-gradient(circle at 88% 8%, rgba(37, 99, 235, 0.08), transparent 24rem),
                    var(--fc-bg);
            }

            .block-container {
                max-width: 1040px;
                padding: 1rem 0.85rem 5.5rem;
            }

            @media (min-width: 768px) {
                .block-container {
                    padding: 1.25rem 1.5rem 4rem;
                }
            }

            [data-testid="stCaptionContainer"] {
                color: var(--fc-muted);
                font-size: 0.78rem;
                font-weight: 650;
                letter-spacing: 0;
            }

            .fc-app-header {
                align-items: center;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(240, 251, 245, 0.92));
                border: 1px solid var(--fc-border);
                border-radius: 24px;
                box-shadow: var(--fc-shadow);
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.8rem;
                padding: 1.1rem 1.15rem;
            }

            .fc-app-title {
                color: var(--fc-text);
                font-size: 1.45rem;
                font-weight: 860;
                line-height: 1.1;
            }

            .fc-app-subtitle {
                color: var(--fc-muted);
                font-size: 0.86rem;
                font-weight: 550;
                margin-top: 0.25rem;
            }

            .fc-status-pill {
                border-radius: 999px;
                font-size: 0.76rem;
                font-weight: 780;
                padding: 0.38rem 0.7rem;
                white-space: nowrap;
            }

            .fc-status-pill--live {
                background: rgba(8, 166, 106, 0.1);
                color: var(--fc-green-dark);
            }

            .fc-status-pill--demo {
                background: rgba(37, 99, 235, 0.1);
                color: #1d4ed8;
            }

            .fc-status-pill--fallback {
                background: rgba(245, 158, 11, 0.12);
                color: #92400e;
            }

            .fc-positive {
                color: var(--fc-green-dark) !important;
            }

            .fc-negative {
                color: var(--fc-red) !important;
            }

            .fc-neutral {
                color: var(--fc-muted) !important;
            }

            .fc-action-caption {
                align-items: center;
                display: flex;
                gap: 0.6rem;
                margin-bottom: 0.55rem;
            }

            .fc-action-caption span:last-child {
                color: var(--fc-muted);
                font-size: 0.74rem;
                font-weight: 650;
                line-height: 1.25;
            }

            .fc-section-header {
                margin: 1.1rem 0 0.55rem;
            }

            .fc-section-header span {
                color: var(--fc-green-dark);
                display: block;
                font-size: 0.76rem;
                font-weight: 820;
                margin-bottom: 0.16rem;
            }

            .fc-section-header h3 {
                color: var(--fc-text);
                font-size: 1.04rem;
                font-weight: 830;
                line-height: 1.15;
                margin: 0;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: var(--fc-card);
                border: 1px solid var(--fc-border);
                border-radius: 20px;
                box-shadow: var(--fc-shadow);
                padding: 1rem;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
                gap: 0.55rem;
            }

            .fc-card {
                background: var(--fc-card);
                border: 1px solid var(--fc-border);
                border-radius: 20px;
                box-shadow: var(--fc-shadow-soft);
                min-height: 100%;
                padding: 1rem;
            }

            .fc-card--primary {
                background:
                    linear-gradient(135deg, rgba(229, 255, 241, 0.92), rgba(255, 255, 255, 0.95)),
                    var(--fc-card-soft);
                box-shadow: var(--fc-shadow);
                overflow: hidden;
                position: relative;
            }

            .fc-card--primary::after {
                background: radial-gradient(circle, rgba(8, 166, 106, 0.16), transparent 62%);
                bottom: -4.4rem;
                content: "";
                height: 9rem;
                position: absolute;
                right: -2.6rem;
                width: 12rem;
            }

            .fc-balance-card {
                background: var(--fc-card);
                border: 1px solid var(--fc-border);
                border-radius: 18px;
                box-shadow: var(--fc-shadow-soft);
                min-height: 7.2rem;
                padding: 0.9rem;
            }

            .fc-balance-icon {
                align-items: center;
                background: rgba(8, 166, 106, 0.08);
                border-radius: 999px;
                color: var(--fc-green-dark);
                display: inline-flex;
                font-size: 0.88rem;
                height: 1.7rem;
                justify-content: center;
                margin-bottom: 0.45rem;
                width: 1.7rem;
            }

            .fc-card-label {
                color: var(--fc-muted);
                font-size: 0.78rem;
                font-weight: 780;
                margin-bottom: 0.38rem;
            }

            .fc-kpi-value {
                color: var(--fc-text);
                font-size: 1.35rem;
                font-weight: 850;
                line-height: 1.08;
                margin: 0.1rem 0 0.42rem;
                white-space: nowrap;
            }

            .fc-kpi-value--primary {
                font-size: 2.35rem;
                letter-spacing: 0;
                margin-top: 0.18rem;
            }

            .fc-card-helper {
                color: var(--fc-muted);
                font-size: 0.78rem;
                font-weight: 560;
                margin-bottom: 0.55rem;
            }

            .fc-kpi-badge {
                align-items: center;
                border-radius: 999px;
                display: inline-flex;
                font-size: 0.78rem;
                font-weight: 800;
                line-height: 1;
                margin: 0 0 0.35rem;
                padding: 0.34rem 0.55rem;
                width: fit-content;
            }

            .fc-kpi-badge--positive {
                background: rgba(8, 166, 106, 0.1);
                color: var(--fc-green-dark);
            }

            .fc-kpi-badge--negative {
                background: rgba(220, 38, 38, 0.09);
                color: var(--fc-red);
            }

            .fc-kpi-badge--neutral {
                background: rgba(107, 114, 128, 0.1);
                color: var(--fc-muted);
            }

            .fc-chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                margin-top: 0.25rem;
            }

            .fc-chip {
                background: rgba(8, 166, 106, 0.06);
                border-radius: 999px;
                display: inline-flex;
                gap: 0.28rem;
                padding: 0.26rem 0.45rem;
            }

            .fc-chip span,
            .fc-chip strong {
                color: var(--fc-muted);
                font-size: 0.7rem;
                line-height: 1.1;
            }

            .fc-chip strong {
                color: var(--fc-green-dark);
                font-weight: 820;
            }

            .fc-chip--negative {
                background: rgba(220, 38, 38, 0.07);
            }

            .fc-chip--negative strong {
                color: var(--fc-red);
            }

            .fc-chip--neutral {
                background: rgba(107, 114, 128, 0.08);
            }

            .fc-chip--neutral strong {
                color: var(--fc-muted);
            }

            .fc-target-card {
                min-height: 5.2rem;
            }

            .fc-target-title {
                color: var(--fc-text);
                font-size: 0.84rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
            }

            .fc-target-row {
                align-items: center;
                display: flex;
                justify-content: space-between;
                gap: 0.5rem;
                margin-bottom: 0.58rem;
            }

            .fc-target-row strong {
                color: var(--fc-text);
                font-size: 0.92rem;
            }

            .fc-target-row span {
                color: var(--fc-muted);
                font-size: 0.76rem;
                font-weight: 680;
                text-align: right;
            }

            .fc-progress {
                background: rgba(15, 23, 42, 0.08);
                border-radius: 999px;
                height: 0.42rem;
                overflow: hidden;
                width: 100%;
            }

            .fc-progress div {
                background: linear-gradient(90deg, var(--fc-green), #58d68d);
                border-radius: 999px;
                height: 100%;
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

            div[role="radiogroup"] {
                gap: 0.35rem;
            }

            div[role="radiogroup"] label {
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid var(--fc-border);
                border-radius: 999px;
                min-height: 2.55rem;
                padding: 0.28rem 0.75rem;
            }

            div[role="radiogroup"] label > div:first-child {
                display: none;
            }

            div[role="radiogroup"] label:has(input:checked) {
                background: linear-gradient(135deg, var(--fc-green), #12b981);
                border-color: transparent;
                color: #ffffff;
                box-shadow: 0 10px 22px rgba(8, 166, 106, 0.22);
            }

            div[data-testid="stForm"] {
                background: var(--fc-card);
                border: 1px solid var(--fc-border);
                border-radius: 20px;
                box-shadow: var(--fc-shadow);
                padding: 1rem;
            }

            [data-testid="stFormSubmitButton"] button,
            .stButton > button {
                border-radius: 14px;
                font-size: 0.84rem;
                font-weight: 760;
                min-height: 2.85rem;
                width: 100%;
            }

            .stButton > button[kind="primary"],
            .stButton > button[data-testid="baseButton-primary"] {
                background: linear-gradient(135deg, var(--fc-green), #11b980);
                border: 0;
                color: white;
            }

            div[data-baseweb="input"],
            div[data-baseweb="select"] > div {
                border-radius: 14px;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid var(--fc-border-soft);
                border-radius: 16px;
                overflow: hidden;
            }

            .fc-holding-card {
                border: 1px solid var(--fc-border-soft);
                border-radius: 18px;
                box-shadow: var(--fc-shadow-soft);
                margin-bottom: 0.55rem;
                padding: 0.88rem 0.95rem;
                background: var(--fc-card);
            }

            .fc-holding-head {
                align-items: baseline;
                display: flex;
                justify-content: space-between;
                gap: 0.7rem;
                margin-bottom: 0.55rem;
            }

            .fc-holding-head strong {
                color: var(--fc-text);
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
                color: var(--fc-text);
                font-size: 0.88rem;
                font-weight: 820;
                text-align: right;
            }

            .fc-holding-profit--positive {
                color: var(--fc-green-dark) !important;
            }

            .fc-holding-profit--negative {
                color: var(--fc-red) !important;
            }

            .fc-transaction-item {
                align-items: center;
                background: var(--fc-card);
                border: 1px solid var(--fc-border-soft);
                border-radius: 18px;
                box-shadow: var(--fc-shadow-soft);
                display: grid;
                gap: 0.7rem;
                grid-template-columns: minmax(0, 1fr) auto;
                margin-bottom: 0.55rem;
                padding: 0.82rem 0.9rem;
            }

            .fc-transaction-item strong {
                color: var(--fc-text);
                font-size: 0.95rem;
            }

            .fc-transaction-item span {
                color: var(--fc-muted);
                display: block;
                font-size: 0.76rem;
                margin-top: 0.16rem;
            }

            .fc-transaction-amount {
                color: var(--fc-text);
                font-weight: 820;
                text-align: right;
                white-space: nowrap;
            }

            .fc-transaction-amount span {
                color: var(--fc-muted);
                display: block;
                font-size: 0.72rem;
                font-weight: 700;
                margin-top: 0.14rem;
            }

            .fc-price-card,
            .fc-success-panel {
                background: linear-gradient(135deg, rgba(229, 255, 241, 0.92), rgba(255, 255, 255, 0.95));
                border: 1px solid rgba(8, 166, 106, 0.15);
                border-radius: 18px;
                padding: 0.9rem 1rem;
            }

            .fc-price-card span,
            .fc-success-panel span {
                color: var(--fc-muted);
                display: block;
                font-size: 0.76rem;
                font-weight: 700;
                margin-bottom: 0.24rem;
            }

            .fc-price-card strong,
            .fc-success-panel strong {
                color: var(--fc-text);
                display: block;
                font-size: 1.35rem;
                font-weight: 860;
            }

            .fc-price-card small,
            .fc-success-panel small {
                color: var(--fc-muted);
                display: block;
                font-size: 0.74rem;
                margin-top: 0.24rem;
            }

            .fc-empty-state {
                background: rgba(255, 255, 255, 0.7);
                border: 1px dashed rgba(15, 23, 42, 0.14);
                border-radius: 18px;
                padding: 1rem;
            }

            .fc-empty-state strong,
            .fc-empty-state span {
                display: block;
            }

            .fc-empty-state strong {
                color: var(--fc-text);
                font-size: 0.95rem;
                font-weight: 820;
                margin-bottom: 0.2rem;
            }

            .fc-empty-state span {
                color: var(--fc-muted);
                font-size: 0.8rem;
            }

            @media (max-width: 700px) {
                .fc-app-header {
                    border-radius: 22px;
                    padding: 0.9rem;
                }

                .fc-app-title {
                    font-size: 1.28rem;
                }

                .fc-app-subtitle {
                    font-size: 0.78rem;
                }

                .fc-status-pill {
                    font-size: 0.68rem;
                    padding: 0.32rem 0.52rem;
                }

                .fc-action-caption {
                    align-items: flex-start;
                    flex-direction: column;
                    gap: 0.35rem;
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
        </style>
        """,
        unsafe_allow_html=True,
    )
