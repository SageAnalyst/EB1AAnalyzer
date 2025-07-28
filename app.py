import streamlit as st
import requests
from io import BytesIO

# Set your deployed backend URL
RENDER_BASE_URL = "https://eb1aanalyzer-1.onrender.com"
API_URL = f"{RENDER_BASE_URL}/analyze/"

st.set_page_config(page_title="EB1A Risk Analyzer", layout="centered")

st.title("🧠 EB1A Risk Analyzer")
st.write("Upload your PDF to receive a detailed RFE risk analysis report.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Warm-up ping (optional, helps avoid timeout due to cold start)
    with st.spinner("Waking up backend..."):
        try:
            requests.get(RENDER_BASE_URL, timeout=10)
        except Exception as e:
            st.info("Backend might be waking up. Hang tight...")

    # Process the file
    with st.spinner("Processing file..."):
        try:
            files = {"file": uploaded_file}
            response = requests.post(API_URL, files=files, timeout=120)

            if response.status_code == 200:
                # Display success and download button
                st.success("✅ Analysis complete!")
                pdf_report = BytesIO(response.content)
                st.download_button(
                    label="📄 Download Risk Report PDF",
                    data=pdf_report,
                    file_name="EB1A_RFE_Risk_Report.pdf",
                    mime="application/pdf",
                )
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("❌ Connection timed out. Please try again in a few moments.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to API: {e}")
