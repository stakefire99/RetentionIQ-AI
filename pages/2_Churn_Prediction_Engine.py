"""
RetentionIQ AI - Churn Prediction Engine
Interactive what-if tool: input a hypothetical or prospective customer
profile and get a live churn probability with risk breakdown.
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from model_training import load_model, predict_churn, CATEGORICAL_FEATURES, NUMERIC_FEATURES
from theme import (
    inject_global_css, render_brand, render_hero, render_section_header,
    render_risk_ring, render_badge, COLORS, PLOTLY_TEMPLATE,
)

st.set_page_config(page_title="RetentionIQ AI | Prediction Engine", page_icon="🤖", layout="wide")
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

model, encoders, metrics = load_model()

render_hero(
    eyebrow="CHURN PREDICTION ENGINE",
    title="Predict Churn for Any Customer Profile",
    subtitle="Enter a customer's attributes to generate a live churn probability, risk level, and a "
              "breakdown of which factors are driving that prediction.",
)

render_section_header("Customer Inputs")

with st.form("prediction_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
        age_proxy = st.selectbox("Senior Citizen", ["No", "Yes"])
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        monthly_charges = st.slider("Monthly Charges ($)", 18.0, 120.0, 70.0, step=0.5)
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])

    with c2:
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        payment_method = st.selectbox(
            "Payment Method",
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        )

    with c3:
        gender = st.selectbox("Gender", ["Male", "Female"])
        partner = st.selectbox("Has Partner", ["Yes", "No"])
        dependents = st.selectbox("Has Dependents", ["Yes", "No"])
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        paperless = st.selectbox("Paperless Billing", ["Yes", "No"])

    submitted = st.form_submit_button("⚡ Predict Churn")

if submitted:
    total_charges = monthly_charges * max(tenure, 1)
    input_dict = {
        "gender": gender,
        "SeniorCitizen": age_proxy,
        "Partner": partner,
        "Dependents": dependents,
        "PhoneService": phone_service,
        "MultipleLines": "No",
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": tech_support,
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment_method,
        "tenure": tenure,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }

    proba, risk = predict_churn(model, encoders, input_dict)

    st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)
    render_section_header("Prediction Result")

    r1, r2, r3 = st.columns([1, 1, 1.4])

    with r1:
        render_risk_ring(proba)
        st.markdown(f'<div style="text-align:center;">{render_badge(risk)}</div>', unsafe_allow_html=True)

    with r2:
        st.markdown(
            f"""
            <div class="riq-card" style="text-align:center; padding-top:34px; padding-bottom:34px;">
                <div style="color:{COLORS['text_dim']}; font-size:12.5px; margin-bottom:8px;">CHURN PROBABILITY</div>
                <div style="font-family:'JetBrains Mono'; font-size:34px; font-weight:700; color:{COLORS['text']};">{proba*100:.1f}%</div>
                <div style="margin-top:14px; color:{COLORS['text_dim']}; font-size:12.5px;">MODEL ROC-AUC (OVERALL)</div>
                <div style="font-family:'JetBrains Mono'; font-size:22px; font-weight:700; color:{COLORS['cyan']};">{metrics['roc_auc']:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:
        # Risk breakdown — weight key inputs by their global feature importance,
        # scaled by how "risky" this particular input value is.
        fi = metrics["feature_importance"]

        def risk_contribution(feature, risky_condition):
            base = fi.get(feature, 0)
            return base if risky_condition else base * 0.25

        breakdown = {
            "Contract Type": risk_contribution("Contract", contract == "Month-to-month"),
            "Tenure": risk_contribution("tenure", tenure < 12),
            "Monthly Charges": risk_contribution("MonthlyCharges", monthly_charges > 70),
            "Support Coverage": risk_contribution("TechSupport", tech_support == "No") + risk_contribution("OnlineSecurity", online_security == "No"),
        }
        total = sum(breakdown.values()) or 1
        breakdown = {k: v / total * 100 for k, v in breakdown.items()}

        fig = go.Figure(data=[go.Bar(
            y=list(breakdown.keys()),
            x=list(breakdown.values()),
            orientation="h",
            marker_color=[COLORS["red"], COLORS["amber"], COLORS["cyan"], COLORS["emerald"]],
            text=[f"{v:.0f}%" for v in breakdown.values()],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=COLORS["text"]),
        )])
        fig.update_layout(
            **PLOTLY_TEMPLATE["layout"],
            height=240,
            margin=dict(l=10, r=40, t=10, b=10),
            xaxis_title="Estimated risk-factor weight (%)",
        )
        fig.update_xaxes(range=[0, max(breakdown.values()) * 1.25])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Illustrative weighting: each factor's importance in the model, boosted when this customer's value is a known risk. It is not a per-customer explanation (such as SHAP).")

    if risk == "High":
        st.warning("⚠️ This profile shows a high probability of churn. See the Strategy Center for recommended retention actions.")
    elif risk == "Medium":
        st.info("This profile shows moderate churn risk. Proactive engagement is recommended.")
    else:
        st.success("✅ Lower relative risk: churn probability is below the 40% Medium-risk threshold.")

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Prediction Engine · Powered by RandomForestClassifier</div>',
    unsafe_allow_html=True,
)
