# EB1A RFE Risk Analyzer
A tool that analyzes petition letters for EB1A visa applicants to identify risks of RFE (Request for Evidence) based on USCIS criteria.

# File Structure
EB1AAnalyzer/
├── app.py # Streamlit app
├── main.py # Optional: backend logic
├── report_generator.py        # Converts analysis results into PDF or DOCX report
├── training_data.json #parsed criterion from https://www.uscis.gov/policy-manual/volume-6-part-f-chapter-2,for rule-based or reference-based checks.
├── recommendation_letters/ #test data, synthetically generated
├── testing_documents/ #test data, contains appeal petition documents with  I‑140 – Extraordinary Ability gotten from https://www.uscis.gov/administrative-appeals/aao-decisions/aao-non-precedent-decisions,for validation.
├── test_petitions/ #contains synthetic petition documents used to test the application after deploying
├── reports/ #contains Final PDF output of the RFE risk report
├── requirements.txt # Python dependenciests

# Installation
git clone https://github.com/yourusername/eb1a_rfe_analyzer.git
cd eb1a_rfe_analyzer
pip install -r requirements.txt

# Run the backend
uvicorn api:app --reload

# Run the application
streamlit run app.py

# Get the report
http://localhost:8000/reports/eb1a_risk_report.pdf

