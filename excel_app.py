import streamlit as st
import pandas as pd
import io

# Page Configuration
st.set_page_config(
    page_title="DataClean Pro - Excel & CSV Automation",
    page_icon="📊",
    layout="wide"
)

# Custom Styling (Fixed Button & Text Visibility)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f0f2f6 !important;
    }
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: #1e2530;
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #00d4ff;
    }
    [data-testid="stFileUploader"] * {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #00d4ff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
    }
    /* Make Sidebar Demo Button Bright Blue and Clear */
    section[data-testid="stSidebar"] button {
        background-color: #00d4ff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
    }
    /* Metric boxes */
    div[data-testid="stMetric"] {
        background-color: #1e2530;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00d4ff;
    }
    div[data-testid="stMetric"] * {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 DataClean Pro: Automated Excel & CSV Processor")
st.write("Upload messy Excel or CSV files to automatically remove duplicates, handle missing data, and generate a clean report.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Cleaning Rules")
    remove_duplicates = st.checkbox("Remove Duplicate Rows", value=True)
    drop_empty_rows = st.checkbox("Remove Completely Empty Rows", value=True)
    
    missing_value_action = st.selectbox(
        "Handle Missing (Empty) Values:",
        ["Fill with 'N/A' or 0", "Keep as is", "Drop rows with any missing value"]
    )
    
    trim_spaces = st.checkbox("Trim Extra Spaces from Text", value=True)
    st.markdown("---")
    use_sample = st.button("🚀 Load Sample Messy Data")

# Session state for sample data
if "use_sample_data" not in st.session_state:
    st.session_state.use_sample_data = False

if use_sample:
    st.session_state.use_sample_data = True

# File Uploader
uploaded_file = st.file_uploader("📂 Upload your Excel (.xlsx) or CSV (.csv) file", type=["csv", "xlsx"])

df = None

if uploaded_file is not None:
    st.session_state.use_sample_data = False
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
elif st.session_state.use_sample_data:
    sample_data = {
        "Customer_ID": [101, 102, 102, 103, 104, None, 105, 106, 106],
        "Name": ["Rahul Sharma", "Priya Patel", "Priya Patel", "Amit Verma", None, None, "Sneha Patil", "Rohan Deshmukh", "Rohan Deshmukh"],
        "Email": ["rahul@email.com", "priya@email.com", "priya@email.com", None, "amit@email.com", None, "sneha@email.com", "rohan@email.com", "rohan@email.com"],
        "Order_Amount": [2500, 1800, 1800, 3200, None, None, 4100, 1500, 1500],
        "City": ["Mumbai", "Pune", "Pune", "Nagpur", "Nashik", None, "Mumbai", None, None]
    }
    df = pd.DataFrame(sample_data)

if df is not None:
    try:
        total_initial_rows = len(df)
        
        col_orig, col_clean = st.columns(2)
        
        with col_orig:
            st.subheader("🔍 1. Original Messy Data")
            st.dataframe(df, use_container_width=True)

        # 2. Data Cleaning Process
        cleaned_df = df.copy()

        # Remove completely empty rows first
        if drop_empty_rows:
            cleaned_df = cleaned_df.dropna(how="all")

        # Trim extra spaces in text columns
        if trim_spaces:
            str_cols = cleaned_df.select_dtypes(include=["object"]).columns
            for col in str_cols:
                cleaned_df[col] = cleaned_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Count & Remove Duplicates
        duplicates_count = int(cleaned_df.duplicated().sum())
        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()

        # Count & Handle Missing Values
        missing_rows_count = int(cleaned_df.isnull().any(axis=1).sum())
        if missing_value_action == "Fill with 'N/A' or 0":
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == "object":
                    cleaned_df[col] = cleaned_df[col].fillna("N/A")
                else:
                    cleaned_df[col] = cleaned_df[col].fillna(0)
        elif missing_value_action == "Drop rows with any missing value":
            cleaned_df = cleaned_df.dropna(how="any")

        final_valid_rows = len(cleaned_df)
        removed_rows = total_initial_rows - final_valid_rows

        with col_clean:
            st.subheader("✅ 2. Cleaned Output Data")
            st.dataframe(cleaned_df, use_container_width=True)

        # 3. Summary Report Metrics
        st.markdown("---")
        st.subheader("📈 Automated Processing Summary Report")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Input Records", total_initial_rows)
        m2.metric("Duplicates Removed", duplicates_count)
        m3.metric("Rows with Missing Data", missing_rows_count)
        m4.metric("Final Clean Records", final_valid_rows)

        # 4. Export / Download Options
        st.markdown("---")
        st.subheader("📥 Download Processed Files")
        dl_col1, dl_col2 = st.columns(2)

        csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        dl_col1.download_button(
            label="⬇️ Download Clean CSV (.csv)",
            data=csv_bytes,
            file_name="cleaned_output.csv",
            mime="text/csv"
        )

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
            summary_df = pd.DataFrame({
                "Metric": ["Total Input Rows", "Duplicates Detected", "Rows with Missing Values", "Final Clean Rows", "Total Rows Removed"],
                "Count": [total_initial_rows, duplicates_count, missing_rows_count, final_valid_rows, removed_rows]
            })
            summary_df.to_excel(writer, index=False, sheet_name="Summary_Report")
            
        excel_buffer.seek(0)

        dl_col2.download_button(
            label="⬇️ Download Clean Excel (.xlsx with Summary Sheet)",
            data=excel_buffer,
            file_name="cleaned_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")