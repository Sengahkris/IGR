# Rwanda Insurance Gap Radar 🇷🇼

> **NISR Big Data Hackathon 2026 · Track 2: Financial Inclusion & Poverty Reduction**  
> *Targeting the protection gap: finding the Rwandans who look like insured adults but hold no cover yet.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Executive Summary

While Rwanda has achieved an impressive **96% headline financial inclusion** and **88.5% health insurance coverage** (primarily via Mutuelle de Santé), only **28.6% of adults** hold any non-health insurance or pension product (FinScope 2024, survey-weighted).

Closing this protection gap is a direct pillar of the National Bank of Rwanda (NBR) ten-year insurance development strategy, the Second National Strategy for Transformation (NST2), and Vision 2050.

The **Rwanda Insurance Gap Radar** reframes the problem: instead of treating all uninsured citizens as a homogenous group, it uses machine learning to identify **Lookalike Non-Adopters**—Rwandans who statistically mirror existing policyholders in demographic, socioeconomic, and behavioural features, yet remain uncovered. 

Because their primary friction is **awareness, distribution access, or product design** (rather than fundamental unaffordability), lookalikes represent the quickest and most cost-effective path to closing Rwanda's insurance and pension gaps.

---

## The Two Gaps

National uptake figures mask two fundamentally different dynamics:

| Protection Gap | Scope & Products | National Uptake (Weighted) | Key Opportunity Identified |
|---|---|:---:|---|
| **Insurance Gap** | 13 commercial products (Life, Motor, Agriculture/Crop, Property, Accident, etc.) | **12.6%** | High awareness (>90%) but physical branch friction; microinsurance bundling. |
| **Pension Gap** | Public and private long-term savings (RSSB, Ejo Heza, Private schemes) | **21.5%** | Driven largely by Ejo Heza (18.9%); huge lookalike pool among mobile-money rural farmers. |

---

## 📊 Data Sources

1. **FinScope Rwanda 2024 Survey Microdata (NISR)**:
   - **Sample size:** 13,994 respondents across all 30 districts of Rwanda.
   - **Weights:** National adult weighting (`pop_wt`) applied to scale all predictions to Rwanda's adult population (~8.16 million adults).
   - **Features:** 30 predictor variables spanning demographics, socioeconomics (Ubudehe categories, housing, livelihood), financial behaviour (mobile money, formal banking, SACCOs, savings, emergency resilience), insurance awareness, and physical distance to financial infrastructure.
   - **Data Access & Link:** Raw survey data is cataloged at [NISR Microdata Catalog #120](https://microdata.statistics.gov.rw/index.php/catalog/120) (also referenced in [`data/link_to_data.txt`](data/link_to_data.txt)).
   - *Note on Data Privacy & File Size:* Raw survey microdata and full respondent-level score files are kept local/proprietary under survey data compliance. The Streamlit dashboard runs on privacy-preserving pre-aggregated demographic segments and model artifacts (`artifacts/`).
2. **geoBoundaries Rwanda ADM1**:
   - Official provincial administrative boundaries (Kigali City, Northern, Southern, Eastern, Western Provinces) used for spatial mapping.

---

## Methodology & Machine Learning Architecture

```
Raw FinScope Microdata (13,994 rows × 30 features)
                 │
                 ▼
Stratified Train/Test Split (70/30 on joint insurance × pension uptake)
                 │
                 ├───────────────────────────────┐
                 ▼                               ▼
       Random Forest Classifier          XGBoost Classifier
     (Entropy, Depth-Capped at 15)      (Optuna Hyperparameter Tuning)
                 │
                 ▼
       Model Evaluation (PR-AUC & ROC-AUC on Held-Out Test Set)
                 │
                 ▼
       Probability Calibration (Isotonic Regression)
                 │
                 ▼
       Explainability Layer (TreeSHAP grouped by FinScope questions)
                 │
                 ▼
       Lookalike & Dissimilar Segmentation (5-Fold Out-of-Fold Scoring)
                 │
                 ▼
       Interactive Streamlit Dashboard + Grounded Gemini AI Assistant
```

### Held-Out Test Performance

| Target | Model | PR-AUC | ROC-AUC | Production Role |
|---|---|:---:|:---:|---|
| **Insurance Uptake** | Logistic Regression (Benchmark) | 0.459 | 0.780 | Baseline |
| **Insurance Uptake** | **Random Forest** | **0.604** | **0.835** | **Production Model** |
| **Insurance Uptake** | XGBoost | 0.606 | 0.838 | Evaluated |
| **Pension Uptake** | Logistic Regression (Benchmark) | 0.486 | 0.733 | Baseline |
| **Pension Uptake** | **Random Forest** | **0.602** | **0.789** | **Production Model** |
| **Pension Uptake** | XGBoost | 0.583 | 0.778 | Evaluated |

**Top Predictive Drivers:**
- **Insurance:** Motor vehicle ownership, understanding of insurance concepts, awareness of life and microinsurance, proximity to insurance branches.
- **Pension:** Understanding of insurance, microinsurance awareness, main livelihood, education level, and presence of emergency savings.

---

## Application Features & User Interaction

The Streamlit dashboard (`streamlit_app/app.py`) provides five interactive analytical modules:

### 1. National Picture (`Tab 1`)
- **Headline Metrics:** Financial inclusion (96%), health insurance (88.5%), non-health uptake (28.6%).
- **Provincial Comparison:** Interactive comparison of insurance vs. pension uptake rates by province.
- **Choropleth Map:** Visualizes lookalike density across Rwanda's 5 provinces.
- **Product Breakdown:** Clean bar charts separating commercial insurance types from pension/Ejo Heza products.

### 2. Insured Profile (`Tab 2`)
- **Holder Archetypes:** Explore unsupervised K-Means archetypes characterizing current policyholders (e.g., Kigali urban salaried professionals, commercial agribusiness operators, rural Ejo Heza contributors).
- **SHAP Feature Importance:** Discover the top drivers that tilt an adult towards insurance or pension uptake.

### 3. Lookalike Finder (`Tab 3`)
- **Targeting Filters:** Filter by province, urban/rural settlement, Ubudehe social category, education, and livelihood.
- **Segment Sizing:** Shows the estimated lookalike population (`adults_k`), holder rate, and lookalike rate with custom opportunity badges (e.g. *Highest lookalike density*).

### 4. Score a Profile (`Tab 4`)
- **Scenario Simulator:** Input individual demographic and financial parameters (~10 intuitive questions).
- **Calibrated Propensity:** Calculates real-world calibrated probabilities for both insurance and pension adoption.
- **Real-Time SHAP Waterfall:** Interactive waterfall visual showing exactly which answers pushed the probability higher or lower.
- **Nearest Archetype:** Matches the profile to the closest national adopter persona.

### 5. Targeting Briefs (`Tab 5`)
- **Actionable Strategic Briefs:** Pre-computed intelligence briefs for the largest lookalike clusters.
- **Clear Action Points:** Detailed analysis covering population scale, key behavioural barriers, distribution channel recommendations, and tailored product angles (e.g., bundling agricultural micro-insurance with cooperatives).

### Grounded AI Chatbot
- An interactive assistant powered by Google Gemini (`gemini-flash-3.8`).
- Strictly grounded in FinScope 2024 national figures, archetype metrics, and segment calculations to eliminate hallucinations.

---

## Repository Structure

Adhering to the **NISR Big Data Hackathon Repository Guidelines**:

```
insurance_gap_radar/
├── README.md                      # Complete documentation & project guide
├── requirements.txt               # Python package dependencies
├── data/                          # FinScope datasets & variable codebooks
│   ├── FinScope 2024 Rwanda.dta
│   ├── FinScope_2024_Rwanda_Variable_Guide.xlsx
│   ├── Insurance_Data.csv
│   ├── finscope_train_processed.csv
│   └── finscope_test_processed.csv
├── notebooks/                     # Machine learning & exploratory pipelines
│   └── insurance_gap_radar_simplified_v2.ipynb
├── streamlit_app/                 # Streamlit Web Application
│   ├── app.py                     # Main application entry point
│   ├── charts.py                  # Plotly visualizations & spatial plots
│   ├── theme.py                   # UI styling & design tokens
│   ├── ai_chat.py                 # Grounded Gemini chatbot integration
│   ├── artifacts/                 # Pre-aggregated data tables & serialized RF model
│   └── assets/                    # Static assets (banner, geojson)
├── demo/                          # Solution video demonstration
│   └── demo.webm                  # (Or link in README)
├── student_cards/                 # Academic eligibility documents (both team members)
│   └── Christian&Vanessa_Recommendation_Letters.pdf
└── Reports/                       # Official FinScope reports & NISR presentations
```

---

## Setup & Local Execution

### 1. Clone the Repository
```bash
git clone https://github.com/Sengahkris/IGR.git
cd IGR
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run streamlit_app/app.py
```
The application will launch in your browser at `http://localhost:8501`.

*(Optional)* To enable the Gemini AI Chatbot, configure your Gemini API key in `streamlit_app/.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-google-gemini-api-key"
```

---

## Team Information & Eligibility

- **Track:** Track 2 — Financial Inclusion & Poverty Reduction
- **Team Members:** Christian & Vanessa
- **Eligibility Documentation:** Official university recommendation/student letters are provided in [`student_cards/Christian&Vanessa_Recommendation_Letters.pdf`](student_cards/Christian&Vanessa_Recommendation_Letters.pdf).
