import streamlit as st
import requests
import os

# 🎨 Style the app
st.set_page_config(page_title="EB1A Petition Analyzer", layout="wide")
st.markdown("""
    <style>
        .stDownloadButton {
            font-size: 18px;
            font-weight: bold;
            padding: 0.6em 1.5em;
            background-color: #0044cc;
            color: white;
            border-radius: 8px;
        }
        .stDownloadButton:hover {
            background-color: #003399;
        }
    </style>
""", unsafe_allow_html=True)

# 📄 App Title and Instructions
st.title("🧠 EB-1A Petition Analyzer")
st.markdown("Upload a draft EB-1A petition (PDF, DOCX, or TXT). We'll analyze it for risks and rule-based issues.")

# ✍️ Custom Report Filename Input
st.markdown("### ✍️ Name your report")
custom_filename = st.text_input("Enter a short name for the report (e.g. applicant name or case ref):", value="EB1A_Report")

# 📁 File Upload
uploaded_file = st.file_uploader("📄 Choose your petition file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with st.spinner("Analyzing file..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

        try:
            response = requests.post("http://127.0.0.1:8000/analyze/", files=files)
            status = response.status_code
            data = response.json()

            st.write("📦 Response status code:", status)
            st.write("📦 Raw response keys:", list(data.keys()))
            st.json(data)  # Optional debug

            if status == 200:
                results = data.get("rule_based_findings", [])
                repetitions = data.get("repetitive_letters", [])
                pdf_path = data.get("pdf_report_path")

                with st.container():
                    st.markdown("### 🧾 Report Summary")

                    if results:
                        st.success("✅ Rule-Based Analysis Results:")
                        for item in results:
                            st.subheader(item["matched_criterion"])
                            st.markdown(f"**Excerpt:**\n> {item['excerpt']}")
                            st.markdown("**⚠️ Issues Detected:**")
                            for issue in item["issues"]:
                                st.markdown(f"- {issue}")
                            st.markdown("---")
                    else:
                        st.info("✅ No rule-based risks or issues found.")

                    if repetitions:
                        st.warning("⚠️ Repetitive Recommendation Letters Detected:")
                        for rep in repetitions:
                            st.markdown(f"- {rep['letter_1']} ↔ {rep['letter_2']} | Similarity Score: {rep['similarity']:.2f}")
                    else:
                        st.success("✅ No significant repetition detected in letters.")

                # ✅ PDF Download Button
                if pdf_path and os.path.exists(pdf_path):
                    full_pdf_path = os.path.join("reports", os.path.basename(pdf_path))
    
                    if os.path.exists(full_pdf_path):
                        with open(full_pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Risk Report (PDF)",
                                data=f,
                                file_name=f"{custom_filename.strip().replace(' ', '_')}.pdf",
                                mime="application/pdf")
                    else:
                        st.warning("⚠️ PDF file not found on the server.")


            else:
                st.error(f"❌ Server Error: {status}")
                st.json(data)

        except requests.exceptions.ConnectionError:
            st.error("🚫 Cannot connect to the FastAPI server. Is it running on http://127.0.0.1:8000?")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
