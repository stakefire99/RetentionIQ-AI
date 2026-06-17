"""
RetentionIQ AI - Customer Intelligence
Look up an individual customer, see their profile, churn risk score,
and a plain-language explanation of why they're at risk.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from data_processing import get_processed_data
from scoring import score_all_customers
from model_training import load_model, ALL_FEATURES
from theme import (
    inject_global_css, render_brand, render_hero, render_section_header,
    render_risk_ring, render_badge, COLORS,
)

st.set_page_config(page_title="RetentionIQ AI | Customer Intelligence", page_icon="👤", layout="wide")
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
model, encoders, metrics = load_model()
merged = df.merge(scored, on="customerID")

render_hero(
    eyebrow="CUSTOMER INTELLIGENCE",
    title="Customer Lookup",
    subtitle="Search any customer to see their full profile, live churn risk score, and the specific "
              "factors driving that score.",
)

# ---- Customer Selector ----
customer_id = st.selectbox(
    "Customer ID",
    options=merged["customerID"].tolist(),
    index=0,
)

row = merged[merged["customerID"] == customer_id].iloc[0]

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

col_profile, col_risk = st.columns([1.4, 1])

with col_profile:
    render_section_header("Customer Profile")
    st.markdown(
        f"""
        <div class="riq-card">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:18px;">
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">CUSTOMER ID</div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700;">{row['customerID']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">GENDER</div>
                    <div>{row['gender']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">SENIOR CITIZEN</div>
                    <div>{row['SeniorCitizen']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">TENURE</div>
                    <div>{row['tenure']} months</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">MONTHLY CHARGES</div>
                    <div style="font-family:'JetBrains Mono';">${row['MonthlyCharges']:.2f}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">TOTAL CHARGES</div>
                    <div style="font-family:'JetBrains Mono';">${row['TotalCharges']:.2f}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">CONTRACT TYPE</div>
                    <div>{row['Contract']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">PAYMENT METHOD</div>
                    <div>{row['PaymentMethod']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">INTERNET SERVICE</div>
                    <div>{row['InternetService']}</div></div>
                <div><div style="color:{COLORS['text_dim']}; font-size:12px; margin-bottom:3px;">TECH SUPPORT</div>
                    <div>{row['TechSupport']}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_risk:
    render_section_header("Risk Score")
    render_risk_ring(row["ChurnProbability"])
    st.markdown(
        f'<div style="text-align:center; margin-top:6px;">{render_badge(row["RiskLevel"])}</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)

# ---- AI Explanation ----
render_section_header("Why is this customer likely to churn?", "Top contributing factors based on model feature importance and customer profile")

reasons = []
if row["Contract"] == "Month-to-month":
    reasons.append("Month-to-month contract — no long-term commitment in place")
if row["MonthlyCharges"] > df["MonthlyCharges"].median():
    reasons.append(f"High monthly charges (${row['MonthlyCharges']:.2f}, above median of ${df['MonthlyCharges'].median():.2f})")
if row["TechSupport"] == "No":
    reasons.append("No Tech Support add-on subscribed")
if row["OnlineSecurity"] == "No":
    reasons.append("No Online Security add-on subscribed")
if row["tenure"] < 12:
    reasons.append(f"Low tenure — only {row['tenure']} months as a customer")
if row["PaymentMethod"] == "Electronic check":
    reasons.append("Pays via Electronic check, a payment method correlated with higher churn")
if row["InternetService"] == "Fiber optic" and row["TechSupport"] == "No":
    reasons.append("Fiber optic customer without support coverage — common churn cluster")

if not reasons:
    reasons.append("No major risk factors detected — profile aligns with typically loyal customers")

reasons_html = "".join([f'<li style="margin-bottom:8px; color:{COLORS["text"]};">{r}</li>' for r in reasons[:5]])
st.markdown(
    f"""
    <div class="riq-card">
        <ul style="margin:0; padding-left:20px; line-height:1.6;">
            {reasons_html}
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Customer Intelligence</div>',
    unsafe_allow_html=True,
)
