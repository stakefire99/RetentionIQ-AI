"""
RetentionIQ AI - Retention Strategy Center
The decision-support layer: for any at-risk customer, recommend
concrete retention actions with business rationale.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from data_processing import get_processed_data
from scoring import score_all_customers
from analytics import recommend_strategy
from theme import inject_global_css, render_brand, render_hero, render_section_header, render_risk_ring, render_badge, COLORS

st.set_page_config(page_title="RetentionIQ AI | Strategy Center", page_icon="🎯", layout="wide")
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
merged = df.merge(scored, on="customerID")

render_hero(
    eyebrow="RETENTION STRATEGY CENTER",
    title="From Analytics to Action",
    subtitle="Select an at-risk customer and the platform recommends specific, prioritized retention "
              "actions — turning a risk score into a decision.",
)

# ---- Filter to risk tiers, default to High ----
col_filter, col_select = st.columns([1, 2])
with col_filter:
    risk_filter = st.selectbox("Filter by Risk Level", ["High", "Medium", "Low"], index=0)

filtered = merged[merged["RiskLevel"] == risk_filter].sort_values("ChurnProbability", ascending=False)

with col_select:
    customer_id = st.selectbox("Select Customer", filtered["customerID"].tolist())

if len(filtered) == 0:
    st.info("No customers found in this risk tier.")
    st.stop()

row = filtered[filtered["customerID"] == customer_id].iloc[0]

st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])

with col_a:
    render_section_header("Customer Snapshot")
    render_risk_ring(row["ChurnProbability"], size=160)
    st.markdown(f'<div style="text-align:center;">{render_badge(row["RiskLevel"])}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="riq-card" style="margin-top:16px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{COLORS['text_dim']}; font-size:12.5px;">CONTRACT</span>
                <span>{row['Contract']}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{COLORS['text_dim']}; font-size:12.5px;">TENURE</span>
                <span>{row['tenure']} months</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{COLORS['text_dim']}; font-size:12.5px;">MONTHLY CHARGES</span>
                <span style="font-family:'JetBrains Mono';">${row['MonthlyCharges']:.2f}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:{COLORS['text_dim']}; font-size:12.5px;">ANNUAL VALUE</span>
                <span style="font-family:'JetBrains Mono'; color:{COLORS['cyan']};">${row['MonthlyCharges']*12:,.0f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b:
    render_section_header("Recommended Retention Actions", "Prioritized by impact, based on this customer's specific risk profile")
    actions = recommend_strategy(row.to_dict())
    for title, body in actions:
        st.markdown(
            f"""
            <div class="riq-rec-card">
                <div class="riq-rec-title">🎯 {title}</div>
                <div class="riq-rec-body">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    potential_save = row["MonthlyCharges"] * 12 * row["ChurnProbability"]
    st.markdown(
        f"""
        <div class="riq-card" style="border-left: 3px solid {COLORS['emerald']};">
            <div style="font-family:'Sora'; font-weight:700; color:{COLORS['emerald']}; margin-bottom:6px;">Estimated Revenue Protected If Retained</div>
            <div style="font-family:'JetBrains Mono'; font-size:24px; font-weight:700;">${potential_save:,.0f} / year</div>
            <div style="color:{COLORS['text_dim']}; font-size:12.5px; margin-top:4px;">Calculated as annual value × churn probability — the expected revenue saved by successful intervention.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Retention Strategy Center</div>',
    unsafe_allow_html=True,
)
