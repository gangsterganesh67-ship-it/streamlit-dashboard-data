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
    df = pd.read_csv("project1_df.csv")
    # Clean dates for time-series plotting
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], dayfirst=True)
    return df

try:
    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Data")
    
    selected_gender = st.sidebar.multiselect(
        "Gender:", options=df["Gender"].unique(), default=df["Gender"].unique()
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", options=df["Product Category"].unique(), default=df["Product Category"].unique()
    )

    # Apply Filters
    filtered_df = df[
        (df["Gender"].isin(selected_gender)) & 
        (df["Product Category"].isin(selected_category))
    ]

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
        # Horizontal Bar Chart
        bar_chart = alt.Chart(filtered_df).mark_bar().encode(
            y=alt.Y("Age Group:N", sort='-x', title="Age Group"),
            x=alt.X("sum(Net Amount):Q", title="Total Net Amount"),
            color=alt.Color("Age Group:N", legend=None),
            tooltip=["Age Group", "sum(Net Amount)"]
        ).properties(height=300).interactive()
        
        st.altair_chart(bar_chart, use_container_width=True)

    with row1_col2:
        st.subheader("Location vs Purchase Method")
        # Heatmap / Punchcard Chart
        heatmap = alt.Chart(filtered_df).mark_rect().encode(
            x=alt.X("Location:N", title="City"),
            y=alt.Y("Purchase Method:N", title="Payment Method"),
            color=alt.Color("count():Q", scale=alt.Scale(scheme='greens'), title="Count"),
            tooltip=["Location", "Purchase Method", "count()"]
        ).properties(height=300)
        
        st.altair_chart(heatmap, use_container_width=True)

    st.subheader("Daily Sales Trend")
    # Time Series Line Chart
    line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("yearmonthdate(Purchase Date):T", title="Date"),
        y=alt.Y("sum(Net Amount):Q", title="Daily Revenue"),
        color=alt.Color("Product Category:N"),
        tooltip=["yearmonthdate(Purchase Date)", "Product Category", "sum(Net Amount)"]
    ).properties(height=400).interactive()

    st.altair_chart(line_chart, use_container_width=True)

    # --- DATA PREVIEW ---
    with st.expander("View Filtered Dataframe"):
        st.write(filtered_df.head(100))

except FileNotFoundError:
    st.error("Error: 'project1_df.csv' not found. Please place the file in the same folder.")