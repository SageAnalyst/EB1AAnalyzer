import streamlit as st
import requests



st.set_page_config(page_title="EB1A RFE Risk Analyzer", layout="wide")
st.title("📄 EB1A RFE Risk Analyzer")

uploaded_file = st.file_uploader("📄 Choose your petition file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    st.info(f"Analyzing: {uploaded_file.name}")

    API_URL = "https://eb1aanalyzer-1.onrender.com/analyze"

    response = requests.post(
        API_URL,
        files={"file": uploaded_file}
    )

    if response.status_code == 200:
        response_data = response.json()

        findings = response_data.get("rule_based_findings", [])
        repetitive_letters = response_data.get("repetitive_letters", [])
        pdf_report_path = response_data.get("pdf_report_path")

        st.subheader("🧾 Report Summary")

        if findings:
            st.success("✅ Rule-Based Analysis Results:")
            for item in findings:
                st.markdown(f"**Criterion {item['matched_criterion']}**")
                st.markdown(f"**Excerpt:**\n\n{item['excerpt']}")
                st.markdown("**⚠️ Issues Detected:**")
                for issue in item["issues"]:
                    st.markdown(f"- {issue}")
                st.markdown("---")
        else:
            st.success("✅ No rule-based issues found.")

        if repetitive_letters:
            st.warning("🔁 Repetitive Letters Detected:")
            for letter in repetitive_letters:
                st.markdown(f"- {letter}")
        else:
            st.success("✅ No significant repetition detected in letters.")

        # Download PDF Report if available
        if pdf_report_path:
            RENDER_BASE_URL = "https://eb1aanalyzer-1.onrender.com"
            full_pdf_url = f"{RENDER_BASE_URL}/{pdf_report_path.lstrip('/')}"

            # Sanitize path
            try:
                pdf_response = requests.get(full_pdf_url)
                if pdf_response.status_code == 200:
                    st.download_button(
                        label="📥 Download Full PDF Report",
                        data=pdf_response.content,
                        file_name="EB1A_RFE_Risk_Report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ PDF report could not be fetched from server.")
            except Exception as e:
                st.error(f"❌ Error downloading PDF: {e}")
        else:
            st.warning("⚠️ PDF report path not returned by the server.")
    else:
        st.error(f"❌ Server Error: {response.status_code}")
        try:
            st.json(response.json())
        except Exception:
            st.error("No JSON response received from backend.")
with st.spinner("Processing file..."):
    response = requests.post(
        API_URL,
        files={"file": uploaded_file},
        timeout=60
    )
response = requests.post(
    API_URL,
    files={"file": uploaded_file},
    timeout=60
)
