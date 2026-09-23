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

# Excel file stored in the same GitHub repository
DATA_FILE = "loan_free.xlsx"

# Loan period = 12 months
LOAN_TERM_MONTHS = 12


# ============================================================
# REQUIRED COLUMNS
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

    if not os.path.exists(DATA_FILE):

        st.error(
            f"❌ {DATA_FILE} was not found."
        )

        st.info(
            "Make sure loan_free.xlsx is uploaded to the "
            "same GitHub repository/folder as this application."
        )

        st.stop()

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

    return df


# ============================================================
# LOAD DATA
# ============================================================

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

df = df[COLUMNS].copy()


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
# DATE FORMAT
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
    # Validate Amount
    # --------------------------------------------------------

    elif loan_amount <= 0:

        st.sidebar.error(
            "Loan amount must be greater than zero."
        )

    else:

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


            # ------------------------------------------------
            # New Loan
            # ------------------------------------------------

            new_row = {

                "Name":
                    clean_name,

                "Disbursed_date":
                    pd.Timestamp(
                        disbursed_date
                    ),

                "loan_amount":
                    float(
                        loan_amount
                    ),

                "Due_date":
                    pd.Timestamp(
                        due_date
                    ),

                "Status":
                    "In Progress"
            }


            # ------------------------------------------------
            # Add to DataFrame
            # ------------------------------------------------

            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [new_row]
                    )
                ],
                ignore_index=True
            )


            # ------------------------------------------------
            # Save
            # ------------------------------------------------

            if save_data(df):

                st.sidebar.success(
                    f"Loan for {clean_name} saved successfully!"
                )

                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

st.subheader(
    "📊 Loan Summary"
)


# ============================================================
# STATUS DATA
# ============================================================

in_progress = df[
    df["Status"]
    .str.lower()
    .eq("in progress")
]


returned = df[
    df["Status"]
    .str.lower()
    .eq("returned")
]


# ============================================================
# CURRENT DATE
# ============================================================

today = pd.Timestamp(
    date.today()
)


# ============================================================
# OVERDUE
# ============================================================

overdue = df[
    (
        df["Status"]
        .str.lower()
        .eq("in progress")
    )
    &
    (
        df["Due_date"]
        < today
    )
]


# ============================================================
# METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Loans",
    f"{len(df):,}"
)


col2.metric(
    "In Progress",
    f"{len(in_progress):,}"
)


col3.metric(
    "Returned",
    f"{len(returned):,}"
)


col4.metric(
    "Overdue",
    f"{len(overdue):,}"
)


# ============================================================
# ALL LOANS
# ============================================================

st.subheader(
    "📋 All Loans"
)


display_df = df.copy()


# ============================================================
# FORMAT DATES
# ============================================================

display_df[
    "Disbursed_date"
] = display_df[
    "Disbursed_date"
].apply(
    format_date
)


display_df[
    "Due_date"
] = display_df[
    "Due_date"
].apply(
    format_date
)


# ============================================================
# FORMAT AMOUNT
# ============================================================

display_df[
    "loan_amount"
] = display_df[
    "loan_amount"
].apply(
    lambda x:
        f"{float(x):,.0f}"
)


# ============================================================
# RENAME COLUMNS FOR DISPLAY
# ============================================================

display_df = display_df.rename(
    columns={

        "Disbursed_date":
            "Disbursed Date",

        "loan_amount":
            "Loan Amount",

        "Due_date":
            "Due Date"
    }
)


# ============================================================
# DISPLAY ALL LOANS
# ============================================================

st.dataframe(
    display_df[
        [
            "Name",
            "Disbursed Date",
            "Loan Amount",
            "Due Date",
            "Status"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MARK LOAN AS RETURNED
# ============================================================

st.subheader(
    "✅ Mark Loan as Returned"
)


if in_progress.empty:

    st.info(
        "There are no loans in progress."
    )

else:

    # --------------------------------------------------------
    # Select Name
    # --------------------------------------------------------

    selected_name = st.selectbox(
        "Select Borrower",
        in_progress["Name"].tolist()
    )


    # --------------------------------------------------------
    # Mark Returned
    # --------------------------------------------------------

    if st.button(
        "Mark as Returned",
        type="primary"
    ):

        df.loc[
            df["Name"] == selected_name,
            "Status"
        ] = "Returned"


        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        if save_data(df):

            st.success(
                f"Loan for {selected_name} marked as Returned."
            )

            st.rerun()


# ============================================================
# OVERDUE LOANS
# ============================================================

st.subheader(
    "⚠️ Overdue Loans"
)


overdue_display = df[
    (
        df["Status"]
        .str.lower()
        .eq("in progress")
    )
    &
    (
        df["Due_date"]
        < today
    )
].copy()


# ============================================================
# NO OVERDUE LOANS
# ============================================================

if overdue_display.empty:

    st.success(
        "No overdue loans."
    )


```python
# ============================================================
# DISPLAY OVERDUE LOANS
# ============================================================

else:

    # --------------------------------------------------------
    # Format Disbursed Date
    # --------------------------------------------------------

    overdue_display[
        "Disbursed_date"
    ] = overdue_display[
        "Disbursed_date"
    ].apply(
        format_date
    )


    # --------------------------------------------------------
    # Format Due Date
    # --------------------------------------------------------

    overdue_display[
        "Due_date"
    ] = overdue_display[
        "Due_date"
    ].apply(
        format_date
    )


    # --------------------------------------------------------
    # Format Loan Amount
    # --------------------------------------------------------

    overdue_display[
        "loan_amount"
    ] = overdue_display[
        "loan_amount"
    ].apply(
        lambda x:
            f"{float(x):,.0f}"
    )


    # --------------------------------------------------------
    # Rename Columns
    # --------------------------------------------------------

    overdue_display = overdue_display.rename(
        columns={

            "Disbursed_date":
                "Disbursed Date",

            "loan_amount":
                "Loan Amount",

            "Due_date":
                "Due Date"
        }
    )


    # --------------------------------------------------------
    # Display Overdue Loans
    # --------------------------------------------------------

    st.dataframe(
        overdue_display[
            [
                "Name",
                "Disbursed Date",
                "Loan Amount",
                "Due Date",
                "Status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )



