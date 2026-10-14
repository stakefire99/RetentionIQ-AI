"""
RetentionIQ AI - Theme Module
Injects the full custom SaaS-grade visual identity: typography, color
tokens, card system, nav styling, and the signature risk-ring component.
This is what makes the app feel like Salesforce/Tableau rather than a
default Streamlit app.
"""

import streamlit as st

# ---- Design Tokens ----
COLORS = {
    "bg": "#0B1120",
    "bg_alt": "#0E1729",
    "surface": "#131D33",
    "surface_hover": "#172445",
    "border": "#1E2D4D",
    "border_bright": "#2A3F66",
    "text": "#E8EDF7",
    "text_muted": "#8B98B8",
    "text_dim": "#5B6B8C",
    "cyan": "#22D3EE",
    "cyan_dim": "#0E7490",
    "emerald": "#34D399",
    "emerald_dim": "#047857",
    "amber": "#FBBF24",
    "red": "#F87171",
    "red_dim": "#7F1D1D",
}

RISK_COLORS = {
    "High": COLORS["red"],
    "Medium": COLORS["amber"],
    "Low": COLORS["emerald"],
}


def inject_global_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {{
            --bg: {COLORS['bg']};
            --bg-alt: {COLORS['bg_alt']};
            --surface: {COLORS['surface']};
            --surface-hover: {COLORS['surface_hover']};
            --border: {COLORS['border']};
            --border-bright: {COLORS['border_bright']};
            --text: {COLORS['text']};
            --text-muted: {COLORS['text_muted']};
            --text-dim: {COLORS['text_dim']};
            --cyan: {COLORS['cyan']};
            --emerald: {COLORS['emerald']};
            --amber: {COLORS['amber']};
            --red: {COLORS['red']};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        .stApp {{
            background: radial-gradient(circle at 15% 0%, #101b33 0%, var(--bg) 45%) !important;
        }}

        section[data-testid="stSidebar"] {{
            background: var(--bg-alt) !important;
            border-right: 1px solid var(--border);
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            font-family: 'Inter', sans-serif;
        }}

        /* Hide Streamlit chrome we do not need, but NEVER hide the sidebar open arrow */
        #MainMenu, footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{ visibility: hidden; }}
        /* Make the arrow that reopens a collapsed sidebar always visible and clickable */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] {{
            visibility: visible !important;
            display: flex !important;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] button {{ color: #E8EDF8 !important; }}
        /* Remove the in-sidebar close button so visitors cannot collapse it and get stuck */
        [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

        h1, h2, h3 {{
            font-family: 'Sora', sans-serif !important;
            color: var(--text) !important;
            letter-spacing: -0.01em;
        }}

        p, div, span, label {{
            color: var(--text);
        }}

        /* ---- Brand lockup ---- */
        .riq-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 18px 4px 22px 4px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 18px;
        }}
        .riq-brand-mark {{
            width: 34px; height: 34px;
            border-radius: 9px;
            background: linear-gradient(135deg, var(--cyan), var(--emerald));
            display: flex; align-items: center; justify-content: center;
            font-family: 'Sora', sans-serif; font-weight: 800; font-size: 16px;
            color: #06141F;
            flex-shrink: 0;
        }}
        .riq-brand-text {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 16.5px;
            color: var(--text);
            line-height: 1.15;
        }}
        .riq-brand-sub {{
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            color: var(--text-dim);
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        /* ---- Hero ---- */
        .riq-hero {{
            padding: 38px 36px 34px 36px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(34,211,238,0.10), rgba(52,211,153,0.06) 60%, transparent);
            border: 1px solid var(--border-bright);
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }}
        .riq-hero::after {{
            content: "";
            position: absolute; top: -60px; right: -60px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(34,211,238,0.18), transparent 70%);
            pointer-events: none;
        }}
        .riq-hero-eyebrow {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            letter-spacing: 0.12em;
            color: var(--cyan);
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .riq-hero-title {{
            font-family: 'Sora', sans-serif;
            font-weight: 800;
            font-size: 38px;
            color: var(--text);
            margin: 0 0 10px 0;
            line-height: 1.1;
        }}
        .riq-hero-sub {{
            font-family: 'Inter', sans-serif;
            font-size: 15.5px;
            color: var(--text-muted);
            max-width: 620px;
            line-height: 1.55;
            margin: 0;
        }}

        /* ---- KPI Cards ---- */
        .riq-kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px 20px 18px 20px;
            height: 100%;
            transition: border-color 0.15s ease;
        }}
        .riq-kpi-card:hover {{ border-color: var(--border-bright); }}
        .riq-kpi-label {{
            font-family: 'Inter', sans-serif;
            font-size: 12.5px;
            color: var(--text-muted);
            font-weight: 500;
            margin-bottom: 8px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .riq-kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            color: var(--text);
            line-height: 1.1;
        }}
        .riq-kpi-delta {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12.5px;
            margin-top: 6px;
            font-weight: 600;
        }}
        .riq-up {{ color: var(--red); }}
        .riq-down {{ color: var(--emerald); }}
        .riq-flat {{ color: var(--text-dim); }}

        /* ---- Section headers ---- */
        .riq-section-title {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 19px;
            color: var(--text);
            margin: 6px 0 4px 0;
        }}
        .riq-section-sub {{
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: var(--text-dim);
            margin-bottom: 14px;
        }}

        /* ---- Alert / Storyline banner ---- */
        .riq-alert {{
            border-radius: 14px;
            padding: 22px 24px;
            border-left: 4px solid var(--amber);
            background: linear-gradient(90deg, rgba(251,191,36,0.08), rgba(251,191,36,0.02));
            margin-bottom: 22px;
        }}
        .riq-alert-title {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 15.5px;
            color: var(--amber);
            margin-bottom: 8px;
            display: flex; align-items: center; gap: 8px;
        }}
        .riq-alert-body {{
            font-family: 'Inter', sans-serif;
            font-size: 14.5px;
            color: var(--text);
            line-height: 1.65;
        }}
        .riq-alert-body b {{ color: var(--text); font-weight: 700; }}
        .riq-highlight {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--cyan);
            font-weight: 700;
        }}

        /* ---- Generic card ---- */
        .riq-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 22px;
        }}

        /* ---- Badges ---- */
        .riq-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 12px;
            border-radius: 100px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .riq-badge-high {{ background: rgba(248,113,113,0.14); color: var(--red); border: 1px solid rgba(248,113,113,0.3); }}
        .riq-badge-medium {{ background: rgba(251,191,36,0.14); color: var(--amber); border: 1px solid rgba(251,191,36,0.3); }}
        .riq-badge-low {{ background: rgba(52,211,153,0.14); color: var(--emerald); border: 1px solid rgba(52,211,153,0.3); }}

        /* ---- Risk Ring (signature element) ---- */
        .riq-ring-wrap {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 10px 0 4px 0;
        }}
        .riq-ring-value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
        }}

        /* ---- Buttons ---- */
        .stButton > button {{
            background: linear-gradient(135deg, var(--cyan), var(--emerald)) !important;
            color: #06141F !important;
            border: none !important;
            border-radius: 9px !important;
            font-family: 'Sora', sans-serif !important;
            font-weight: 700 !important;
            padding: 0.6rem 1.4rem !important;
            transition: transform 0.12s ease, box-shadow 0.12s ease !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(34,211,238,0.25);
        }}

        /* ---- Inputs ---- */
        .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 8px !important;
        }}
        .stSlider [data-baseweb="slider"] {{ color: var(--cyan); }}

        /* ---- Dataframe ---- */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: 12px;
        }}

        /* ---- Divider ---- */
        .riq-divider {{
            height: 1px;
            background: var(--border);
            margin: 26px 0;
            border: none;
        }}

        /* ---- Metric strip label (nav) ---- */
        .riq-nav-section {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10.5px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 18px 0 6px 4px;
        }}

        /* recommendation card */
        .riq-rec-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 3px solid var(--cyan);
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }}
        .riq-rec-title {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 14.5px;
            color: var(--cyan);
            margin-bottom: 6px;
        }}
        .riq-rec-body {{
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.55;
        }}

        /* footer credit */
        .riq-footer {{
            text-align: center;
            color: var(--text-dim);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            padding: 30px 0 10px 0;
            letter-spacing: 0.04em;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand():
    st.markdown(
        """
        <div class="riq-brand">
            <div class="riq-brand-mark">R</div>
            <div>
                <div class="riq-brand-text">RetentionIQ AI</div>
                <div class="riq-brand-sub">Retention Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(eyebrow: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="riq-hero">
            <div class="riq-hero-eyebrow">{eyebrow}</div>
            <div class="riq-hero-title">{title}</div>
            <p class="riq-hero-sub">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, delta: str = None, delta_direction: str = "flat", icon: str = ""):
    delta_html = ""
    if delta:
        cls = {"up": "riq-up", "down": "riq-down", "flat": "riq-flat"}.get(delta_direction, "riq-flat")
        arrow = {"up": "▲", "down": "▼", "flat": "—"}.get(delta_direction, "—")
        delta_html = f'<div class="riq-kpi-delta {cls}">{arrow} {delta}</div>'

    st.markdown(
        f"""
        <div class="riq-kpi-card">
            <div class="riq-kpi-label"><span>{label}</span><span>{icon}</span></div>
            <div class="riq-kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(risk_level: str) -> str:
    cls = {"High": "riq-badge-high", "Medium": "riq-badge-medium", "Low": "riq-badge-low"}.get(risk_level, "riq-badge-low")
    dot = {"High": "●", "Medium": "●", "Low": "●"}.get(risk_level, "●")
    return f'<span class="riq-badge {cls}">{dot} {risk_level} Risk</span>'


def render_risk_ring(probability: float, size: int = 180):
    """Renders an SVG circular gauge — the signature visual element of the app."""
    pct = max(0, min(1, probability))
    color = COLORS["red"] if pct >= 0.7 else (COLORS["amber"] if pct >= 0.4 else COLORS["emerald"])
    radius = size / 2 - 14
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - pct)
    center = size / 2

    st.markdown(
        f"""
        <div class="riq-ring-wrap">
            <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
                <circle cx="{center}" cy="{center}" r="{radius}" fill="none"
                    stroke="{COLORS['border']}" stroke-width="12" />
                <circle cx="{center}" cy="{center}" r="{radius}" fill="none"
                    stroke="{color}" stroke-width="12" stroke-linecap="round"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    transform="rotate(-90 {center} {center})"
                    style="filter: drop-shadow(0 0 8px {color}66); transition: stroke-dashoffset 0.6s ease;" />
                <text x="{center}" y="{center - 4}" text-anchor="middle"
                    font-family="JetBrains Mono, monospace" font-size="{size*0.19}" font-weight="700"
                    fill="{COLORS['text']}">{pct*100:.0f}%</text>
                <text x="{center}" y="{center + 22}" text-anchor="middle"
                    font-family="Inter, sans-serif" font-size="{size*0.075}"
                    fill="{COLORS['text_muted']}">CHURN RISK</text>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = ""):
    sub_html = f'<div class="riq-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="riq-section-title">{title}</div>
        {sub_html}
        """,
        unsafe_allow_html=True,
    )


PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": COLORS["text_muted"]},
        "xaxis": {"gridcolor": COLORS["border"], "zerolinecolor": COLORS["border"]},
        "yaxis": {"gridcolor": COLORS["border"], "zerolinecolor": COLORS["border"]},
        "legend": {"font": {"color": COLORS["text_muted"]}},
        "colorway": [COLORS["cyan"], COLORS["emerald"], COLORS["amber"], COLORS["red"], COLORS["text_dim"]],
    }
}
