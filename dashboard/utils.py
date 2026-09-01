"""Data loading, cleaning, and KPI helpers for attrition analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "employee_attrition.csv"
CLEANED_DATA_PATH = PROJECT_ROOT / "outputs" / "cleaned_employee_attrition.csv"

KEY_COLUMNS = [
    "Age",
    "Attrition",
    "Department",
    "JobRole",
    "YearsAtCompany",
    "OverTime",
    "BusinessTravel",
    "DistanceFromHome",
    "Gender",
    "MaritalStatus",
    "Education",
    "EducationField",
    "YearsSinceLastPromotion",
    "TotalWorkingYears",
]

TRAVEL_MAP = {
    "Non-Travel": "Non-Travel",
    "Non_Travel": "Non-Travel",
    "Travel Rarely": "Travel Rarely",
    "Travel_Rarely": "Travel Rarely",
    "Travel Frequently": "Travel Frequently",
    "Travel_Frequently": "Travel Frequently",
}


def normalize_attrition(series: pd.Series) -> pd.Series:
    mapping = {
        "yes": 1,
        "no": 0,
        "1": 1,
        "0": 0,
        1: 1,
        0: 0,
        True: 1,
        False: 0,
    }
    return series.map(lambda value: mapping.get(str(value).strip().lower(), value)).astype(int)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = cleaned.columns.str.strip()

    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.dropna(subset=KEY_COLUMNS)

    cleaned["Attrition"] = normalize_attrition(cleaned["Attrition"])
    cleaned["Department"] = cleaned["Department"].astype(str).str.strip()
    cleaned["JobRole"] = cleaned["JobRole"].astype(str).str.strip()
    cleaned["BusinessTravel"] = (
        cleaned["BusinessTravel"].astype(str).str.strip().replace(TRAVEL_MAP)
    )
    cleaned["OverTime"] = cleaned["OverTime"].astype(str).str.strip().str.title()
    cleaned["Gender"] = cleaned["Gender"].astype(str).str.strip()
    cleaned["MaritalStatus"] = cleaned["MaritalStatus"].astype(str).str.strip()
    cleaned["EducationField"] = cleaned["EducationField"].astype(str).str.strip()

    cleaned["AgeGroup"] = pd.cut(
        cleaned["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "55+"],
        right=True,
    )
    cleaned["TenureBand"] = pd.cut(
        cleaned["YearsAtCompany"],
        bins=[-1, 2, 6, 100],
        labels=["Early (0-2 yrs)", "Mid (3-6 yrs)", "Senior (7+ yrs)"],
        right=True,
    )
    cleaned["PromotionStagnation"] = pd.cut(
        cleaned["YearsSinceLastPromotion"],
        bins=[-1, 2, 5, 100],
        labels=["Recent (0-2 yrs)", "Moderate (3-5 yrs)", "Stagnant (6+ yrs)"],
        right=True,
    )
    cleaned["DistanceBand"] = pd.cut(
        cleaned["DistanceFromHome"],
        bins=[-1, 5, 15, 100],
        labels=["Near (0-5 mi)", "Moderate (6-15 mi)", "Far (16+ mi)"],
        right=True,
    )

    return cleaned


def load_raw_data() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_PATH)


def load_cleaned_data(force_refresh: bool = False) -> pd.DataFrame:
    if force_refresh or not CLEANED_DATA_PATH.exists():
        cleaned = clean_dataframe(load_raw_data())
        CLEANED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(CLEANED_DATA_PATH, index=False)
        return cleaned
    return pd.read_csv(CLEANED_DATA_PATH)


def attrition_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df["Attrition"].mean() * 100)


def grouped_attrition_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, observed=False)
        .agg(
            Total=("Attrition", "count"),
            Exited=("Attrition", "sum"),
        )
        .reset_index()
    )
    summary["Attrition Rate (%)"] = (summary["Exited"] / summary["Total"] * 100).round(2)
    return summary.sort_values("Attrition Rate (%)", ascending=False)


def early_tenure_attrition(df: pd.DataFrame, years: int = 2) -> float:
    early = df[df["YearsAtCompany"] <= years]
    return attrition_rate(early)


def workload_attrition_index(df: pd.DataFrame) -> pd.DataFrame:
    overtime = grouped_attrition_rate(df, "OverTime").rename(columns={"OverTime": "Factor"})
    travel = grouped_attrition_rate(df, "BusinessTravel").rename(columns={"BusinessTravel": "Factor"})
    overtime["Category"] = "Overtime"
    travel["Category"] = "Business Travel"
    return pd.concat([overtime, travel], ignore_index=True)


def apply_filters(
    df: pd.DataFrame,
    departments: list[str] | None = None,
    job_roles: list[str] | None = None,
    tenure_range: tuple[int, int] | None = None,
    overtime_only: bool = False,
    no_overtime_only: bool = False,
    travel_modes: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()

    if departments:
        filtered = filtered[filtered["Department"].isin(departments)]
    if job_roles:
        filtered = filtered[filtered["JobRole"].isin(job_roles)]
    if tenure_range:
        filtered = filtered[
            (filtered["YearsAtCompany"] >= tenure_range[0])
            & (filtered["YearsAtCompany"] <= tenure_range[1])
        ]
    if overtime_only:
        filtered = filtered[filtered["OverTime"] == "Yes"]
    if no_overtime_only:
        filtered = filtered[filtered["OverTime"] == "No"]
    if travel_modes:
        filtered = filtered[filtered["BusinessTravel"].isin(travel_modes)]

    return filtered


def department_role_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(
        index="Department",
        columns="JobRole",
        values="Attrition",
        aggfunc="mean",
        fill_value=np.nan,
    )
    return (pivot * 100).round(2)
