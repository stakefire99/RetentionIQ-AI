"""
RetentionIQ AI - Batch Scoring
Pre-computes churn probability and risk level for every customer in the
dataset so pages don't need to re-run inference on every interaction.
"""

import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(__file__))
from data_processing import get_processed_data
from model_training import load_model, ALL_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES

SCORED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scored_customers.csv")


def score_all_customers(force: bool = False) -> pd.DataFrame:
    if os.path.exists(SCORED_PATH) and not force:
        return pd.read_csv(SCORED_PATH)

    df = get_processed_data()
    model, encoders, metrics = load_model()

    X = df[ALL_FEATURES].copy()
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        X[col] = X[col].astype(str).apply(
            lambda v: v if v in le.classes_ else le.classes_[0]
        )
        X[col] = le.transform(X[col])

    proba = model.predict_proba(X)[:, 1]

    def risk_level(p):
        if p >= 0.7:
            return "High"
        elif p >= 0.4:
            return "Medium"
        return "Low"

    result = df[["customerID"]].copy()
    result["ChurnProbability"] = proba
    result["RiskLevel"] = result["ChurnProbability"].apply(risk_level)

    result.to_csv(SCORED_PATH, index=False)
    return result


if __name__ == "__main__":
    scored = score_all_customers(force=True)
    print(scored["RiskLevel"].value_counts())
    print(scored.head())
