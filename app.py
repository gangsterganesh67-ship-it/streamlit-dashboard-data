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
    
    # Updated Information Box with comprehensive attribute restrictions
    st.sidebar.info("""
    **Core Variable Restrictions:**
    - **CID:** Present & Numeric ID.
    - **TID:** Positive Transaction ID.
    - **Gender:** Strictly Male, Female, or Other.
    - **Age Group:** Categorical binned intervals.
    - **Purchase Date:** Valid temporal timestamp.
    - **Product Category:** Standard taxonomy string.
    - **Discount Availed:** Strict boolean 'Yes' or 'No'.
    - **Discount Name:** Non-empty string if Availed is 'Yes'.
    - **Discount Amount (INR):** Numeric value >= 0.
    - **Gross Amount:** Positive numerical value > 0.
    - **Net Amount:** Positive numerical value > 0.
    - **Purchase Method:** Transaction type string.
    - **Location:** Pure alphabetic city names.
    - **Warehouse_block:** Strictly uppercase alphabets only.
    """)

    st.sidebar.markdown("### 🛠️ Interactive Data Filters")

    # 1. Categorical Filters (Multi-Selects)
    selected_gender = st.sidebar.multiselect(
        "Gender:", 
        options=df["Gender"].dropna().unique(), 
        default=df["Gender"].dropna().unique()
    )
    
    selected_category = st.sidebar.multiselect(
        "Product Category:", 
        options=df["Product Category"].dropna().unique(), 
        default=df["Product Category"].dropna().unique()
    )

    selected_age = st.sidebar.multiselect(
        "Age Group:",
        options=df["Age Group"].dropna().unique(),
        default=df["Age Group"].dropna().unique()
    )

    selected_location = st.sidebar.multiselect(
        "Location (City):",
        options=df["Location"].dropna().unique(),
        default=df["Location"].dropna().unique()
    )

    selected_method = st.sidebar.multiselect(
        "Purchase Method:",
        options=df["Purchase Method"].dropna().unique(),
        default=df["Purchase Method"].dropna().unique()
    )

    selected_avail = st.sidebar.multiselect(
        "Discount Availed:",
        options=df["Discount Availed"].dropna().unique(),
        default=df["Discount Availed"].dropna().unique()
    )

    if 'Warehouse_block' in df.columns:
        selected_warehouse = st.sidebar.multiselect(
            "Warehouse Block:",
            options=df["Warehouse_block"].dropna().unique(),
            default=df["Warehouse_block"].dropna().unique()
        )

    # 2. Temporal Date Range Filter
    min_date = df["Purchase Date"].min().date()
    max_date = df["Purchase Date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Purchase Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 3. Numeric Metric Filters (Sliders)
    min_gross, max_gross = float(df["Gross Amount"].min()), float(df["Gross Amount"].max())
    gross_range = st.sidebar.slider("Gross Amount Range (₹):", min_gross, max_gross, (min_gross, max_gross))

    min_net, max_net = float(df["Net Amount"].min()), float(df["Net Amount"].max())
    net_range = st.sidebar.slider("Net Amount Range (₹):", min_net, max_net, (min_net, max_net))

    if 'Discount Amount (INR)' in df.columns:
        min_disc, max_disc = float(df["Discount Amount (INR)"].min()), float(df["Discount Amount (INR)"].max())
        disc_range = st.sidebar.slider("Discount Amount Range (₹):", min_disc, max_disc, (min_disc, max_disc))

    # Additional metadata layout documentation
    with st.sidebar.expander("View Full Measurement Details"):
        st.write("""
        - **CID / TID:** Identity keys checked for completeness.
        - **Amounts:** Evaluated mathematically to prevent calculations ≤ 0.
        - **Strings:** Validated using format checks (`isalpha`, `isupper`, etc.).
        """)

    # --- APPLY SIDEBAR FILTERS ---
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
    else:
        start_date, end_date = pd.to_datetime(min_date), pd.to_datetime(max_date)

    filtered_df = df[
        (df["Gender"].isin(selected_gender)) & 
        (df["Product Category"].isin(selected_category)) &
        (df["Age Group"].isin(selected_age)) &
        (df["Location"].isin(selected_location)) &
        (df["Purchase Method"].isin(selected_method)) &
        (df["Discount Availed"].isin(selected_avail)) &
        (df["Purchase Date"] >= start_date) &
        (df["Purchase Date"] <= end_date) &
        (df["Gross Amount"] >= gross_range[0]) &
        (df["Gross Amount"] <= gross_range[1]) &
        (df["Net Amount"] >= net_range[0]) &
        (df["Net Amount"] <= net_range[1])
    ]

    if 'Warehouse_block' in df.columns:
        filtered_df = filtered_df[filtered_df["Warehouse_block"].isin(selected_warehouse)]
        
    if 'Discount Amount (INR)' in df.columns:
        filtered_df = filtered_df[
            (filtered_df["Discount Amount (INR)"] >= disc_range[0]) &
            (filtered_df["Discount Amount (INR)"] <= disc_range[1])
        ]

    # Handle empty filtered dataframe
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your criteria inside the sidebar panels.")
    else:
        # --- KPI METRICS ---
        total_sales = filtered_df["Net Amount"].sum()
        avg_purchase = filtered_df["Net Amount"].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Net Sales", f"₹{total_sales:,.0f}")
        col2.metric("Average Transaction", f"₹{avg_purchase:,.2f}")
        col3.metric("Transaction Count", len(filtered_df))

        # --- DATA VALIDITY REGISTRY ---
        with st.expander("🔍 Data Validity & Measurement Registry", expanded=True):
            st.markdown("### 📈 Variable Validity Scorecards")
            st.caption("🔴 Red Alert Scorecards indicate attribute compliance dropped below 90%.")
            
            total_records = len(filtered_df)
            
            # --- COMPREHENSIVE VARIABLE RESTRICTIONS & VALIDATION LOGIC ---
            
            # 1. CID
            valid_cid = filtered_df['CID'].notna().sum() if 'CID' in filtered_df.columns else 0
            cid_pct = (valid_cid / total_records) * 100 if total_records > 0 else 0
            
            # 2. TID
            valid_tid = (filtered_df['TID'] > 0).sum() if 'TID' in filtered_df.columns else 0
            tid_pct = (valid_tid / total_records) * 100 if total_records > 0 else 0

            # 3. Gender (Updated Restrictive Taxonomy Validation)
            if 'Gender' in filtered_df.columns:
                valid_gender = filtered_df['Gender'].isin(['Male', 'Female', 'Other']).sum()
                gender_pct = (valid_gender / total_records) * 100 if total_records > 0 else 0
            else:
                valid_gender, gender_pct = 0, 0

            # 4. Age Group
            if 'Age Group' in filtered_df.columns:
                valid_age = filtered_df['Age Group'].apply(lambda x: '-' in str(x) or 'above' in str(x)).sum()
                age_pct = (valid_age / total_records) * 100 if total_records > 0 else 0
            else:
                valid_age, age_pct = 0, 0

            # 5. Purchase Date
            valid_dates = filtered_df['Purchase Date'].notna().sum()
            date_pct = (valid_dates / total_records) * 100 if total_records > 0 else 0

            # 6. Product Category
            if 'Product Category' in filtered_df.columns:
                valid_cat = filtered_df['Product Category'].apply(lambda x: len(str(x)) > 2 if pd.notnull(x) else False).sum()
                cat_pct = (valid_cat / total_records) * 100 if total_records > 0 else 0
            else:
                valid_cat, cat_pct = 0, 0

            # 7. Discount Availed
            if 'Discount Availed' in filtered_df.columns:
                valid_avail = filtered_df['Discount Availed'].isin(['Yes', 'No']).sum()
                avail_pct = (valid_avail / total_records) * 100 if total_records > 0 else 0
            else:
                valid_avail, avail_pct = 0, 0

            # 8. Discount Name
            if 'Discount Name' in filtered_df.columns and 'Discount Availed' in filtered_df.columns:
                valid_name = (((filtered_df['Discount Availed'] == 'Yes') & filtered_df['Discount Name'].notna()) | (filtered_df['Discount Availed'] == 'No')).sum()
                name_pct = (valid_name / total_records) * 100 if total_records > 0 else 0
            else:
                valid_name, name_pct = 0, 0

            # 9. Discount Amount
            if 'Discount Amount (INR)' in filtered_df.columns:
                valid_disc_amt = (filtered_df['Discount Amount (INR)'] >= 0).sum()
                disc_amt_pct = (valid_disc_amt / total_records) * 100 if total_records > 0 else 0
            else:
                valid_disc_amt, disc_amt_pct = 0, 0

            # 10. Gross Amount
            if 'Gross Amount' in filtered_df.columns:
                valid_gross = (filtered_df['Gross Amount'] > 0).sum()
                gross_pct = (valid_gross / total_records) * 100 if total_records > 0 else 0
            else:
                valid_gross, gross_pct = 0, 0

            # 11. Net Amount
            if 'Net Amount' in filtered_df.columns:
                valid_net = (filtered_df['Net Amount'] > 0).sum()
                net_pct = (valid_net / total_records) * 100 if total_records > 0 else 0
            else:
                valid_net, net_pct = 0, 0

            # 12. Purchase Method
            if 'Purchase Method' in filtered_df.columns:
                valid_method = filtered_df['Purchase Method'].notna().sum()
                method_pct = (valid_method / total_records) * 100 if total_records > 0 else 0
            else:
                valid_method, method_pct = 0, 0

            # 13. Location
            if 'Location' in filtered_df.columns:
                valid_loc = filtered_df['Location'].apply(lambda x: str(x).replace(" ", "").isalpha() if pd.notnull(x) else False).sum()
                loc_pct = (valid_loc / total_records) * 100 if total_records > 0 else 0
            else:
                valid_loc, loc_pct = 0, 0

            # 14. Warehouse Block
            if 'Warehouse_block' in filtered_df.columns:
                valid_warehouse = filtered_df['Warehouse_block'].apply(lambda x: str(x).isupper() if pd.notnull(x) else False).sum()
                warehouse_pct = (valid_warehouse / total_records) * 100 if total_records > 0 else 0
            else:
                valid_warehouse, warehouse_pct = 0, 0

            # --- NATIVE STREAMLIT CONDITIONAL SCORECARD GENERATOR ---
            def render_native_card(label, score):
                if score < 90:
                    st.error(f"⚠️ **{label}** \n## {score:.1f}%")
                else:
                    st.info(f"**{label}** \n## {score:.1f}%")

            # --- RENDER SCORECARD GRID ---
            sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
            with sc_col1:
                render_native_card("CID", cid_pct)
                render_native_card("Purchase Date", date_pct)
                render_native_card("Discount Amount", disc_amt_pct)
                render_native_card("Location", loc_pct)
            with sc_col2:
                render_native_card("TID", tid_pct)
                render_native_card("Product Category", cat_pct)
                render_native_card("Gross Amount", gross_pct)
                render_native_card("Warehouse Block", warehouse_pct)
            with sc_col3:
                render_native_card("Gender", gender_pct)
                render_native_card("Discount Availed", avail_pct)
                render_native_card("Net Amount", net_pct)
            with sc_col4:
                render_native_card("Age Group", age_pct)
                render_native_card("Discount Name", name_pct)
                render_native_card("Purchase Method", method_pct)

            st.markdown("---")
            st.markdown("### 📋 Detailed Rule Log")

            # Compile Full Variable Registry DataFrame
            registry_data = {
                "Variable / Attribute Rule": [
                    "CID (Must be Present/Numeric)",
                    "TID (Must be Positive Transaction ID)",
                    "Gender Taxonomy Compliance (Strictly Male/Female/Other)",
                    "Age Group Formats (Categorical Intervals)",
                    "Purchase Date Temporal Presence",
                    "Product Category Compliance (Valid Taxonomy)",
                    "Discount Availed Value Range (Yes/No)",
                    "Discount Name Integrity (Present if Availed)",
                    "Discount Amount Bounds (Numeric >= 0)",
                    "Gross Amount Value Range (Positive > 0)",
                    "Net Amount Value Range (Positive > 0)",
                    "Purchase Method Integrity (Valid Method Text)",
                    "Location Rule Validation (Alphabetic City Names)",
                    "Warehouse_block Format (Strictly Uppercase)"
                ],
                "Valid Records": [
                    valid_cid, valid_tid, valid_gender, valid_age, valid_dates, 
                    valid_cat, valid_avail, valid_name, valid_disc_amt, valid_gross, 
                    valid_net, valid_method, valid_loc, valid_warehouse
                ],
                "Total Evaluated": [total_records] * 14,
                "Validity Score": [
                    f"{cid_pct:.2f}%", f"{tid_pct:.2f}%", f"{gender_pct:.2f}%", f"{age_pct:.2f}%", f"{date_pct:.2f}%",
                    f"{cat_pct:.2f}%", f"{avail_pct:.2f}%", f"{name_pct:.2f}%", f"{disc_amt_pct:.2f}%", f"{gross_pct:.2f}%",
                    f"{net_pct:.2f}%", f"{method_pct:.2f}%", f"{loc_pct:.2f}%", f"{warehouse_pct:.2f}%"
                ],
                "Status": [
                    "🟢 Compliant" if cid_pct == 100 else "⚠️ Missing CIDs",
                    "🟢 Compliant" if tid_pct == 100 else "⚠️ Corrupt TIDs Found",
                    "🟢 Compliant" if gender_pct == 100 else "⚠️ Invalid Gender Category Encountered",
                    "🟢 Compliant" if age_pct == 100 else "⚠️ Unexpected Age Category Format",
                    "🟢 Compliant" if date_pct == 100 else "⚠️ Missing Temporal Data",
                    "🟢 Compliant" if cat_pct == 100 else "⚠️ Missing Category Entries",
                    "🟢 Compliant" if avail_pct == 100 else "⚠️ Invalid Flags Found",
                    "🟢 Compliant" if name_pct == 100 else "⚠️ Missing Promotion Identifiers",
                    "🟢 Compliant" if disc_amt_pct == 100 else "⚠️ Negative Discount Values Found",
                    "🟢 Compliant" if gross_pct == 100 else "⚠️ Erroneous Gross Calculations",
                    "🟢 Compliant" if net_pct == 100 else "⚠️ Non-Compliant Rows Detected",
                    "🟢 Compliant" if method_pct == 100 else "⚠️ Missing Payment Methods",
                    "🟢 Compliant" if loc_pct == 100 else "⚠️ Format Discrepancies in Location Strings",
                    "🟢 Compliant" if warehouse_pct == 100 else "⚠️ Non-Compliant Rows Detected"
                ]
            }
            registry_df = pd.DataFrame(registry_data)
            st.dataframe(registry_df, use_container_width=True, hide_index=True)

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

        # --- DATA PREVIEW & VARIABLE INSPECTION ---
        with st.expander("🔍 View/Export Filtered Data & Inspect Variables", expanded=False):
            st.markdown("### 👁️ Individual Variable Viewer")
            
            # Generate column list from available variables
            available_columns = list(filtered_df.columns)
            
            # Dropdown menu to view a specific column
            selected_var = st.selectbox(
                "Select a variable to isolate and inspect its contents:",
                options=["All Columns Combined"] + available_columns
            )
            
            # Render selected target data view
            if selected_var == "All Columns Combined":
                st.dataframe(filtered_df.head(100), use_container_width=True)
            else:
                st.markdown(f"Displaying data preview specifically for **{selected_var}**:")
                st.dataframe(filtered_df[[selected_var]].head(100), use_container_width=True)
                
            # Global Export Actions
            st.markdown("---")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Filtered CSV",
                data=csv,
                file_name='retail_data_export.csv',
                mime='text/csv',
            )

else:
    st.error("Error: 'project1_df.csv' not found. Please ensure the file is in the same directory as this script.")
