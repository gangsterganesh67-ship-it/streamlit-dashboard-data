import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Validated Retail Analytics", layout="wide")

# Title
st.title("📊 Validated Retail Dashboard")
st.markdown("This dashboard automatically maps column names and enforces data restrictions.")

# --- DATA VALIDATION & CLEANING FUNCTION ---
@st.cache_data
def load_and_validate_data():
    try:
        df = pd.read_csv("project1_df.csv")
        
        # --- COLUMN MAPPING LOGIC ---
        # This converts all columns to lowercase and replaces spaces with underscores
        # for easier internal handling, then we rename them back for display.
        original_cols = df.columns.tolist()
        normalized_cols = {col: col.strip().lower().replace(" ", "_") for col in original_cols}
        df = df.rename(columns=normalized_cols)

        # Ensure 'warehouse_block' exists even if named differently in CSV
        # (e.g., if CSV had 'Warehouse Block' or 'warehouse block')
        
        # 1. Purchase Date Restriction
        date_col = 'purchase_date' if 'purchase_date' in df.columns else None
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            df = df.dropna(subset=[date_col])

        # 2. Warehouse_block Restriction: Force Uppercase
        if 'warehouse_block' in df.columns:
            df['warehouse_block'] = df['warehouse_block'].astype(str).str.upper().str.strip()

        # 3. Net Amount Restriction: Positive Numeric
        amt_col = 'net_amount' if 'net_amount' in df.columns else None
        if amt_col:
            df[amt_col] = pd.to_numeric(df[amt_col], errors='coerce').fillna(0)
            df[amt_col] = df[amt_col].apply(lambda x: x if x > 0 else 0)

        # 4. Age Restriction: Range 18-100
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce').clip(18, 100)

        return df
    except FileNotFoundError:
        return None

df = load_and_validate_data()

if df is not None:
    # --- SIDEBAR: DATA RESTRICTIONS INFO ---
    st.sidebar.header("📋 Data Restrictions")
    st.sidebar.info("""
    **Rules Enforced:**
    - **Warehouse:** Uppercase only.
    - **Sales:** Must be > 0.
    - **Age:** Clamped to 18-100.
    """)

    # Dynamic Filters
    gender_col = 'gender' if 'gender' in df.columns else None
    cat_col = 'product_category' if 'product_category' in df.columns else None
    
    selected_gender = st.sidebar.multiselect(
        "Gender:", 
        options=df[gender_col].unique() if gender_col else [], 
        default=df[gender_col].unique() if gender_col else []
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", 
        options=df[cat_col].unique() if cat_col else [], 
        default=df[cat_col].unique() if cat_col else []
    )

    # Filtering Logic
    mask = pd.Series([True] * len(df))
    if gender_col: mask &= df[gender_col].isin(selected_gender)
    if cat_col: mask &= df[cat_col].isin(selected_category)
    filtered_df = df[mask]

    # --- MAIN UI ---
    if filtered_df.empty:
        st.warning("No data found for selected filters.")
    else:
        # Metrics
        col1, col2 = st.columns(2)
        if 'net_amount' in filtered_df.columns:
            col1.metric("Total Sales", f"₹{filtered_df['net_amount'].sum():,.0f}")
        col2.metric("Records", len(filtered_df))

        st.divider()

        # Warehouse Distribution Chart
        st.subheader("Warehouse Distribution")
        if 'warehouse_block' in filtered_df.columns and 'net_amount' in filtered_df.columns:
            chart = alt.Chart(filtered_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("sum(net_amount):Q"),
                color=alt.Color("warehouse_block:N", title="Warehouse Block"),
                tooltip=["warehouse_block", "sum(net_amount)"]
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.error("Cannot find 'Warehouse Block' or 'Net Amount' columns in your file.")
            st.write("Found columns:", list(df.columns))

        # Data Preview
        with st.expander("View Validated Data"):
            st.dataframe(filtered_df)

else:
    st.error("Please place 'project1_df.csv' in the same folder as this script.")
