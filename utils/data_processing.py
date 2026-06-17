"""
RetentionIQ AI - Data Processing Module
Handles loading, cleaning, and feature engineering for the Telco Customer Churn dataset.
"""

import pandas as pd
import numpy as np
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "telco_churn.csv")
PROCESSED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed_churn.csv")


def load_raw_data(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # TotalCharges has blank strings for customers with 0 tenure (brand new sign-ups)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"])

    # Standardize binary-like text fields
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

    # Drop exact duplicates if any
    df = df.drop_duplicates(subset="customerID")

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Tenure buckets for cohort-style storytelling
    def tenure_bucket(t):
        if t <= 6:
            return "0-6 Months"
        elif t <= 12:
            return "6-12 Months"
        elif t <= 24:
            return "1-2 Years"
        elif t <= 48:
            return "2-4 Years"
        else:
            return "4+ Years"

    df["TenureBucket"] = df["tenure"].apply(tenure_bucket)

    # Count of subscribed add-on services (proxy for engagement depth)
    service_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    df["ServiceCount"] = df[service_cols].apply(
        lambda row: sum(1 for v in row if v == "Yes"), axis=1
    )

    # Average revenue per month of tenure (helps spot high-value-but-new accounts)
    df["AvgMonthlySpend"] = df["TotalCharges"] / df["tenure"].replace(0, 1)

    # CLV proxy: monthly charges * tenure (already TotalCharges, but a forward-looking proxy)
    df["EstimatedAnnualValue"] = df["MonthlyCharges"] * 12

    # Risk-relevant flag: no tech support AND no online security (common churn cluster)
    df["LowSupportFlag"] = (
        (df["TechSupport"] == "No") & (df["OnlineSecurity"] == "No")
    ).map({True: "Yes", False: "No"})

    return df


def get_processed_data(force_reprocess: bool = False) -> pd.DataFrame:
    if os.path.exists(PROCESSED_PATH) and not force_reprocess:
        return pd.read_csv(PROCESSED_PATH)

    df = load_raw_data()
    df = clean_data(df)
    df = engineer_features(df)
    df.to_csv(PROCESSED_PATH, index=False)
    return df


if __name__ == "__main__":
    df = get_processed_data(force_reprocess=True)
    print(f"Processed {len(df)} rows, {len(df.columns)} columns")
    print(df.head())
    print("\nChurn rate:", (df["Churn"] == "Yes").mean())
