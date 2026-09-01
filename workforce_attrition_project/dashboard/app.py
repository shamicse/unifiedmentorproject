"""Palo Alto Networks — Workforce Attrition Patterns & Risk Hotspot Analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (
    apply_filters,
    attrition_rate,
    department_role_heatmap_data,
    early_tenure_attrition,
    grouped_attrition_rate,
    load_cleaned_data,
    workload_attrition_index,
)
from modeling import FEATURE_COLUMNS, CATEGORICAL_FEATURES, UI_FEATURES, train_attrition_model

st.set_page_config(
    page_title="Palo Alto Networks | Attrition Analysis",
    page_icon="📊",
    layout="wide",
)

PALO_ALTO_COLORS = {
    "primary": "#FA582D",
    "secondary": "#0078D4",
    "retained": "#2ECC71",
    "exited": "#E74C3C",
}


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_cleaned_data()


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    st.sidebar.caption("Refine analysis across all dashboard modules.")

    departments = st.sidebar.multiselect(
        "Department",
        options=sorted(df["Department"].unique()),
        default=sorted(df["Department"].unique()),
    )
    job_roles = st.sidebar.multiselect(
        "Job Role",
        options=sorted(df["JobRole"].unique()),
        default=sorted(df["JobRole"].unique()),
    )

    min_tenure = int(df["YearsAtCompany"].min())
    max_tenure = int(df["YearsAtCompany"].max())
    tenure_range = st.sidebar.slider(
        "Tenure Range (Years at Company)",
        min_value=min_tenure,
        max_value=max_tenure,
        value=(min_tenure, max_tenure),
    )

    st.sidebar.subheader("Workload Toggles")
    overtime_only = st.sidebar.toggle("Overtime employees only", value=False)
    no_overtime_only = st.sidebar.toggle("Non-overtime employees only", value=False)
    if overtime_only and no_overtime_only:
        st.sidebar.warning("Both overtime toggles are on; results may be empty.")

    travel_modes = st.sidebar.multiselect(
        "Business Travel",
        options=sorted(df["BusinessTravel"].unique()),
        default=sorted(df["BusinessTravel"].unique()),
    )

    return apply_filters(
        df,
        departments=departments,
        job_roles=job_roles,
        tenure_range=tenure_range,
        overtime_only=overtime_only,
        no_overtime_only=no_overtime_only,
        travel_modes=travel_modes,
    )


def overview_tab(df: pd.DataFrame) -> None:
    st.subheader("Attrition Overview Dashboard")

    rate = attrition_rate(df)
    retained = int((df["Attrition"] == 0).sum())
    exited = int((df["Attrition"] == 1).sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Employees", f"{len(df):,}")
    c2.metric("Attrition Rate", f"{rate:.2f}%")
    c3.metric("Retained", f"{retained:,}")
    c4.metric("Exited", f"{exited:,}")

    distribution = pd.DataFrame(
        {
            "Status": ["Retained", "Exited"],
            "Count": [retained, exited],
        }
    )
    fig = px.pie(
        distribution,
        names="Status",
        values="Count",
        color="Status",
        color_discrete_map={
            "Retained": PALO_ALTO_COLORS["retained"],
            "Exited": PALO_ALTO_COLORS["exited"],
        },
        title="Retained vs Exited Employee Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

    baseline = pd.DataFrame(
        {
            "Metric": ["Organization Attrition Rate", "Retention Rate"],
            "Percentage": [rate, 100 - rate],
        }
    )
    fig_bar = px.bar(
        baseline,
        x="Metric",
        y="Percentage",
        text="Percentage",
        color="Metric",
        color_discrete_sequence=[PALO_ALTO_COLORS["exited"], PALO_ALTO_COLORS["retained"]],
        title="Baseline Organizational Turnover",
    )
    fig_bar.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)


def department_role_tab(df: pd.DataFrame) -> None:
    st.subheader("Department & Role Heatmaps")

    dept = grouped_attrition_rate(df, "Department")
    role = grouped_attrition_rate(df, "JobRole")

    c1, c2 = st.columns(2)
    with c1:
        fig_dept = px.bar(
            dept,
            x="Department",
            y="Attrition Rate (%)",
            color="Attrition Rate (%)",
            color_continuous_scale="Reds",
            title="Attrition Rate by Department",
            text="Attrition Rate (%)",
        )
        fig_dept.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_dept, use_container_width=True)

    with c2:
        fig_role = px.bar(
            role.head(10),
            x="JobRole",
            y="Attrition Rate (%)",
            color="Attrition Rate (%)",
            color_continuous_scale="OrRd",
            title="Top 10 Roles by Attrition Rate",
            text="Attrition Rate (%)",
        )
        fig_role.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_role.update_xaxes(tickangle=45)
        st.plotly_chart(fig_role, use_container_width=True)

    heatmap_data = department_role_heatmap_data(df)
    if not heatmap_data.empty:
        st.markdown("#### Attrition Intensity Heatmap (Department × Job Role)")
        fig_heat = px.imshow(
            heatmap_data,
            text_auto=".1f",
            color_continuous_scale="Reds",
            aspect="auto",
            labels=dict(color="Attrition Rate (%)"),
        )
        fig_heat.update_layout(xaxis_title="Job Role", yaxis_title="Department")
        st.plotly_chart(fig_heat, use_container_width=True)

        high_risk_dept = dept.iloc[0]["Department"] if not dept.empty else "N/A"
        high_risk_role = role.iloc[0]["JobRole"] if not role.empty else "N/A"
        st.info(
            f"**High-risk hotspots:** {high_risk_dept} department and "
            f"{high_risk_role} role show the highest attrition in the current filter."
        )


def demographic_tab(df: pd.DataFrame) -> None:
    st.subheader("Demographic Attrition Explorer")

    age = grouped_attrition_rate(df, "AgeGroup")
    gender = grouped_attrition_rate(df, "Gender")
    marital = grouped_attrition_rate(df, "MaritalStatus")
    education = grouped_attrition_rate(df, "Education")
    edu_field = grouped_attrition_rate(df, "EducationField")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(age, x="AgeGroup", y="Attrition Rate (%)", title="Attrition by Age Group"),
            use_container_width=True,
        )
        st.plotly_chart(
            px.bar(gender, x="Gender", y="Attrition Rate (%)", title="Attrition by Gender"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            px.bar(marital, x="MaritalStatus", y="Attrition Rate (%)", title="Attrition by Marital Status"),
            use_container_width=True,
        )
        st.plotly_chart(
            px.bar(education, x="Education", y="Attrition Rate (%)", title="Attrition by Education Level"),
            use_container_width=True,
        )

    fig_field = px.bar(
        edu_field.sort_values("Attrition Rate (%)", ascending=False),
        x="EducationField",
        y="Attrition Rate (%)",
        title="Attrition by Education Field",
    )
    fig_field.update_xaxes(tickangle=45)
    st.plotly_chart(fig_field, use_container_width=True)


def tenure_workload_tab(df: pd.DataFrame) -> None:
    st.subheader("Tenure & Workload Analysis")

    tenure = grouped_attrition_rate(df, "TenureBand")
    promotion = grouped_attrition_rate(df, "PromotionStagnation")
    distance = grouped_attrition_rate(df, "DistanceBand")
    workload = workload_attrition_index(df)
    early_rate = early_tenure_attrition(df, years=2)

    def band_rate(band_name: str) -> str:
        match = tenure.loc[tenure["TenureBand"] == band_name, "Attrition Rate (%)"]
        return f"{match.iloc[0]:.2f}%" if not match.empty else "N/A"

    c1, c2, c3 = st.columns(3)
    c1.metric("Early-Tenure Attrition (≤2 yrs)", f"{early_rate:.2f}%")
    c2.metric("Mid-Career Band", band_rate("Mid (3-6 yrs)"))
    c3.metric("Senior Band", band_rate("Senior (7+ yrs)"))

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(tenure, x="TenureBand", y="Attrition Rate (%)", title="Attrition by Tenure Band"),
            use_container_width=True,
        )
        st.plotly_chart(
            px.bar(promotion, x="PromotionStagnation", y="Attrition Rate (%)", title="Promotion Stagnation Impact"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            px.bar(distance, x="DistanceBand", y="Attrition Rate (%)", title="Distance from Home vs Attrition"),
            use_container_width=True,
        )

        fig_workload = go.Figure()
        for category in workload["Category"].unique():
            subset = workload[workload["Category"] == category]
            fig_workload.add_trace(
                go.Bar(
                    name=category,
                    x=subset["Factor"],
                    y=subset["Attrition Rate (%)"],
                    text=subset["Attrition Rate (%)"],
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                )
            )
        fig_workload.update_layout(
            barmode="group",
            title="Workload Attrition Index (Overtime & Travel)",
            xaxis_title="Factor",
            yaxis_title="Attrition Rate (%)",
        )
        st.plotly_chart(fig_workload, use_container_width=True)


def kpi_summary(df: pd.DataFrame) -> None:
    st.subheader("Key Performance Indicators")
    kpi_df = pd.DataFrame(
        {
            "Metric": [
                "Attrition Rate (%)",
                "Department Attrition Rate (Highest)",
                "Role Attrition Rate (Highest)",
                "Early-Tenure Attrition (≤2 yrs)",
                "Overtime Attrition Rate",
            ],
            "Value": [
                f"{attrition_rate(df):.2f}%",
                f"{grouped_attrition_rate(df, 'Department').iloc[0]['Attrition Rate (%)']:.2f}%" if not df.empty else "N/A",
                f"{grouped_attrition_rate(df, 'JobRole').iloc[0]['Attrition Rate (%)']:.2f}%" if not df.empty else "N/A",
                f"{early_tenure_attrition(df):.2f}%",
                f"{grouped_attrition_rate(df, 'OverTime').query('OverTime == \"Yes\"')['Attrition Rate (%)'].iloc[0]:.2f}%"
                if not df[df["OverTime"] == "Yes"].empty
                else "N/A",
            ],
            "Description": [
                "Employees who left ÷ total employees",
                "Highest attrition among departments",
                "Highest attrition among job roles",
                "Attrition within first 2 years",
                "Attrition linked to overtime workload",
            ],
        }
    )
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)


@st.cache_resource
def get_model_results():
    df = load_cleaned_data()
    return train_attrition_model(df)


def prediction_tab(df: pd.DataFrame) -> None:
    st.subheader("Predictive Attrition Modeling")
    st.caption(
        "Random Forest classifier trained on workforce features to estimate individual exit risk."
    )

    with st.spinner("Training model..."):
        results = get_model_results()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Accuracy", f"{results.metrics['Accuracy']:.2%}")
    c2.metric("Precision", f"{results.metrics['Precision']:.2%}")
    c3.metric("Recall", f"{results.metrics['Recall']:.2%}")
    c4.metric("F1 Score", f"{results.metrics['F1 Score']:.2%}")
    c5.metric("ROC-AUC", f"{results.metrics['ROC-AUC']:.3f}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Confusion Matrix")
        cm = results.confusion_matrix
        cm_df = pd.DataFrame(
            cm,
            index=["Actual Retained", "Actual Exited"],
            columns=["Predicted Retained", "Predicted Exited"],
        )
        st.dataframe(cm_df, use_container_width=True)

        top_features = results.feature_importance.head(15)
        fig = px.bar(
            top_features,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Top 15 Attrition Drivers (Feature Importance)",
            color="Importance",
            color_continuous_scale="Reds",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Classification Report")
        st.code(results.classification_report)

        st.markdown("#### Sample Predictions (Test Set)")
        st.dataframe(
            results.predictions.sort_values("Exit Probability", ascending=False).head(20),
            use_container_width=True,
        )

    st.divider()
    st.markdown("#### Individual Risk Estimator")
    st.caption("Adjust employee attributes to estimate attrition probability.")

    sample = df.iloc[0]
    input_cols = st.columns(3)
    values = sample[FEATURE_COLUMNS].to_dict()

    for idx, feature in enumerate(UI_FEATURES):
        col = input_cols[idx % 3]
        with col:
            if feature in CATEGORICAL_FEATURES:
                options = sorted(df[feature].dropna().unique().tolist())
                values[feature] = st.selectbox(
                    feature,
                    options=options,
                    index=options.index(sample[feature]) if sample[feature] in options else 0,
                    key=f"pred_{feature}",
                )
            else:
                values[feature] = st.number_input(
                    feature,
                    value=float(sample[feature]),
                    key=f"pred_{feature}",
                )

    if st.button("Estimate Exit Risk", type="primary"):
        employee_df = pd.DataFrame([values])
        probability = results.model.predict_proba(employee_df[FEATURE_COLUMNS])[:, 1][0]
        risk_label = "High" if probability >= 0.5 else "Moderate" if probability >= 0.25 else "Low"
        st.metric("Predicted Exit Probability", f"{probability:.1%}", delta=risk_label)


def main() -> None:
    st.title("Workforce Attrition Patterns & Risk Hotspot Analysis")
    st.caption("Palo Alto Networks — Foundational HR Intelligence Dashboard")

    df = get_data()
    filtered = render_sidebar(df)

    if filtered.empty:
        st.error("No employees match the selected filters. Adjust sidebar filters to continue.")
        return

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Overview",
            "Department & Role",
            "Demographics",
            "Tenure & Workload",
            "KPI Summary",
            "Predictive Model",
        ]
    )

    with tab1:
        overview_tab(filtered)
    with tab2:
        department_role_tab(filtered)
    with tab3:
        demographic_tab(filtered)
    with tab4:
        tenure_workload_tab(filtered)
    with tab5:
        kpi_summary(filtered)
    with tab6:
        prediction_tab(filtered)


if __name__ == "__main__":
    main()
