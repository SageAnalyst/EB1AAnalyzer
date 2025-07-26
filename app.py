import streamlit as st
import requests

st.set_page_config(page_title="EB1A Petition Analyzer", layout="wide")
st.title("🧠 EB-1A Petition Analyzer")

st.markdown("Upload a draft EB-1A petition (PDF, DOCX, or TXT). We'll analyze it for risks and rule-based issues.")

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
            st.json(data)  # Display full raw JSON

            if status == 200:
                results = data.get("rule_based_findings", [])
                repetitions = data.get("repetitive_letters", [])

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
                    for l1, l2, score in repetitions:
                        st.markdown(f"- {l1} ↔ {l2} | Similarity Score: {score:.2f}")
                else:
                    st.success("✅ No significant repetition detected in letters.")

            else:
                st.error(f"❌ Server Error: {status}")
                st.json(data)

        except requests.exceptions.ConnectionError:
            st.error("🚫 Cannot connect to the FastAPI server. Is it running on http://127.0.0.1:8000?")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
