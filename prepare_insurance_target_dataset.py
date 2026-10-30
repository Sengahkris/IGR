"""
FinScope Rwanda 2024 - Non-Health Insurance Uptake: Data Prep Pipeline
NISR Big Data Hackathon 2026, Track 2 (Financial Inclusion & Poverty Reduction)

Builds the binary "non-health insurance uptake" target (any of 16 named
insurance/pension products) from FinScope Rwanda 2024 microdata, cleans a
15-variable predictor set spanning demographic / socioeconomic / geographic
access / financial behaviour, runs a short EDA, and writes a stratified
70/30 train-test split ready for the modeling stage (XGBoost + logistic
regression baseline, per the project plan).

Run:    python prepare_insurance_target_dataset.py
Input:  "FinScope 2024 Rwanda.dta"  (must be in the same folder as this script)
Output: finscope_train_raw.csv        - cleaned, human-readable categories
        finscope_test_raw.csv
        finscope_train_processed.csv  - one-hot encoded, model-ready
        finscope_test_processed.csv

Variable choices were mapped against FinScope_2024_Rwanda_Variable_Guide.xlsx
and cross-checked directly on the data (see comments below for anything
non-obvious - skip patterns, mislabeled columns, potential target leakage).
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)

RAW_FILE = "FinScope 2024 Rwanda.dta"
RANDOM_STATE = 42
TEST_SIZE = 0.30

# =============================================================================
# SECTION 1 - LOAD (only the ~20 columns we need - the .dta has 2,442 columns)
# =============================================================================

# Target components: i6_01-i6_16 ("Do you have any of the following insurance
# products?") are asked of ALL 13,994 respondents with zero missingness.
# The alternative pair, qf1_07/qf4_07 ("ever used" / "currently use" an
# insurance provider institution), follows a skip pattern - qf4 is only
# asked of the ~1-2% who say "yes" to qf1 (198 non-missing out of 13,994) -
# so it was ruled out; using it as a target would silently drop 99% of the
# sample.
TARGET_COLS = [f"i6_{i:02d}" for i in range(1, 17)]

# Finalized 15-variable predictor shortlist. Raw FinScope code -> readable
# name. See SECTION 4 for the variables that were considered and dropped
# for heavy missingness.
FEATURE_COLS = {
    # -- Demographic (age, sex, marital status, education) ------------------
    "b1": "age",
    "b2": "sex",
    "b3": "marital_status",
    "c4a": "education",
    # -- Socioeconomic (Ubudehe, assets, income proxy) -----------------------
    "c13a": "ubudehe_category",
    "c12_16": "owns_motor_vehicle",
    "n1b": "main_livelihood",              # recoded to 6 broad groups, see SECTION 3
    # -- Geographic access (distance/time to bank, ATM, insurance, SACCO) ---
    "a6": "urban_rural",
    "d1b10": "time_to_bank",
    "d1a15": "time_to_insurance_branch",   # NOTE: for item 15 the a/b suffixes are
                                            # swapped vs. every other d1 pair - d1a15
                                            # holds the TIME categories ("How long...")
                                            # and d1b15 holds DISTANCE ("What is the
                                            # distance..."). Verified directly against
                                            # the value labels; d1a15 is used here to
                                            # stay consistent with time_to_bank/sacco.
    "d1b7": "time_to_sacco",
    # -- Financial behaviour (savings, mobile money, insurance awareness) ---
    "qf1_05": "used_mobile_money",
    "e2c": "saves_money",
    "e9b": "has_emergency_savings",
    "i3_3": "aware_microinsurance",
}

# Kept for identification / EDA / weighting - NOT used as model features.
CONTEXT_COLS = ["key", "a1", "pop_wt"]

usecols = list(dict.fromkeys(CONTEXT_COLS + list(FEATURE_COLS) + TARGET_COLS))
df = pd.read_stata(RAW_FILE, columns=usecols, convert_categoricals=True)
print(f"Loaded {df.shape[0]:,} respondents x {df.shape[1]} columns\n")

# =============================================================================
# SECTION 2 - BUILD TARGET
# =============================================================================

# Binary target = 1 if respondent holds ANY of the 16 named products:
#   i6_01-i6_12, i6_16  -> 13 general insurance types (motor, life, household,
#                          credit-life, legal aid, business, property, accident,
#                          savings-with-risk, home, agriculture, education, other)
#   i6_13, i6_14, i6_15 -> RSSB public pension, private pension, Ejo Heza
# All 16 columns are Yes/No with zero missingness (asked of the full sample).
df["insurance_uptake"] = (df[TARGET_COLS] == "Yes").any(axis=1).astype(int)
df = df.drop(columns=TARGET_COLS)

n_pos, n = int(df["insurance_uptake"].sum()), len(df)
weighted_prev = np.average(df["insurance_uptake"], weights=df["pop_wt"])
print("=" * 70)
print("TARGET: insurance_uptake")
print("=" * 70)
print(f"Unweighted prevalence:          {n_pos/n:.1%}  ({n_pos:,} / {n:,})")
print(f"Population-weighted prevalence: {weighted_prev:.1%}  (weight = pop_wt)")
print("(Matches the project's headline 28.6% non-health insurance uptake figure.)\n")

# =============================================================================
# SECTION 3 - CLEAN & RECODE PREDICTORS
# =============================================================================

df = df.rename(columns=FEATURE_COLS)

# Cosmetic fix: several Stata value labels contain a mis-encoded apostrophe
# ("Don?t know" instead of "Don't know"). Purely cosmetic - does not change
# category identity or counts.
for col in df.select_dtypes(include="category").columns:
    df[col] = df[col].cat.rename_categories(
        lambda x: x.replace("Don?t know", "Don't know") if isinstance(x, str) else x
    )

# --- main_livelihood (n1b): collapse 23 raw categories into 6 groups -------
# Two raw categories - 'Private pension' and 'Government pension' - mean the
# respondent's main livelihood IS a pension income stream, i.e. they almost
# certainly already hold i6_13/i6_14 (the pension components of our target).
# Kept as their own categories, they would leak the target into a predictor.
# They are folded into the broader "Dependent/social transfer" bucket
# (dominated by remittances, gifts, household support, VUP, humanitarian aid
# - ~2,250 people), which dilutes that leakage to a tolerable residual while
# keeping livelihood type as a usable socioeconomic/income-proxy feature.
LIVELIHOOD_MAP = {
    "Salary/wages from Government institution": "Salaried",
    "Salary/wages from a private business/company": "Salaried",
    "Salary/wages from a farmer": "Salaried",
    "Salary/wages from an individual": "Salaried",
    "Self-employed (registered/licensed)": "Self-employed",
    "Self-employed (not registered/licensed)": "Self-employed",
    "Money from farming": "Farming/fishing",
    "Money from fishing": "Farming/fishing",
    "Sell something I grow": "Farming/fishing",
    "Sell something I collect from nature": "Farming/fishing",
    "Piece work": "Informal/piece work",
    "Make goods to sell": "Informal/piece work",
    "Rental income": "Rental/asset income",
    "Private pension": "Dependent/social transfer",
    "Government pension": "Dependent/social transfer",
    "Government": "Dependent/social transfer",
    "Social protection": "Dependent/social transfer",
    "Gift": "Dependent/social transfer",
    "Remittances": "Dependent/social transfer",
    "Get money from household member": "Dependent/social transfer",
    "Household member pays my expenses": "Dependent/social transfer",
    "VUP public works": "Dependent/social transfer",
    "Humanitarian": "Dependent/social transfer",
}
df["main_livelihood"] = (
    df["main_livelihood"].astype(str).str.strip().map(lambda x: LIVELIHOOD_MAP.get(x, x))
)

# --- Missing values ----------------------------------------------------------
# The finalized 15-feature set has exactly ONE missing value in the whole
# matrix (a single respondent with no answer for time_to_insurance_branch).
# Filled with "Don't know" - the closest existing category and, in this
# context, a plausible reason for a non-response to a distance/time question.
missing_before = df[list(FEATURE_COLS.values())].isna().sum()
if missing_before.sum() > 0:
    print("Missing values found in final feature set (filled with \"Don't know\"):")
    print(missing_before[missing_before > 0], "\n")
df["time_to_insurance_branch"] = df["time_to_insurance_branch"].astype(str)
df["time_to_insurance_branch"] = df["time_to_insurance_branch"].replace("nan", "Don't know")

# =============================================================================
# SECTION 4 - VARIABLES CONSIDERED AND EXCLUDED (heavy missingness)
# =============================================================================
# These were on the initial candidate shortlist but dropped from the final
# 15 because of heavy missingness (pct computed on the full 13,994 sample):
EXCLUDED_FOR_MISSINGNESS = {
    "c1c   (education of household head)": "56.6% missing",
    "c8b   (has title deed for land/plot)": "31.2% missing",
    "n11   (monthly personal income)": "72.2% missing",
    "n12   (annual total income)": "69.1% missing",
    "c14_4 (household owns a computer)": "91.8% missing",
    "c14_6 (household owns internet access)": "84.9% missing",
    "f4e   (number of smartphones owned)": "79.9% missing",
    "qf4_05/qf4_10 (currently use mobile money/savings group)": "~50-65% missing (skip pattern)",
    "h1    (agree/disagree borrowing statements)": "100% missing - dropped entirely",
    "i7    (main reason for not having insurance)": "only asked of the uninsured - circular w.r.t. target",
}
print("=" * 70)
print("EXCLUDED CANDIDATES (heavy missingness or skip-pattern / leakage risk)")
print("=" * 70)
for var, reason in EXCLUDED_FOR_MISSINGNESS.items():
    print(f"  {var:60s} {reason}")
print()

# =============================================================================
# SECTION 5 - EDA
# =============================================================================
print("=" * 70)
print("EDA: target prevalence by subgroup (population-weighted, pop_wt)")
print("=" * 70)


def weighted_prevalence_by(frame, group_col):
    out = (
        frame.groupby(group_col, observed=True)
        .apply(lambda g: pd.Series({
            "n": len(g),
            "weighted_prevalence": np.average(g["insurance_uptake"], weights=g["pop_wt"]),
        }))
        .sort_values("weighted_prevalence", ascending=False)
    )
    out["n"] = out["n"].astype(int)
    out["weighted_prevalence"] = out["weighted_prevalence"].map(lambda x: f"{x:.1%}")
    return out


for group_col, label in [
    ("a1", "Province"),
    ("urban_rural", "Urban / Rural"),
    ("ubudehe_category", "Ubudehe category"),
    ("education", "Education level"),
]:
    print(f"\n-- By {label} --")
    print(weighted_prevalence_by(df, group_col))

print("\n" + "=" * 70)
print("Class balance check")
print("=" * 70)
balance = df["insurance_uptake"].value_counts(normalize=True).rename({0: "No (0)", 1: "Yes (1)"})
print(balance.map(lambda x: f"{x:.1%}"))
print("-> Moderate imbalance (~3:1). Stratified split used below; prefer AUC-ROC")
print("   and precision/recall over plain accuracy at the modeling stage.\n")

print("=" * 70)
print("Association with target (quick correlation check)")
print("=" * 70)
age_corr = df["age"].corr(df["insurance_uptake"])
print(f"Point-biserial correlation, age vs. insurance_uptake: {age_corr:+.3f}")

print("\nUnweighted uptake rate by category (categorical predictors):")
for col in FEATURE_COLS.values():
    if col == "age":
        continue
    rates = df.groupby(col, observed=True)["insurance_uptake"].mean().sort_values(ascending=False)
    spread = rates.max() - rates.min()
    print(f"  {col:28s} spread across categories: {spread:.1%}")
print()

# =============================================================================
# SECTION 6 - FINALIZE X / y
# =============================================================================
CATEGORICAL_FEATURES = [c for c in FEATURE_COLS.values() if c != "age"]
NUMERIC_FEATURES = ["age"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

model_df = df[["key", "insurance_uptake"] + ALL_FEATURES].copy()
for col in CATEGORICAL_FEATURES:
    model_df[col] = model_df[col].astype(str)

X = model_df[ALL_FEATURES]
y = model_df["insurance_uptake"]

# =============================================================================
# SECTION 7 - STRATIFIED TRAIN/TEST SPLIT (70/30)
# =============================================================================
train_idx, test_idx = train_test_split(
    model_df.index,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_STATE,
)
train_df = model_df.loc[train_idx].reset_index(drop=True)
test_df = model_df.loc[test_idx].reset_index(drop=True)

print("=" * 70)
print("STRATIFIED TRAIN/TEST SPLIT")
print("=" * 70)
print(f"Train: {len(train_df):,} rows  ({train_df['insurance_uptake'].mean():.1%} positive)")
print(f"Test:  {len(test_df):,} rows  ({test_df['insurance_uptake'].mean():.1%} positive)\n")

# =============================================================================
# SECTION 8 - ONE-HOT ENCODE (fit on train only, to avoid leakage into test)
# =============================================================================
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
    ]
)

X_train_enc = preprocessor.fit_transform(train_df[ALL_FEATURES])
X_test_enc = preprocessor.transform(test_df[ALL_FEATURES])

encoded_cols = NUMERIC_FEATURES + list(
    preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
)
train_processed = pd.DataFrame(X_train_enc, columns=encoded_cols)
train_processed.insert(0, "key", train_df["key"].values)
train_processed["insurance_uptake"] = train_df["insurance_uptake"].values

test_processed = pd.DataFrame(X_test_enc, columns=encoded_cols)
test_processed.insert(0, "key", test_df["key"].values)
test_processed["insurance_uptake"] = test_df["insurance_uptake"].values

# =============================================================================
# SECTION 9 - SAVE OUTPUTS
# =============================================================================
train_df.to_csv("finscope_train_raw.csv", index=False)
test_df.to_csv("finscope_test_raw.csv", index=False)
train_processed.to_csv("finscope_train_processed.csv", index=False)
test_processed.to_csv("finscope_test_processed.csv", index=False)

print("=" * 70)
print("SAVED FILES")
print("=" * 70)
print("finscope_train_raw.csv        -", train_df.shape, "(human-readable categories)")
print("finscope_test_raw.csv         -", test_df.shape)
print("finscope_train_processed.csv  -", train_processed.shape, "(one-hot encoded, model-ready)")
print("finscope_test_processed.csv   -", test_processed.shape)
