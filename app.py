"""
RetentionIQ AI - Customer Retention Intelligence Platform
Main entry point: Executive Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))
from data_processing import get_processed_data
from scoring import score_all_customers
from analytics import compute_kpis, contract_churn_multiplier, monthly_churn_trend
from theme import (
    inject_global_css, render_brand, render_hero, render_kpi_card,
    render_section_header, PLOTLY_TEMPLATE, COLORS,
)

st.set_page_config(
    page_title="RetentionIQ AI | Executive Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

with st.sidebar:
    render_brand()
    st.markdown('<div class="riq-nav-section">Platform</div>', unsafe_allow_html=True)
    st.page_link("app.py", label="Executive Dashboard", icon="📊")
    st.page_link("pages/1_Customer_Intelligence.py", label="Customer Intelligence", icon="👤")
    st.page_link("pages/2_Churn_Prediction_Engine.py", label="Prediction Engine", icon="🤖")
    st.page_link("pages/3_Churn_Drivers.py", label="Churn Drivers", icon="📉")
    st.page_link("pages/4_Revenue_Intelligence.py", label="Revenue Intelligence", icon="💰")
    st.page_link("pages/5_Retention_Strategy_Center.py", label="Strategy Center", icon="🎯")
    st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)
    st.caption("Data source: IBM Telco Customer Churn dataset · 7,043 customer records")

# ---- Load data ----
df = get_processed_data()
scored = score_all_customers()
kpis = compute_kpis(df)
contract_stats = contract_churn_multiplier(df)

# ---- Hero ----
render_hero(
    eyebrow="EXECUTIVE DASHBOARD · LIVE",
    title="RetentionIQ AI",
    subtitle="Customer Retention Intelligence Platform — predict customer churn before it happens, "
             "understand why customers leave, and quantify the revenue impact in real time.",
)

# ---- KPI Row ----
high_risk_count = (scored["RiskLevel"] == "High").sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Total Customers", f"{kpis['total_customers']:,}", icon="👥")
with c2:
    render_kpi_card("Churn Rate", f"{kpis['churn_rate']*100:.1f}%", "vs. 15% industry benchmark", "up", icon="⚠️")
with c3:
    render_kpi_card("Retention Rate", f"{kpis['retention_rate']*100:.1f}%", icon="✅")
with c4:
    render_kpi_card("Revenue At Risk", f"${kpis['annual_revenue_at_risk']/1e6:.2f}M", "annualized", "up", icon="💸")
with c5:
    render_kpi_card("High Risk Customers", f"{high_risk_count:,}", f"{high_risk_count/kpis['total_customers']*100:.1f}% of base", "up", icon="🔥")

st.markdown('<div style="height:26px"></div>', unsafe_allow_html=True)

# ---- Executive Storyline ----
mtm_mult = contract_stats["mtm_vs_one_year"]
st.markdown(
    f"""
    <div class="riq-alert">
        <div class="riq-alert-title">⚠️ Retention Alert</div>
        <div class="riq-alert-body">
            The organization currently has a churn rate of <span class="riq-highlight">{kpis['churn_rate']*100:.1f}%</span>,
            well above the typical telecom benchmark of 10&ndash;15%.<br><br>
            Customers on <b>month-to-month contracts</b> are
            <span class="riq-highlight">{mtm_mult:.1f}x</span> more likely to churn than annual subscribers,
            and <span class="riq-highlight">{contract_stats['mtm_vs_two_year']:.1f}x</span> more likely to churn
            than two-year subscribers.<br><br>
            Potential annualized revenue at risk: <span class="riq-highlight">${kpis['annual_revenue_at_risk']:,.0f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Visual Row 1: Churn Distribution + Monthly Trend ----
col1, col2 = st.columns([1, 1.6])

with col1:
    render_section_header("Churn Distribution", "Retained vs. churned customers")
    fig = go.Figure(data=[go.Pie(
        labels=["Retained", "Churned"],
        values=[kpis["retained_count"], kpis["churned_count"]],
        hole=0.62,
        marker=dict(colors=[COLORS["emerald"], COLORS["red"]]),
        textinfo="percent",
        textfont=dict(family="JetBrains Mono", size=14, color=COLORS["text"]),
    )])
    fig.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        showlegend=True,
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text=f"{kpis['churn_rate']*100:.1f}%<br>Churn", x=0.5, y=0.5,
                           font=dict(size=16, family="JetBrains Mono", color=COLORS["text"]), showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    render_section_header("Monthly Churn Trend", "Last 12 months")
    trend = monthly_churn_trend(df)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=trend["Month"], y=trend["ChurnRate"] * 100,
        mode="lines+markers",
        line=dict(color=COLORS["cyan"], width=3, shape="spline"),
        marker=dict(size=6, color=COLORS["cyan"]),
        fill="tozeroy",
        fillcolor="rgba(34,211,238,0.08)",
    ))
    fig2.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Churn Rate (%)",
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Note: trend simulated month-over-month around the dataset's true churn rate for illustrative trending; underlying dataset is a single snapshot without timestamps.")

st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)

# ---- Visual Row 2: Churn by Contract + Revenue ----
col3, col4 = st.columns([1, 1])

with col3:
    render_section_header("Churn by Contract Type", "Month-to-month vs. annual vs. two-year")
    rates = contract_stats["rates"]
    order = ["Month-to-month", "One year", "Two year"]
    fig3 = go.Figure(data=[go.Bar(
        x=order,
        y=[rates.get(o, 0) * 100 for o in order],
        marker_color=[COLORS["red"], COLORS["amber"], COLORS["emerald"]],
        text=[f"{rates.get(o, 0)*100:.1f}%" for o in order],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", color=COLORS["text"]),
    )])
    fig3.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Churn Rate (%)",
        showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    render_section_header("Revenue At Risk", "Current vs. lost vs. at-risk revenue")
    fig4 = go.Figure(data=[go.Bar(
        x=["Active Revenue", "Lost Revenue (Churned)", "Annualized Risk"],
        y=[kpis["current_active_monthly_revenue"], kpis["monthly_revenue_at_risk"], kpis["annual_revenue_at_risk"] / 12],
        marker_color=[COLORS["emerald"], COLORS["red"], COLORS["amber"]],
        text=[f"${v:,.0f}" for v in [kpis["current_active_monthly_revenue"], kpis["monthly_revenue_at_risk"], kpis["annual_revenue_at_risk"] / 12]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", color=COLORS["text"]),
    )])
    fig4.update_layout(
        **PLOTLY_TEMPLATE["layout"],
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Monthly $ (USD)",
        showlegend=False,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Built on IBM Telco Customer Churn Dataset · RandomForest Classification Engine</div>',
    unsafe_allow_html=True,
)
