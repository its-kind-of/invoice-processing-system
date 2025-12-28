import streamlit as st
import requests
import pandas as  pd

API_URL = "http://127.0.0.1:8000/extract-invoice"

st.set_page_config(
    page_title="Invoice Extraction Demo",
    layout="centered"
)

st.title("Invoice Extraction Demo")
st.caption("OCR AI Powered invoice parsing")

uploaded_files = st.file_uploader(
    "Upload an invoice PDF",
    type=['pdf'],
    accept_multiple_files=True
)

results = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.info(f"Processing {uploaded_file.name}...")

        files = {
            "file" : (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }

        response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            st.error(f"Failed: {uploaded_file.name}")
            st.code(response.text)
            continue

        data = response.json()
        data['file_name'] = uploaded_file.name

        if data.get("confidence") == "high":
            data['review_status'] = "Auto-approved"
        else:
            data['review_status'] = "Review-recommended"

        results.append(data)



    if results:
        df = pd.DataFrame(results)
        st.success("Batch extraction completed")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV", 
            csv, 
            "invoices_csv", 
            "text/csv"
        )
    
