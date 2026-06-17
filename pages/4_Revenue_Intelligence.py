"""
RetentionIQ AI - Revenue Intelligence
Quantifies revenue at risk and surfaces the highest-value customers
who are most likely to churn.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from data_processing import get_processed_data
from scoring import score_all_customers
from analytics import compute_kpis, top_risk_customers
from theme import inject_global_css, render_brand, render_hero, render_section_header, render_badge, COLORS, PLOTLY_TEMPLATE

st.set_page_config(page_title="RetentionIQ AI | Revenue Intelligence", page_icon="💰", layout="wide")
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

df = get_processed_data()
scored = score_all_customers()
kpis = compute_kpis(df)

render_hero(
    eyebrow="REVENUE INTELLIGENCE",
    title="How Much Money Is At Risk?",
    subtitle="Revenue at risk isn't just about customer counts — it's about which customers represent "
              "the largest financial exposure if they churn.",
)

# ---- Top KPI strip ----
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f"""<div class="riq-kpi-card"><div class="riq-kpi-label">Current Active Monthly Revenue</div>
        <div class="riq-kpi-value">${kpis['current_active_monthly_revenue']:,.0f}</div></div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="riq-kpi-card"><div class="riq-kpi-label">Lost Monthly Revenue (Already Churned)</div>
        <div class="riq-kpi-value" style="color:{COLORS['red']};">${kpis['monthly_revenue_at_risk']:,.0f}</div></div>""",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""<div class="riq-kpi-card"><div class="riq-kpi-label">Annualized Revenue At Risk</div>
        <div class="riq-kpi-value" style="color:{COLORS['amber']};">${kpis['annual_revenue_at_risk']:,.0f}</div></div>""",
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

# ---- Top High-Value Risk Customers ----
render_section_header("Top High-Value Risk Customers", "Ranked by revenue exposure (churn probability × annualized spend)")

top_n = top_risk_customers(df, scored, n=15)
display_df = top_n[["customerID", "MonthlyCharges", "Contract", "tenure", "ChurnProbability", "RiskLevel", "RevenueExposure"]].copy()
display_df.columns = ["Customer", "Monthly Charges", "Contract", "Tenure (mo)", "Churn Probability", "Risk", "Annual Revenue Exposure"]
display_df["Monthly Charges"] = display_df["Monthly Charges"].apply(lambda x: f"${x:,.2f}")
display_df["Churn Probability"] = display_df["Churn Probability"].apply(lambda x: f"{x*100:.1f}%")
display_df["Annual Revenue Exposure"] = display_df["Annual Revenue Exposure"].apply(lambda x: f"${x:,.0f}")

st.dataframe(display_df, use_container_width=True, hide_index=True, height=460)

st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)

# ---- Revenue Exposure by Risk Tier ----
render_section_header("Revenue Exposure by Risk Tier", "Total annualized revenue exposure, grouped by risk level")

merged = df.merge(scored, on="customerID")
merged["AnnualRevenue"] = merged["MonthlyCharges"] * 12
exposure_by_tier = merged.groupby("RiskLevel")["AnnualRevenue"].sum().reindex(["High", "Medium", "Low"]).fillna(0)

fig = go.Figure(data=[go.Bar(
    x=exposure_by_tier.index,
    y=exposure_by_tier.values,
    marker_color=[COLORS["red"], COLORS["amber"], COLORS["emerald"]],
    text=[f"${v:,.0f}" for v in exposure_by_tier.values],
    textposition="outside",
    textfont=dict(family="JetBrains Mono", color=COLORS["text"]),
)])
fig.update_layout(
    **PLOTLY_TEMPLATE["layout"],
    height=320,
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_title="Total Annualized Revenue ($)",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Revenue Intelligence</div>',
    unsafe_allow_html=True,
)
