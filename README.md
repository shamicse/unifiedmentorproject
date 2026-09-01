# Workforce Attrition Patterns & Risk Hotspot Analysis

**Organization:** Palo Alto Networks  
**Program:** Unified Mentor Capstone Project  
**Focus:** Foundational HR intelligence — where attrition happens, which groups are most affected, and which employees are at highest risk.

---

## Overview

This project analyzes **1,470 employee records** to answer critical workforce questions for HR leadership:

- Which departments and job roles experience the highest attrition?
- Is attrition concentrated among specific age groups or tenure bands?
- Do overtime and business travel contribute to exits?
- Are early-career employees leaving more frequently than experienced staff?

The solution includes **EDA notebooks**, a **Streamlit dashboard**, **predictive modeling**, and **Word report deliverables**.

---

## Quick Start (GitHub)

> **Full step-by-step guide:** see **[SETUP.md](SETUP.md)** for clone, install, run notebook, dashboard, and publish instructions.

### Clone this repo

Replace `YOUR_USERNAME` with the GitHub account that published the repo:

```powershell
git clone https://github.com/YOUR_USERNAME/workforce_attrition_project.git
cd workforce_attrition_project
```

### Setup & run (5 commands)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1                 # Windows — see SETUP.md for macOS/Linux
pip install -r requirements.txt
python -m streamlit run dashboard/app.py    # Open http://localhost:8501
```

For the full workflow (notebook, model training, reports), follow **[SETUP.md](SETUP.md)**.

---

## Project Structure

```
workforce_attrition_project/
│
├── data/
│   └── employee_attrition.csv          # Raw dataset (1,470 rows, 31 columns)
│
├── notebooks/
│   └── attrition_analysis.ipynb        # Full 7-step analytical workflow
│
├── dashboard/
│   ├── app.py                          # Streamlit web application
│   ├── utils.py                        # Data cleaning & KPI functions
│   └── modeling.py                     # Predictive modeling pipeline
│
├── outputs/
│   ├── charts/                         # Exported visualization PNGs
│   ├── cleaned_employee_attrition.csv  # Processed dataset
│   └── attrition_model.joblib          # Trained Random Forest model
│
├── reports/
│   ├── research_paper.docx             # Full research paper (submission)
│   ├── executive_summary.docx          # Executive summary (submission)
│   └── generate_reports.py             # Optional script to regenerate .docx files
│
├── requirements.txt                    # Python dependencies
├── README.md                           # Project documentation
├── SETUP.md                            # Full GitHub clone & setup guide
└── .gitignore                          # Git ignore rules for publishing
```

---

## Features

### Data & Analysis
- Automated data validation and cleaning
- Attrition label normalization (`Yes/No` and `0/1` supported)
- Derived analytics fields: age groups, tenure bands, promotion stagnation, distance bands
- Department × role heatmap for risk hotspot identification
- Workload attrition index (overtime + business travel)

### Streamlit Dashboard
- **Overview** — overall attrition rate, retained vs exited distribution
- **Department & Role** — bar charts + attrition intensity heatmap
- **Demographics** — age, gender, marital status, education analysis
- **Tenure & Workload** — tenure bands, promotion stagnation, distance, overtime/travel
- **KPI Summary** — key performance indicators table
- **Predictive Model** — model metrics, feature importance, individual risk estimator

### Interactive Filters (Sidebar)
- Department multiselect
- Job role multiselect
- Tenure range slider (Years at Company)
- Overtime toggle (overtime only / non-overtime only)
- Business travel multiselect

### Predictive Modeling
- Random Forest classifier with balanced class weights
- 80/20 stratified train-test split
- Saved model artifact for reuse
- Individual employee exit probability estimation

### Reports
- Research paper with methodology, results, and recommendations
- Executive summary for HR leadership and stakeholders
- Optional Python script to regenerate Word documents from latest findings

---

## Key Findings

| Metric | Value |
|---|---|
| Total Employees | 1,470 |
| Overall Attrition Rate | 16.12% |
| Highest-Risk Department | Sales (20.63%) |
| Highest-Risk Role | Sales Representative (39.76%) |
| Early-Tenure Attrition (≤2 yrs) | 29.82% |
| Overtime Attrition Rate | 30.53% |
| Model ROC-AUC | 0.802 |

---

## Installation & Usage

| Step | Action | Command / File |
|---|---|---|
| 1 | Clone from GitHub | `git clone https://github.com/YOUR_USERNAME/workforce_attrition_project.git` |
| 2 | Create virtual environment | `python -m venv venv` then activate (see SETUP.md) |
| 3 | Install dependencies | `pip install -r requirements.txt` |
| 4 | Run analysis notebook | `jupyter notebook notebooks/attrition_analysis.ipynb` |
| 5 | Launch dashboard | `python -m streamlit run dashboard/app.py` |
| 6 | Generate reports (optional) | `python reports/generate_reports.py` |

**Detailed instructions** (Windows, macOS, Linux, troubleshooting, publishing to GitHub): **[SETUP.md](SETUP.md)**

> **Note:** Submission deliverables are the `.docx` files in `reports/`. The `generate_reports.py` script only regenerates them; you can also edit the Word files directly.

### Using this repo after publishing on GitHub

Anyone with your repo link can:

1. **Clone** the repository (HTTPS, SSH, or Download ZIP)
2. **Open** the folder in VS Code, Cursor, or Jupyter
3. **Create a virtual environment** and install `requirements.txt`
4. **Run the notebook** for full EDA (Steps 1–7)
5. **Start Streamlit** at `http://localhost:8501` for the live dashboard
6. **Open** `reports/research_paper.docx` and `reports/executive_summary.docx` for submission documents

See **[SETUP.md](SETUP.md)** for copy-paste commands for each step.

---

## Functions Reference

### `dashboard/utils.py` — Data & KPI Layer

| Function | Description |
|---|---|
| `normalize_attrition(series)` | Converts attrition labels (`Yes/No`, `0/1`, boolean) into numeric `0` or `1`. |
| `clean_dataframe(df)` | Full cleaning pipeline: deduplication, missing-value removal, field standardization, and derived band columns (`AgeGroup`, `TenureBand`, `PromotionStagnation`, `DistanceBand`). |
| `load_raw_data()` | Loads the raw CSV from `data/employee_attrition.csv`. |
| `load_cleaned_data(force_refresh=False)` | Loads cleaned data from cache or regenerates and saves to `outputs/cleaned_employee_attrition.csv`. |
| `attrition_rate(df)` | Returns overall attrition percentage for a DataFrame. |
| `grouped_attrition_rate(df, group_col)` | Computes total employees, exits, and attrition rate (%) grouped by any column. |
| `early_tenure_attrition(df, years=2)` | Attrition rate for employees within the first N years at company. |
| `workload_attrition_index(df)` | Combines overtime and business travel attrition rates into a single workload index DataFrame. |
| `apply_filters(df, ...)` | Filters data by department, job role, tenure range, overtime flags, and travel modes. |
| `department_role_heatmap_data(df)` | Builds a department × job role pivot table of attrition rates for heatmap visualization. |

### `dashboard/modeling.py` — Predictive Layer

| Function / Class | Description |
|---|---|
| `ModelResults` | Dataclass holding metrics, classification report, confusion matrix, feature importance, predictions, and the trained pipeline. |
| `build_pipeline()` | Creates a scikit-learn pipeline with StandardScaler, OneHotEncoder, and RandomForestClassifier. |
| `_feature_names(pipeline)` | Extracts human-readable feature names after preprocessing (internal helper). |
| `train_attrition_model(df, test_size=0.2)` | Trains the model, evaluates performance, saves to `outputs/attrition_model.joblib`, and returns `ModelResults`. |
| `load_model()` | Loads a previously saved model from disk, or returns `None` if not found. |
| `predict_employee_risk(model, employee)` | Returns exit probability (0–1) for a single employee record. |

### `dashboard/app.py` — Streamlit UI Layer

| Function | Description |
|---|---|
| `get_data()` | Cached loader for cleaned employee dataset. |
| `render_sidebar(df)` | Renders all sidebar filters and returns the filtered DataFrame. |
| `overview_tab(df)` | Overview dashboard: metrics, pie chart, baseline turnover bar chart. |
| `department_role_tab(df)` | Department/role bar charts, heatmap, and high-risk hotspot alert. |
| `demographic_tab(df)` | Age, gender, marital status, education, and education field charts. |
| `tenure_workload_tab(df)` | Tenure bands, promotion stagnation, distance, and workload index charts. |
| `kpi_summary(df)` | Displays the KPI summary table. |
| `get_model_results()` | Cached model training and evaluation results. |
| `prediction_tab(df)` | Predictive modeling tab with metrics, confusion matrix, feature importance, and risk estimator form. |
| `main()` | Application entry point — loads data, applies filters, and renders all tabs. |

### `reports/generate_reports.py` — Report Generator (Optional)

| Function | Description |
|---|---|
| `add_bullet_list(doc, items)` | Adds a bulleted list to a Word document. |
| `build_research_paper()` | Generates `reports/research_paper.docx` with full analysis sections. |
| `build_executive_summary()` | Generates `reports/executive_summary.docx` with headline metrics and recommendations. |

---

## Analytical Methodology (Notebook Steps)

| Step | Name | Status |
|---|---|---|
| 1 | Data Validation & Cleaning | ✅ Completed |
| 2 | Overall Attrition Assessment | ✅ Completed |
| 3 | Department & Role-Wise Analysis | ✅ Completed |
| 4 | Demographic Attrition Analysis | ✅ Completed |
| 5 | Tenure & Career Stage Analysis | ✅ Completed |
| 6 | Workload & Mobility Impact Analysis | ✅ Completed |
| 7 | Predictive Attrition Modeling | ✅ Completed |

---

## Tasks Completed

- [x] Project folder structure created
- [x] Raw dataset integrated (`employee_attrition.csv`, 1,470 records)
- [x] Data cleaning pipeline implemented (`utils.py`)
- [x] Cleaned dataset exported to `outputs/cleaned_employee_attrition.csv`
- [x] Full EDA notebook with all 6 diagnostic steps + Step 7 modeling
- [x] Chart exports to `outputs/charts/`
- [x] Streamlit dashboard with 6 interactive tabs
- [x] Sidebar filters: department, role, tenure, overtime, travel
- [x] Department × role attrition heatmap
- [x] KPI summary module
- [x] Random Forest predictive model trained and saved
- [x] Individual employee risk estimator in dashboard
- [x] Research paper drafted (`reports/research_paper.docx`)
- [x] Executive summary drafted (`reports/executive_summary.docx`)
- [x] `requirements.txt` with all dependencies
- [x] README documentation
- [x] SETUP.md — GitHub clone, environment setup, and full run guide
- [x] `.gitignore` for GitHub publishing

---

## Roadmap

### Phase 1 — Foundation (Completed ✅)
- Project setup and data ingestion
- EDA across departments, demographics, tenure, and workload
- Streamlit diagnostic dashboard
- Research paper and executive summary drafts

### Phase 2 — Enhancement (Planned)
- [ ] Add SHAP values for model explainability
- [ ] Compare multiple models (Logistic Regression, XGBoost, LightGBM)
- [ ] Hyperparameter tuning with cross-validation
- [ ] Export dashboard charts as PDF report pack
- [ ] Add unit tests for `utils.py` and `modeling.py`

### Phase 3 — Deployment (Planned)
- [ ] Deploy Streamlit app to Streamlit Community Cloud or Cloudflare
- [ ] Schedule automated data refresh pipeline
- [ ] Email alerts for departments exceeding attrition thresholds
- [ ] Role-based dashboard access for HR vs leadership views

### Phase 4 — Business Integration (Planned)
- [ ] Connect to live HRIS / SAP / Workday data source
- [ ] Retention recommendation engine (action cards per risk segment)
- [ ] A/B tracking of retention program effectiveness
- [ ] Quarterly automated executive briefing generation

---

## Deliverables (Submission)

| Deliverable | File |
|---|---|
| Research paper | `reports/research_paper.docx` |
| Executive summary | `reports/executive_summary.docx` |
| Streamlit dashboard | `dashboard/app.py` |
| Analysis notebook | `notebooks/attrition_analysis.ipynb` |
| Cleaned dataset | `outputs/cleaned_employee_attrition.csv` |
| Visualizations | `outputs/charts/` |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11+ | Core language |
| Pandas / NumPy | Data manipulation |
| Matplotlib / Seaborn | Notebook visualizations |
| Plotly | Interactive dashboard charts |
| Scikit-learn | Predictive modeling |
| Streamlit | Web dashboard |
| Jupyter | Exploratory analysis |
| python-docx | Report generation |

---

## Author

**[Your Name]** — Unified Mentor Capstone Project  
**Organization context:** Palo Alto Networks  
**Date:** September 2026

---

## License

Academic / capstone project — Unified Mentor program.
