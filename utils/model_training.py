"""
RetentionIQ AI - Model Training Module
Trains a RandomForestClassifier on the Telco churn dataset and persists
the model, encoders, and metrics for use across the Streamlit app.
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve, confusion_matrix
)

import sys
sys.path.append(os.path.dirname(__file__))
from data_processing import get_processed_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.joblib")

# Features used for prediction (raw, pre-encoding column names)
CATEGORICAL_FEATURES = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService",
    "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
    "Contract", "PaperlessBilling", "PaymentMethod",
]
NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges"]
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET = "Churn"


def build_training_frame(df: pd.DataFrame):
    X = df[ALL_FEATURES].copy()
    y = (df[TARGET] == "Yes").astype(int)

    encoders = {}
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    return X, y, encoders


def train_model():
    df = get_processed_data()
    X, y, encoders = build_training_frame(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_importance": dict(zip(ALL_FEATURES, model.feature_importances_.tolist())),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    metrics["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    joblib.dump(metrics, METRICS_PATH)

    return model, encoders, metrics


def load_model():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH)):
        return train_model()
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    metrics = joblib.load(METRICS_PATH)
    return model, encoders, metrics


def predict_churn(model, encoders, input_dict: dict):
    """
    input_dict should contain raw values for ALL_FEATURES.
    Returns (churn_probability, risk_level)
    """
    row = {}
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        val = str(input_dict.get(col, le.classes_[0]))
        if val not in le.classes_:
            val = le.classes_[0]
        row[col] = le.transform([val])[0]
    for col in NUMERIC_FEATURES:
        row[col] = input_dict.get(col, 0)

    X_row = pd.DataFrame([row])[ALL_FEATURES]
    proba = model.predict_proba(X_row)[0, 1]

    if proba >= 0.7:
        risk = "High"
    elif proba >= 0.4:
        risk = "Medium"
    else:
        risk = "Low"

    return proba, risk


if __name__ == "__main__":
    model, encoders, metrics = train_model()
    print("Accuracy: ", round(metrics["accuracy"], 4))
    print("Precision:", round(metrics["precision"], 4))
    print("Recall:   ", round(metrics["recall"], 4))
    print("F1:       ", round(metrics["f1"], 4))
    print("ROC-AUC:  ", round(metrics["roc_auc"], 4))
    print("\nFeature Importance (top 10):")
    sorted_fi = sorted(metrics["feature_importance"].items(), key=lambda x: -x[1])
    for feat, imp in sorted_fi[:10]:
        print(f"  {feat:20s} {imp:.4f}")
