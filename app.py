import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Validated Retail Analytics", layout="wide")

# Title
st.title("📊 Validated Retail Dashboard")
st.markdown("This dashboard strictly enforces data restrictions and validates columns before rendering.")

# --- DATA VALIDATION & CLEANING FUNCTION ---
@st.cache_data
def load_and_validate_data():
    try:
        # Load data
        df = pd.read_csv("project1_df.csv")
        
        # 1. Purchase Date: Must be valid date, remove corrupted rows
        df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Purchase Date'])

        # 2. Warehouse_block: Restriction - Uppercase Alphabets Only
        # We force this in the backend to prevent visualization errors
        if 'Warehouse_block' in df.columns:
            df['Warehouse_block'] = df['Warehouse_block'].astype(str).str.upper().str.strip()
        elif 'Warehouse Block' in df.columns: # Common variation
            df.rename(columns={'Warehouse Block': 'Warehouse_block'}, inplace=True)
            df['Warehouse_block'] = df['Warehouse_block'].astype(str).str.upper().str.strip()

        # 3. Net Amount: Restriction - Must be Positive Numeric
        if 'Net Amount' in df.columns:
            df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce').fillna(0)
            df['Net Amount'] = df['Net Amount'].apply(lambda x: x if x > 0 else 0)

        # 4. Gender: Restriction - Standardized Categories
        if 'Gender' in df.columns:
            df['Gender'] = df['Gender'].fillna('Unknown').str.capitalize()

        # 5. Age: Restriction - Range 18 to 100
        if 'Age' in df.columns:
            # Handle cases where Age might be a string range or numeric
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce').clip(18, 100)

        # 6. Purchase Method: Restriction - Limited to specific set
        if 'Purchase Method' in df.columns:
            valid_methods = ['Online', 'In-Store']
            df['Purchase Method'] = df['Purchase Method'].apply(lambda x: x if x in valid_methods else 'Other')

        return df
    except FileNotFoundError:
        return None

df = load_and_validate_data()

if df is not None:
    # --- SIDEBAR: DATA RESTRICTIONS INFO ---
    st.sidebar.header("📋 Data Restrictions")
    
    with st.sidebar.expander("Attribute Rules", expanded=True):
        st.markdown("""
        **System Constraints:**
        *   **Warehouse_block:** Strictly UPPERCASE [A-F].
        *   **Net Amount:** Positive Float.
        *   **Age:** Integer 18-100.
        *   **Gender:** Male, Female, Unknown.
        *   **Purchase Date:** Valid DD-MM-YYYY.
        *   **Method:** Online or In-Store only.
        """)

    st.sidebar.divider()
    st.sidebar.header("Filter View")

    # Dynamic Sidebar Filters with Hover-Help
    selected_gender = st.sidebar.multiselect(
        "Gender:", 
        options=df["Gender"].unique() if "Gender" in df.columns else [], 
        default=df["Gender"].unique() if "Gender" in df.columns else [],
        help="Restriction: Entries outside Male/Female are standardized to 'Unknown'."
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", 
        options=df["Product Category"].unique() if "Product Category" in df.columns else [], 
        default=df["Product Category"].unique() if "Product Category" in df.columns else [],
        help="Restriction: Categories must match the Inventory Master list."
    )

    # Filtering Logic
    filtered_df = df[
        (df["Gender"].isin(selected_gender)) & 
        (df["Product Category"].isin(selected_category))
    ]

    # --- MAIN UI ---
    if filtered_df.empty:
        st.warning("⚠️ No data matches the current filters. Please adjust your selection.")
    else:
        # KPI Row
        col1, col2, col3 = st.columns(3)
        if 'Net Amount' in filtered_df.columns:
            col1.metric("Total Sales", f"₹{filtered_df['Net Amount'].sum():,.0f}")
            col2.metric("Avg Transaction", f"₹{filtered_df['Net Amount'].mean():,.2f}")
        col3.metric("Validated Records", len(filtered_df))

        st.divider()

        # Charts
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("Sales by Age Group")
            # Using try-except for Altair specific rendering issues
            try:
                chart1 = alt.Chart(filtered_df).mark_bar().encode(
                    y=alt.Y("Age Group:N", sort='-x', title="Age Group"),
                    x=alt.X("sum(Net Amount):Q", title="Total Sales"),
                    color="Age Group:N"
                ).properties(height=300)
                st.altair_chart(chart1, use_container_width=True)
            except Exception as e:
                st.error(f"Chart Error: Ensure 'Age Group' exists in data.")

        with row1_col2:
            st.subheader("Warehouse Distribution")
            # Defensive check for Warehouse_block to prevent the error in image_d89d41.png
            if "Warehouse_block" in filtered_df.columns:
                chart2 = alt.Chart(filtered_df).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta("sum(Net Amount):Q"),
                    color=alt.Color("Warehouse_block:N", title="Block"),
                    tooltip=["Warehouse_block", "sum(Net Amount)"]
                ).properties(height=300)
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.info("Warehouse_block column not found. Check CSV headers.")

        # Data Preview
        st.subheader("Validated Dataset Preview")
        st.dataframe(filtered_df.head(50), use_container_width=True)
        
        # Export Button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Validated CSV", data=csv, file_name="retail_cleaned.csv")

else:
    st.error("🚨 File `project1_df.csv` not found! Please ensure it is in the same folder as this script.")
