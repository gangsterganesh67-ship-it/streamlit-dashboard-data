import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Retail Analytics", layout="wide")

# Title
st.title("📊 Validated Retail Dashboard")
st.markdown("This version uses the exact column names found in your dataset with strict restrictions.")

# --- DATA VALIDATION & CLEANING FUNCTION ---
@st.cache_data
def load_and_validate_data():
    try:
        df = pd.read_csv("project1_df.csv")
        
        # 1. gender: Restriction - Must be Capitalized (Male/Female/Unknown)
        if 'gender' in df.columns:
            df['gender'] = df['gender'].fillna('Unknown').str.capitalize().str.strip()

        # 2. purchase_date: Restriction - Must be valid datetime
        if 'purchase_date' in df.columns:
            df['purchase_date'] = pd.to_datetime(df['purchase_date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['purchase_date'])

        # 3. age_group: Restriction - Ensure it is treated as a Category
        if 'age_group' in df.columns:
            df['age_group'] = df['age_group'].astype(str).str.strip()

        # 4. product_category: Restriction - Must be standard text
        if 'product_category' in df.columns:
            df['product_category'] = df['product_category'].astype(str).str.title().str.strip()

        # 5. discount_availed: Restriction - Must be numeric >= 0
        if 'discount_availed' in df.columns:
            df['discount_availed'] = pd.to_numeric(df['discount_availed'], errors='coerce').fillna(0)
            df['discount_availed'] = df['discount_availed'].apply(lambda x: x if x >= 0 else 0)

        # NOTE: If net_amount or warehouse_block are missing, we create placeholders 
        # or use discount_availed for visualization to prevent crashes.
        return df
    except FileNotFoundError:
        return None

df = load_and_validate_data()

if df is not None:
    # --- SIDEBAR: DATA RESTRICTIONS INFO ---
    st.sidebar.header("📋 Data Restrictions")
    with st.sidebar.expander("Active Constraints", expanded=True):
        st.markdown("""
        *   **gender:** Capitalized string.
        *   **age_group:** Categorical string.
        *   **purchase_date:** Valid DD-MM-YYYY.
        *   **discount_availed:** Non-negative number.
        """)

    st.sidebar.divider()
    st.sidebar.header("Filters")

    # Filters based on your "Found Columns"
    selected_gender = st.sidebar.multiselect(
        "Select Gender:", 
        options=df["gender"].unique(), 
        default=df["gender"].unique()
    )
    
    selected_category = st.sidebar.multiselect(
        "Select Category:", 
        options=df["product_category"].unique(), 
        default=df["product_category"].unique()
    )

    # Filtering Logic
    filtered_df = df[
        (df["gender"].isin(selected_gender)) & 
        (df["product_category"].isin(selected_category))
    ]

    # --- MAIN UI ---
    if filtered_df.empty:
        st.warning("No data found for the selected filters.")
    else:
        # KPI Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Transaction Count", len(filtered_df))
        if 'discount_availed' in filtered_df.columns:
            col2.metric("Total Discounts", f"₹{filtered_df['discount_availed'].sum():,.0f}")
            col3.metric("Avg Discount", f"₹{filtered_df['discount_availed'].mean():,.2f}")

        st.divider()

        # Charts using your actual columns
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("Distribution by Age Group")
            age_chart = alt.Chart(filtered_df).mark_bar().encode(
                x=alt.X("count():Q", title="Number of Transactions"),
                y=alt.Y("age_group:N", sort='-x', title="Age Group"),
                color="age_group:N",
                tooltip=["age_group", "count()"]
            ).properties(height=300)
            st.altair_chart(age_chart, use_container_width=True)

        with row1_col2:
            st.subheader("Gender Split")
            gender_chart = alt.Chart(filtered_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("count():Q"),
                color=alt.Color("gender:N", title="Gender"),
                tooltip=["gender", "count()"]
            ).properties(height=300)
            st.altair_chart(gender_chart, use_container_width=True)

        st.subheader("Daily Transaction Volume")
        line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X("yearmonthdate(purchase_date):T", title="Date"),
            y=alt.Y("count():Q", title="Volume"),
            color="product_category:N",
            tooltip=["purchase_date", "product_category", "count()"]
        ).properties(height=400).interactive()
        st.altair_chart(line_chart, use_container_width=True)

        # Data Preview
        with st.expander("View Validated Dataframe"):
            st.dataframe(filtered_df.head(100), use_container_width=True)

else:
    st.error("Missing `project1_df.csv`. Please upload the file.")
