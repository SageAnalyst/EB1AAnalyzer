# EB1A RFE Risk Analyzer
A tool that analyzes petition letters for EB1A visa applicants to identify risks of RFE (Request for Evidence) based on USCIS criteria.

# FEATURES
-Upload EB1A petition or recommendation letter (PDF, DOCX).

-Get a detailed risk report based on USCIS EB1A criteria.

-Rule-based and heuristic matching using real AAO decisions and USCIS guidelines.

-Exports PDF report with actionable recommendations.

# FILE STRUCTURE
EB1AAnalyzer/
├── app.py                    # Streamlit frontend interface
├── main.py                   # FastAPI backend handling file uploads and response
├── report_generator.py       # Converts API results into PDF report
├── training_data.json        # Structured USCIS EB1A criteria for rule-based analysis
├── recommendation_letters/  # Sample synthetic recommendation letters
├── testing_documents/       # Real AAO EB1A petitions for evaluation
├── test_petitions/          # Synthetic petition documents for QA testing
├── reports/                 # Final reports generated after processing
├── requirements.txt         # Python dependencies
├── render-build.sh          # Required for installing WeasyPrint on Render
├── Procfile                 # Specifies how to run FastAPI on Render
├── .gitignore               # Ignore cache, env, reports, etc.
├── .devcontainer/           # For development inside VS Code containers (optional)
└── README.md                # right here


# INSTALLATION
-- CLONE REPOSITORY
git clone https://github.com/yourusername/eb1a_rfe_analyzer.git
cd eb1a_rfe_analyzer
pip install -r requirements.txt

# LOCAL DEPLOYMENT
-- Start Backend (FastAPI)
uvicorn main:app --reload

-- Launch Frontend (Streamlit)
streamlit run app.py

-- Get the report
http://localhost:8000/reports/eb1a_risk_report.pdf

# CLOUD DEPLOYMENT(RENDER)
-- Backend Service (FastAPI)
main.py is used
Add a Procfile(START COMMAND):
      web: uvicorn main:app --host 0.0.0.0 --port 10000
Add render-build.sh:
      apt-get update && apt-get install -y build-essential libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
NB:Make sure this is added under Build Command in Render dashboard.

-- Frontend Service (Streamlit)
Connect app.py in a separate Render service.
Update API_URL in app.py to match the deployed backend URL

# LIMITATIONS
May generate false positives/negatives depending on document structure.
Accuracy is highly dependent on how well the extracted text matches USCIS phrasing.
Doesn't replace legal judgment.

# ACKNOWLEDGMENTS
USCIS Policy Manual Volume 6, Part F, Chapter 2
AAO Non-Precedent Decisions Repository




