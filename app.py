import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(page_title="Retail Analytics (Altair)", layout="wide")

# Title
st.title("📊 Retail Dashboard with Altair")
st.markdown("Analyzing `project1_df.csv` using declarative visualizations.")

# Load and Clean Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("project1_df.csv")
        # Clean dates for time-series plotting
        df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True, errors='coerce')
        # Standardize Warehouse_block to Uppercase as per attribute restrictions
        if 'Warehouse_block' in df.columns:
            df['Warehouse_block'] = df['Warehouse_block'].astype(str).str.upper()
        return df.dropna(subset=['Purchase Date'])
    except FileNotFoundError:
        return None

df = load_data()

if df is not None:
    # --- SIDEBAR FILTERS & DATA CONSTRAINTS ---
    st.sidebar.header("Filter & Data Info")
    
    # Information Box for critical attribute constraints
    st.sidebar.info("""
    **Attribute Restrictions:**
    - **Warehouse_block:** Strictly uppercase alphabets only.
    - **Net Amount:** Must be a positive numerical value.
    """)

    # Multi-select with hover-over help constraints
    selected_gender = st.sidebar.multiselect(
        "Gender:", 
        options=df["Gender"].unique(), 
        default=df["Gender"].unique(),
        help="Constraint: Valid entries are limited to 'Male', 'Female', or 'Unknown'."
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", 
        options=df["Product Category"].unique(), 
        default=df["Product Category"].unique(),
        help="Constraint: Must align with the standardized product taxonomy."
    )

    # Additional attribute info in sidebar
    with st.sidebar.expander("View Full Attribute Limits"):
        st.write("""
        - **Age Group:** Categorical (e.g., 18-24, 25-34).
        - **Location:** Valid City names only.
        - **Purchase Method:** 'Online' or 'In-Store'.
        """)

    # Apply Filters
    filtered_df = df[
        (df["Gender"].isin(selected_gender)) & 
        (df["Product Category"].isin(selected_category))
    ]

    # Handle empty filtered dataframe
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your criteria.")
    else:
        # --- KPI METRICS ---
        total_sales = filtered_df["Net Amount"].sum()
        avg_purchase = filtered_df["Net Amount"].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Net Sales", f"₹{total_sales:,.0f}")
        col2.metric("Average Transaction", f"₹{avg_purchase:,.2f}")
        col3.metric("Transaction Count", len(filtered_df))

        st.divider()

        # --- ALTAIR CHARTS ---
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("Sales by Age Group")
            bar_chart = alt.Chart(filtered_df).mark_bar().encode(
                y=alt.Y("Age Group:N", sort='-x', title="Age Group"),
                x=alt.X("sum(Net Amount):Q", title="Total Net Amount"),
                color=alt.Color("Age Group:N", legend=None),
                tooltip=["Age Group", "sum(Net Amount)"]
            ).properties(height=300).interactive()
            
            st.altair_chart(bar_chart, use_container_width=True)

        with row1_col2:
            st.subheader("Location vs Purchase Method")
            heatmap = alt.Chart(filtered_df).mark_rect().encode(
                x=alt.X("Location:N", title="City"),
                y=alt.Y("Purchase Method:N", title="Payment Method"),
                color=alt.Color("count():Q", scale=alt.Scale(scheme='greens'), title="Count"),
                tooltip=["Location", "Purchase Method", "count()"]
            ).properties(height=300)
            
            st.altair_chart(heatmap, use_container_width=True)

        st.subheader("Daily Sales Trend")
        line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X("yearmonthdate(Purchase Date):T", title="Date"),
            y=alt.Y("sum(Net Amount):Q", title="Daily Revenue"),
            color=alt.Color("Product Category:N"),
            tooltip=["yearmonthdate(Purchase Date)", "Product Category", "sum(Net Amount)"]
        ).properties(height=400).interactive()

        st.altair_chart(line_chart, use_container_width=True)

        # --- DATA PREVIEW & DOWNLOAD ---
        with st.expander("View/Export Filtered Data"):
            st.dataframe(filtered_df.head(100), use_container_width=True)
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered CSV",
                data=csv,
                file_name='retail_data_export.csv',
                mime='text/csv',
            )

else:
    st.error("Error: 'project1_df.csv' not found. Please ensure the file is in the same directory as this script.")
