import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import os


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AO Loan Management App",
    page_icon="💰",
    layout="wide"
)

st.title("AO Interest-Free Loan Management App")

DATA_FILE = "loan_free.xlsx"

# Loan term = 12 months
LOAN_TERM_MONTHS = 12


# ============================================================
# COLUMNS
# ============================================================

COLUMNS = [
    "Name",
    "Disbursed_date",
    "loan_amount",
    "Due_date",
    "Status"
]


# ============================================================
# LOAD EXCEL FILE
# ============================================================

def load_data():

    if os.path.exists(DATA_FILE):

        try:

            df = pd.read_excel(
                DATA_FILE,
                engine="openpyxl"
            )

        except Exception as e:

            st.error(
                f"Could not read {DATA_FILE}: {e}"
            )

            st.stop()

    else:

        df = pd.DataFrame(
            columns=COLUMNS
        )

    return df


df = load_data()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

missing_columns = [
    col
    for col in COLUMNS
    if col not in df.columns
]

if missing_columns:

    st.error(
        "The Excel file is missing these columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# KEEP ONLY REQUIRED COLUMNS
# ============================================================

df = df[
    COLUMNS
].copy()


# ============================================================
# CLEAN DATA
# ============================================================

# ------------------------------------------------------------
# Name
# ------------------------------------------------------------

df["Name"] = (
    df["Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------
# Disbursed Date
# ------------------------------------------------------------

df["Disbursed_date"] = pd.to_datetime(
    df["Disbursed_date"],
    errors="coerce"
)


# ------------------------------------------------------------
# Due Date
# ------------------------------------------------------------

df["Due_date"] = pd.to_datetime(
    df["Due_date"],
    errors="coerce"
)


# ------------------------------------------------------------
# Loan Amount
# ------------------------------------------------------------

df["loan_amount"] = pd.to_numeric(
    df["loan_amount"],
    errors="coerce"
).fillna(0)


# ------------------------------------------------------------
# Status
# ------------------------------------------------------------

df["Status"] = (
    df["Status"]
    .fillna("In Progress")
    .astype(str)
    .str.strip()
)


# ============================================================
# DATE FORMAT FUNCTION
# ============================================================

def format_date(value):

    if pd.isna(value):
        return ""

    value = pd.to_datetime(
        value,
        errors="coerce"
    )

    if pd.isna(value):
        return ""

    return (
        f"{value.month}/"
        f"{value.day}/"
        f"{value.year}"
    )


# ============================================================
# SAVE DATA
# ============================================================

def save_data(data):

    try:

        data.to_excel(
            DATA_FILE,
            index=False,
            engine="openpyxl"
        )

        return True

    except Exception as e:

        st.error(
            f"Could not save Excel file: {e}"
        )

        return False


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "➕ Add New Loan"
)


# ============================================================
# ADD NEW LOAN
# ============================================================

loan_name = st.sidebar.text_input(
    "Name",
    placeholder="Enter borrower name"
)


loan_amount = st.sidebar.number_input(
    "Loan Amount",
    min_value=0.0,
    step=100.0,
    format="%.0f"
)


disbursed_date = st.sidebar.date_input(
    "Disbursed Date",
    value=date.today()
)


# ============================================================
# SAVE NEW LOAN
# ============================================================

if st.sidebar.button(
    "Save Loan",
    type="primary"
):

    # --------------------------------------------------------
    # Validate Name
    # --------------------------------------------------------

    if not loan_name.strip():

        st.sidebar.error(
            "Name is required."
        )

    # --------------------------------------------------------
    # Validate Loan Amount
    # --------------------------------------------------------

    elif loan_amount <= 0:

        st.sidebar.error(
            "Loan amount must be greater than zero."
        )

    else:

        # ----------------------------------------------------
        # Clean Name
        # ----------------------------------------------------

        clean_name = loan_name.strip()


        # ----------------------------------------------------
        # Check duplicate name
        # ----------------------------------------------------

        duplicate_name = df[
            df["Name"]
            .str.lower()
            .eq(clean_name.lower())
        ]


        if not duplicate_name.empty:

            st.sidebar.error(
                f"A loan already exists for {clean_name}."
            )

        else:

            # ------------------------------------------------
            # Calculate Due Date
            # ------------------------------------------------

            due_date = (
                disbursed_date
                +
                relativedelta(
                    months=LOAN_TERM_MONTHS
                )
            )


        
