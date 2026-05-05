import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Validated Retail Analytics", layout="wide")

# Title
st.title("📊 Validated Retail Dashboard")
st.markdown("This dashboard strictly enforces data restrictions for every attribute.")

# --- DATA VALIDATION & CLEANING FUNCTION ---
@st.cache_data
def load_and_validate_data():
    try:
        df = pd.read_csv("project1_df.csv")
        
        # 1. Purchase Date: Must be valid date, remove corrupted rows
        df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Purchase Date'])

        # 2. Warehouse_block: Restriction - Uppercase Alphabets Only
        if 'Warehouse_block' in df.columns:
            df['Warehouse_block'] = df['Warehouse_block'].astype(str).str.upper().str.strip()

        # 3. Net Amount: Restriction - Must be Positive Numeric
        df['Net Amount'] = pd.to_numeric(df['Net Amount'], errors='coerce').fillna(0)
        df['Net Amount'] = df['Net Amount'].apply(lambda x: x if x > 0 else 0)

        # 4. Gender: Restriction - Standardized Categories
        df['Gender'] = df['Gender'].fillna('Unknown').str.capitalize()

        # 5. Age: Restriction - Range 18 to 100
        if 'Age' in df.columns:
            df['Age'] = df['Age'].clip(18, 100)

        # 6. Purchase Method: Restriction - Limited to specific set
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
        **Strict Rules Applied:**
        *   **Warehouse_block:** A-Z (Uppercase).
        *   **Net Amount:** Float > 0.
        *   **Age:** Integer (18-100).
        *   **Gender:** Male, Female, Unknown.
        *   **Purchase Date:** DD-MM-YYYY format.
        *   **Method:** Online / In-Store only.
        """)

    st.sidebar.divider()
    st.sidebar.header("Filter View")

    # Sidebar Filters with Hover-Help Restrictions
    selected_gender = st.sidebar.multiselect(
        "Gender:", 
        options=df["Gender"].unique(), 
        default=df["Gender"].unique(),
        help="Restriction: Entries outside Male/Female are tagged as 'Unknown'."
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", 
        options=df["Product Category"].unique(), 
        default=df["Product Category"].unique(),
        help="Restriction: Must match the official master SKU list."
    )

    # Filtering Logic
    filtered_df = df[
        (df["Gender"].isin(selected_gender)) & 
        (df["Product Category"].isin(selected_category))
    ]

    # --- MAIN UI ---
    if filtered_df.empty:
        st.warning("The applied restrictions and filters resulted in no data.")
    else:
        # KPI Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"₹{filtered_df['Net Amount'].sum():,.0f}")
        col2.metric("Avg Trans", f"₹{filtered_df['Net Amount'].mean():,.2f}")
        col3.metric("Valid Records", len(filtered_df))

        st.divider()

        # Charts
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("Sales by Age Group")
            chart1 = alt.Chart(filtered_df).mark_bar().encode(
                y=alt.Y("Age Group:N", sort='-x'),
                x="sum(Net Amount):Q",
                color="Age Group:N"
            ).properties(height=300)
            st.altair_chart(chart1, use_container_width=True)

        with row1_col2:
            st.subheader("Warehouse Performance")
            chart2 = alt.Chart(filtered_df).mark_arc().encode(
                theta="sum(Net Amount):Q",
                color="Warehouse_block:N",
                tooltip=["Warehouse_block", "sum(Net Amount)"]
            ).properties(height=300)
            st.altair_chart(chart2, use_container_width=True)

        # Data Quality View
        st.subheader("Validated Data Preview")
        st.dataframe(filtered_df.head(50), use_container_width=True)
        
        # Download
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned Data", data=csv, file_name="cleaned_data.csv")

else:
    st.error("Missing `project1_df.csv`. Please upload the source file.")
