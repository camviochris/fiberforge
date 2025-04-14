import streamlit as st
import pandas as pd
from converters import adtran, dzs, calix  # Add calix when ready

st.set_page_config(page_title="FiberForge", layout="centered")

if "step" not in st.session_state:
    st.session_state.step = 1

st.title("FiberForge")
st.caption("Molding messy inventory into streamlined onboarding — one device at a time.")

if st.session_state.step == 1:
    st.header("Welcome to FiberForge")
    st.markdown("""
    This tool helps convert fiber inventory from manufacturer-specific formats
    into a streamlined structure ready for Camvio-style onboarding.

    1. Choose your manufacturer
    2. Upload your device list
    3. Preview and confirm detected output
    4. Download the converted CSV
    
    All processing is in-memory. No SN, MAC, or FSAN is stored.
    """)
    if st.button("Get Started"):
        st.session_state.step = 2

elif st.session_state.step == 2:
    st.header("Select Manufacturer")
    manufacturer = st.radio("Choose a manufacturer:", ["Adtran", "DZS", "Calix", "Other"])
    st.session_state.manufacturer = manufacturer
    col1, col2 = st.columns(2)
    if col1.button("Next"):
        st.session_state.step = 3
    if col2.button("Back"):
        st.session_state.step = 1

elif st.session_state.step == 3:
    st.header("Upload Inventory File")
    st.markdown("Supported formats: .xlsx or .csv")
    uploaded_file = st.file_uploader("Choose your file", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.df = df
            st.success("File uploaded successfully.")
            if st.button("Next"):
                st.session_state.step = 4
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if st.button("Back"):
        st.session_state.step = 2

elif st.session_state.step == 4:
    st.header("Review Device Detection & Preview")
    manufacturer = st.session_state.get("manufacturer")
    df = st.session_state.get("df")

    if df is not None:
        try:
            if manufacturer == "Adtran":
                preview_df, file_name = adtran.convert(df)
            elif manufacturer == "DZS":
                preview_df, file_name = dzs.convert(df)
            elif manufacturer == "Calix":
                preview_df, file_name = calix.convert(df)
            else:
                st.warning("'Other' not yet supported. Please select a supported manufacturer.")
                preview_df = None
                file_name = None

            if preview_df is not None:
                st.dataframe(preview_df.head(10), use_container_width=True)
                csv_output = preview_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Converted File", data=csv_output, file_name=file_name, mime="text/csv")
        except Exception as e:
            st.error(f"Conversion error: {e}")

    if st.button("Back"):
        st.session_state.step = 3
    if st.button("Start Over"):
        st.session_state.step = 1
