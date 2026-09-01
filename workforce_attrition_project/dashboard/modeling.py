"""Predictive attrition modeling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "outputs" / "attrition_model.joblib"

UI_FEATURES = [
    "Age",
    "Department",
    "JobRole",
    "OverTime",
    "BusinessTravel",
    "MaritalStatus",
    "YearsAtCompany",
    "MonthlyIncome",
    "WorkLifeBalance",
    "JobSatisfaction",
    "DistanceFromHome",
    "YearsSinceLastPromotion",
]

FEATURE_COLUMNS = [
    "Age",
    "BusinessTravel",
    "Department",
    "DistanceFromHome",
    "Education",
    "EducationField",
    "EnvironmentSatisfaction",
    "Gender",
    "JobInvolvement",
    "JobLevel",
    "JobRole",
    "JobSatisfaction",
    "MaritalStatus",
    "MonthlyIncome",
    "NumCompaniesWorked",
    "OverTime",
    "PercentSalaryHike",
    "PerformanceRating",
    "RelationshipSatisfaction",
    "StockOptionLevel",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "WorkLifeBalance",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager",
]

CATEGORICAL_FEATURES = [
    "BusinessTravel",
    "Department",
    "EducationField",
    "Gender",
    "JobRole",
    "MaritalStatus",
    "OverTime",
]

NUMERIC_FEATURES = [col for col in FEATURE_COLUMNS if col not in CATEGORICAL_FEATURES]


@dataclass
class ModelResults:
    metrics: dict[str, float]
    classification_report: str
    confusion_matrix: np.ndarray
    feature_importance: pd.DataFrame
    predictions: pd.DataFrame
    model: Pipeline


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        max_depth=12,
        min_samples_leaf=4,
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def _feature_names(pipeline: Pipeline) -> list[str]:
    preprocessor: ColumnTransformer = pipeline.named_steps["preprocessor"]
    cat_encoder: OneHotEncoder = preprocessor.named_transformers_["cat"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    return NUMERIC_FEATURES + cat_names


def train_attrition_model(df: pd.DataFrame, test_size: float = 0.2) -> ModelResults:
    model_df = df[FEATURE_COLUMNS + ["Attrition"]].copy()
    x = model_df[FEATURE_COLUMNS]
    y = model_df["Attrition"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)
    y_prob = pipeline.predict_proba(x_test)[:, 1]

    importances = pipeline.named_steps["classifier"].feature_importances_
    importance_df = (
        pd.DataFrame({"Feature": _feature_names(pipeline), "Importance": importances})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )

    predictions = pd.DataFrame(
        {
            "Actual": y_test.values,
            "Predicted": y_pred,
            "Exit Probability": y_prob,
        }
    )

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1 Score": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_prob),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    return ModelResults(
        metrics=metrics,
        classification_report=classification_report(y_test, y_pred, zero_division=0),
        confusion_matrix=confusion_matrix(y_test, y_pred),
        feature_importance=importance_df,
        predictions=predictions,
        model=pipeline,
    )


def load_model() -> Pipeline | None:
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


def predict_employee_risk(model: Pipeline, employee: pd.DataFrame) -> float:
    return float(model.predict_proba(employee[FEATURE_COLUMNS])[:, 1][0])
