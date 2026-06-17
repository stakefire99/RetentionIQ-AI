"""
RetentionIQ AI - Churn Drivers
Shows the model's feature importance ranking and translates the top
drivers into plain-language business insights.
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from data_processing import get_processed_data
from model_training import load_model
from analytics import contract_churn_multiplier
from theme import inject_global_css, render_brand, render_hero, render_section_header, COLORS, PLOTLY_TEMPLATE

st.set_page_config(page_title="RetentionIQ AI | Churn Drivers", page_icon="📉", layout="wide")
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
model, encoders, metrics = load_model()
contract_stats = contract_churn_multiplier(df)

render_hero(
    eyebrow="CHURN DRIVERS",
    title="What's Actually Driving Churn?",
    subtitle="RandomForest feature importance ranks every signal in the model by how much it "
              "contributes to churn predictions across the full customer base.",
)

# ---- Feature Importance Chart ----
render_section_header("Feature Importance", "RandomForest Gini importance, full feature set")

fi = metrics["feature_importance"]
sorted_fi = dict(sorted(fi.items(), key=lambda x: x[1], reverse=True)[:10])

# friendlier labels
label_map = {
    "Contract": "Contract Type",
    "tenure": "Tenure",
    "TotalCharges": "Total Charges",
    "MonthlyCharges": "Monthly Charges",
    "OnlineSecurity": "Online Security",
    "TechSupport": "Tech Support",
    "InternetService": "Internet Service",
    "PaymentMethod": "Payment Method",
    "OnlineBackup": "Online Backup",
    "DeviceProtection": "Device Protection",
    "gender": "Gender",
    "SeniorCitizen": "Senior Citizen",
    "Partner": "Partner Status",
    "Dependents": "Dependents",
    "PhoneService": "Phone Service",
    "MultipleLines": "Multiple Lines",
    "StreamingTV": "Streaming TV",
    "StreamingMovies": "Streaming Movies",
    "PaperlessBilling": "Paperless Billing",
}

labels = [label_map.get(k, k) for k in sorted_fi.keys()]
values = [v * 100 for v in sorted_fi.values()]

fig = go.Figure(data=[go.Bar(
    y=labels[::-1],
    x=values[::-1],
    orientation="h",
    marker=dict(
        color=values[::-1],
        colorscale=[[0, COLORS["emerald"]], [0.5, COLORS["cyan"]], [1, COLORS["red"]]],
    ),
    text=[f"{v:.1f}%" for v in values[::-1]],
    textposition="outside",
    textfont=dict(family="JetBrains Mono", color=COLORS["text"]),
)])
fig.update_layout(
    **PLOTLY_TEMPLATE["layout"],
    height=440,
    margin=dict(l=10, r=40, t=10, b=10),
    xaxis_title="Relative Importance (%)",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="riq-divider">', unsafe_allow_html=True)

# ---- Business Insights ----
render_section_header("Business Insights", "Plain-language takeaways from the top drivers")

mtm_mult = contract_stats["mtm_vs_one_year"]
two_yr_mult = contract_stats["mtm_vs_two_year"]

insights = [
    ("Contract Type — #1 driver", f"Customers with month-to-month contracts are <b>{mtm_mult:.1f}x</b> more likely to churn than annual subscribers, and <b>{two_yr_mult:.1f}x</b> more likely than two-year subscribers. This is the single strongest lever for reducing churn."),
    ("Tenure — #2 driver", "Newer customers churn at significantly higher rates. The first 12 months are the highest-risk window — early engagement and onboarding quality matter most here."),
    ("Total & Monthly Charges — #3 & #4 drivers", "Spend levels correlate strongly with churn risk, particularly when high charges aren't matched by perceived value (e.g. missing support add-ons)."),
    ("Online Security & Tech Support", "Customers without these add-ons churn measurably more than those with full support coverage — bundling support can directly offset risk."),
]

for title, body in insights:
    st.markdown(
        f"""
        <div class="riq-card" style="margin-bottom:14px;">
            <div style="font-family:'Sora'; font-weight:700; font-size:15px; color:{COLORS['cyan']}; margin-bottom:6px;">{title}</div>
            <div style="font-family:'Inter'; font-size:13.5px; color:{COLORS['text_muted']}; line-height:1.6;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="riq-footer">RetentionIQ AI · Churn Drivers · RandomForest Feature Importance</div>',
    unsafe_allow_html=True,
)
