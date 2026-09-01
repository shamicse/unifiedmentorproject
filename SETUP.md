# Setup Guide — Workforce Attrition Project

Complete instructions to **clone from GitHub**, **set up your environment**, and **run every part of this project** from scratch.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Get the Project from GitHub](#get-the-project-from-github)
3. [Open the Project in Your Editor](#open-the-project-in-your-editor)
4. [Create a Virtual Environment](#create-a-virtual-environment)
5. [Install Dependencies](#install-dependencies)
6. [Verify the Dataset](#verify-the-dataset)
7. [Run the Full Workflow](#run-the-full-workflow)
8. [Use the Streamlit Dashboard](#use-the-streamlit-dashboard)
9. [Generate Word Reports](#generate-word-reports)
10. [Publish This Repo on GitHub (For Owners)](#publish-this-repo-on-github-for-owners)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Install these **before** you start:

| Tool | Minimum Version | Download |
|---|---|---|
| Python | 3.10+ (3.11 recommended) | [python.org/downloads](https://www.python.org/downloads/) |
| Git | Latest | [git-scm.com/downloads](https://git-scm.com/downloads) |
| Code editor | Any | [VS Code](https://code.visualstudio.com/) or [Cursor](https://cursor.com/) |

**Optional but recommended:**
- **Jupyter** (included in `requirements.txt`) — for running the notebook
- **Microsoft Word** or **LibreOffice** — to open `.docx` reports

### Check installations

**Windows (PowerShell):**
```powershell
python --version
git --version
```

**macOS / Linux (Terminal):**
```bash
python3 --version
git --version
```

---

## Get the Project from GitHub

### Option A — Clone with HTTPS (easiest)


```powershell
# Windows PowerShell
cd Desktop
git clone https://github.com/shamicse/unifiedmentorproject.git
cd unifiedmentorproject
```

```bash
# macOS / Linux
cd ~/Desktop
git clone https://github.com/shamicse/unifiedmentorproject.git
cd unifiedmentorproject
```

### Option B — Clone with SSH (if you use SSH keys)

```bash
git https://github.com/shamicse/unifiedmentorproject.git
cd unifiedmentorproject
```

### Option C — Download ZIP (no Git required)

1. Open your GitHub repo page in a browser
2. Click **Code** → **Download ZIP**
3. Extract the ZIP to a folder (e.g. `Desktop/unifiedmentorproject`)
4. Open a terminal in that folder

---

## Open the Project in Your Editor

### VS Code / Cursor

```powershell
# From inside the project folder
code .
```

Or in Cursor:

```powershell
cursor .
```

**Manual method:**
1. Open VS Code or Cursor
2. **File → Open Folder**
3. Select the `unifiedmentorproject` folder

### Jupyter Notebook

After setup (steps below), open the notebook:

```powershell
jupyter notebook notebooks/attrition_analysis.ipynb
```

Or open `notebooks/attrition_analysis.ipynb` directly in VS Code/Cursor with the Jupyter extension.

---

## Create a Virtual Environment

Using a virtual environment keeps project dependencies isolated.

### Windows (PowerShell)

```powershell
cd workforce_attrition_project
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
cd unifiedmentorproject
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

## Install Dependencies

With the virtual environment **activated**:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---|---|
| pandas, numpy | Data processing |
| matplotlib, seaborn | Notebook charts |
| plotly | Interactive dashboard charts |
| scikit-learn, joblib | Machine learning |
| streamlit | Web dashboard |
| jupyter, ipykernel | Notebook environment |
| python-docx | Word report generation |

**Verify installation:**

```powershell
python -c "import pandas, streamlit, sklearn; print('All packages OK')"
```

---

## Verify the Dataset

Confirm the raw data file exists:

```
data/employee_attrition.csv
```

Quick check:

```powershell
python -c "import pandas as pd; df=pd.read_csv('data/employee_attrition.csv'); print(df.shape)"
```

Expected output: `(1470, 31)` — 1,470 employees, 31 columns.

If the file is missing, ensure you cloned/downloaded the full repo including the `data/` folder.

---

## Run the Full Workflow

Follow these steps **in order** the first time you use the repo.

### Step 1 — Clean the data

```powershell
python -c "import sys; sys.path.insert(0,'dashboard'); from utils import load_cleaned_data; df=load_cleaned_data(force_refresh=True); print('Cleaned rows:', len(df))"
```

Output saved to: `outputs/cleaned_employee_attrition.csv`

### Step 2 — Run the analysis notebook

```powershell
jupyter notebook notebooks/attrition_analysis.ipynb
```

In the notebook:
1. Click **Kernel → Restart & Run All**
2. Wait for all 7 steps to finish
3. Charts are saved to `outputs/charts/`

**Notebook steps covered:**

| Step | What it does |
|---|---|
| 1 | Data validation & cleaning |
| 2 | Overall attrition assessment |
| 3 | Department & role analysis |
| 4 | Demographic analysis |
| 5 | Tenure & career stage analysis |
| 6 | Workload & mobility analysis |
| 7 | Predictive modeling |

### Step 3 — Train the predictive model

The notebook Step 7 trains the model automatically. You can also run:

```powershell
python -c "import sys; sys.path.insert(0,'dashboard'); from utils import load_cleaned_data; from modeling import train_attrition_model; r=train_attrition_model(load_cleaned_data()); print(r.metrics)"
```

Model saved to: `outputs/attrition_model.joblib`

### Step 4 — Generate Word reports (optional)

```powershell
python reports/generate_reports.py
```

Creates/updates:
- `reports/research_paper.docx`
- `reports/executive_summary.docx`

You can also open and edit these `.docx` files directly in Word without running the script.

---

## Use the Streamlit Dashboard

### Start the app

With virtual environment activated, from the project root:

```powershell
python -m streamlit run dashboard/app.py
```

Your terminal will show:

```
Local URL: http://localhost:8501
```

### Open in browser

1. Open **http://localhost:8501**
2. Use the **sidebar filters** (department, role, tenure, overtime, travel)
3. Explore the **6 tabs**:

| Tab | What you see |
|---|---|
| Overview | Total employees, attrition rate, retained vs exited charts |
| Department & Role | Bar charts + department × role heatmap |
| Demographics | Age, gender, marital status, education charts |
| Tenure & Workload | Tenure bands, promotion, distance, overtime/travel |
| KPI Summary | Key performance indicators table |
| Predictive Model | Model metrics, feature importance, risk estimator |

### Stop the dashboard

Press `Ctrl + C` in the terminal where Streamlit is running.

---

## Generate Word Reports

| File | Description |
|---|---|
| `reports/research_paper.docx` | Full research paper with methodology and results |
| `reports/executive_summary.docx` | Short summary for HR leadership |

**To regenerate after new analysis:**

```powershell
python reports/generate_reports.py
```

**To edit manually:** Open the `.docx` files in Microsoft Word or Google Docs. You do **not** need the Python script for editing.

---

## Publish This Repo on GitHub (For Owners)

If you are the project owner and want to publish this for the first time:

### 1. Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `unifiedmentorproject`
3. Choose **Public** or **Private**
4. Do **not** initialize with README (you already have one)
5. Click **Create repository**

### 2. Initialize Git and push (first time)

From your project folder:

```powershell
git init
git add .
git commit -m "Initial commit:unified mentor project"
git branch -M main
git remote add origin https://github.com/shamicse/unifiedmentorproject.git
git push -u origin main
```


### 3. What to include in the repo

| Include | Exclude |
|---|---|
| `data/employee_attrition.csv` | `venv/` folder |
| `dashboard/`, `notebooks/`, `reports/` | `__pycache__/` |
| `outputs/charts/` (PNG files) | `.ipynb_checkpoints/` |
| `requirements.txt`, `README.md`, `SETUP.md` | Large temp files |

### 4. Share with others

Send them your repo URL:

```
https://github.com/shamicse/unifiedmentorproject.git
```

They follow **this SETUP.md** from [Get the Project from GitHub](#get-the-project-from-github) onward.

### 5. Update README GitHub URL

---

## Troubleshooting

### `python` is not recognized

- Reinstall Python and check **"Add Python to PATH"**
- On macOS/Linux, use `python3` instead of `python`

### `streamlit` is not recognized

Use the module form:

```powershell
python -m streamlit run dashboard/app.py
```

### `ModuleNotFoundError: No module named 'sklearn'`

```powershell
pip install scikit-learn
```

Or reinstall all dependencies:

```powershell
pip install -r requirements.txt
```

### Jupyter notebook kernel errors

Register the virtual environment as a Jupyter kernel:

```powershell
pip install ipykernel
python -m ipykernel install --user --name=attrition-env --display-name="Attrition Project"
```

Then in the notebook: **Kernel → Change Kernel → Attrition Project**

### Port 8501 already in use

Streamlit will try the next port (8502, 8503…). Check the terminal for the actual URL, or stop the other Streamlit process.

### Empty dashboard / no data

Regenerate cleaned data:

```powershell
python -c "import sys; sys.path.insert(0,'dashboard'); from utils import load_cleaned_data; load_cleaned_data(force_refresh=True)"
```

### Virtual environment not activating (Windows)

Use Command Prompt instead:

```cmd
venv\Scripts\activate.bat
```

---

## Quick Reference — All Commands

Run these from the project root with `venv` activated:

```powershell
# Setup (first time only)
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt

# Clean data
python -c "import sys; sys.path.insert(0,'dashboard'); from utils import load_cleaned_data; load_cleaned_data(force_refresh=True)"

# Notebook
jupyter notebook notebooks/attrition_analysis.ipynb

# Dashboard
python -m streamlit run dashboard/app.py

# Reports
python reports/generate_reports.py
```

---

## Need Help?

1. Check [README.md](README.md) for features, functions, and project overview
2. Review the notebook outputs for analysis errors
3. Open an **Issue** on the GitHub repo page if something is broken

---

**Author:** Shami Akhtar  
**Project:** Unified Mentor — Palo Alto Networks Attrition Analysis
