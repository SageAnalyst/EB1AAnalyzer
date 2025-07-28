import os
import re
import fitz
import docx
import json
import random
import string
import tempfile
import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import resample
from sklearn.metrics.pairwise import cosine_similarity
from report_generator import generate_pdf_report
from fastapi.staticfiles import StaticFiles



app = FastAPI()

# Mount the "reports" folder to serve static files (like the PDF)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Import your routes or define them here
from fastapi.responses import FileResponse

app.mount("/reports", StaticFiles(directory="reports"), name="reports")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI"}

@app.get("/download-report")
def download_report():
    report_path = "reports/eb1a_risk_report.pdf"
    if os.path.exists(report_path):
        return FileResponse(path=report_path, filename="EB1A_Risk_Report.pdf", media_type="application/pdf")
    return {"error": "Report not found."}




base_dir = os.path.dirname(os.path.abspath(__file__))

petition_folder = os.path.join(base_dir, "testing_documents")
recommendation_folder = os.path.join(base_dir, "recommendation_letters")
training_json_path = os.path.join(base_dir, "training_data.json")



from fastapi.staticfiles import StaticFiles
app.mount("/reports", StaticFiles(directory="reports"), name="reports")


 

#File Utilities
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_document(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format. Please use .pdf, .docx, or .txt")

#Criterion Segmentation
def segment_by_criterion(text):
    pattern = r"(Criterion\s+\d+\s*[:\-–]\s*[^\n]*)"
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    criterion_sections = {}
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        criterion_sections[header] = body
    return criterion_sections


#Normalization
def normalize(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation))

#Expectation Matching
def detect_missing_signals(text, criterion):
    expected = evidence_expectations.get(criterion, [])
    return [f"Missing expected detail: {keyword}" for keyword in expected if keyword.lower() not in text]

def apply_advanced_rule_based_check(section_text):
    results = []
    cleaned = normalize(section_text)
    for criterion, rule in EB1A_RULES.items():
        if any(k in cleaned for k in rule["keywords"]):
            issues = []
            for phrase, message in rule["red_flags"]:
                if phrase in cleaned:
                    issues.append(message)
            issues += detect_missing_signals(cleaned, criterion)
            results.append({
                "matched_criterion": criterion,
                "issues": issues or ["None detected"],
                "excerpt": section_text[:300] + "..." if len(section_text) > 300 else section_text
            })
    return results



#Recommendation Letter Analysis
def extract_recommendation_letters(text):
    pattern = r"(Letter\s+from\s+[^\n]+|Recommendation\s+Letter\s+from\s+[^\n]+)"
    chunks = re.split(pattern, text, flags=re.IGNORECASE)
    letters = []
    for i in range(1, len(chunks), 2):
        header = chunks[i].strip()
        body = chunks[i + 1].strip() if i + 1 < len(chunks) else ""
        letters.append((header, body))
    return letters

def detect_repetitive_letters(letters, threshold=0.9):
    if len(letters) < 2:
        return []
    bodies = [normalize(body) for _, body in letters]
    vect = TfidfVectorizer().fit_transform(bodies)
    sim_matrix = cosine_similarity(vect)

    flags = []
    for i in range(len(letters)):
        for j in range(i + 1, len(letters)):
            sim_score = sim_matrix[i][j]
            if sim_score > threshold:
                flags.append((letters[i][0], letters[j][0], sim_score))
    return flags

def analyze_recommendation_folder(rec_folder_path):
    rec_texts = []
    for filename in os.listdir(rec_folder_path):
        file_path = os.path.join(rec_folder_path, filename)
        try:
            text = load_document(file_path)
            rec_texts.append((filename, text))
            print(f"📄 Loaded recommendation: {filename}")
        except Exception as e:
            print(f"⚠️ Skipping {filename}: {e}")

    full_text = "\n\n".join([t for _, t in rec_texts])
    letters = extract_recommendation_letters(full_text)
    flags = detect_repetitive_letters(letters)

    if flags:
        print("\n⚠️ Repetition Detected in Letters:")
        for l1, l2, score in flags:
            print(f" - {l1} ↔ {l2} | Similarity: {score:.2f}")
    else:
        print("\n✅ No significant repetition across letters.")

#Load Petition Documents
all_texts = []
for filename in os.listdir(petition_folder):
    file_path = os.path.join(petition_folder, filename)
    try:
        text = load_document(file_path)
        all_texts.append((filename, text))
        print(f"✅ Loaded: {filename}")
    except Exception as e:
        print(f"❌ Skipping {filename}: {e}")




EB1A_RULES = {
"Criterion 1": {
"title": "Prizes or Awards for Excellence",
"keywords": ["award", "prize", "fellowship", "recognition", "honor", "competition", "medal"],
"red_flags": [
("local", "Award appears to be local or school-level."),
("department", "Award is limited to a department."),
("not well known", "Award lacks recognized national or international prestige."),
("team", "Award may not have been given to individual specifically.")
]
},
"Criterion 2": {
"title": "Membership in Reputable Associations",
"keywords": ["member", "association", "fellow", "admission", "committee", "invitation"],
"red_flags": [
("anyone can join", "Association has open or fee-based membership."),
("fee", "Membership appears to require payment rather than achievement."),
("no review", "No evidence of expert peer review in admission process.")
]
},
"Criterion 3": {
"title": "Published Material About the Person",
"keywords": ["media", "featured", "profile", "press", "interview", "coverage", "article", "publication"],
"red_flags": [
("employer", "Media discusses employer or team, not individual."),
("marketing", "Coverage seems promotional or internal."),
("no author", "No identifiable date, source, or author.")
]
},
"Criterion 4": {
"title": "Judging the Work of Others",
"keywords": ["review", "judge", "committee", "evaluator", "dissertation", "panel", "abstract", "referee"],
"red_flags": [
("student", "Judging was at student or informal level."),
("invited", "Only invitation mentioned—no proof of actual judging."),
("newsletter", "Judging activity lacks professional/peer-reviewed status.")
]
},
"Criterion 5": {
"title": "Original Contributions of Major Significance",
"keywords": ["contribution", "innovation", "impact", "patent", "citation", "original work", "discovery"],
"red_flags": [
("internal", "Contribution recognized only within company."),
("no citation", "No citation metrics or third-party validation."),
("unpublished", "Claimed contribution is unpublished or unverified.")
]
},
"Criterion 6": {
"title": "Authorship of Scholarly Articles",
"keywords": ["author", "publication", "journal", "conference", "paper", "article", "proceedings"],
"red_flags": [
("blog", "Publication is a blog or non-scholarly source."),
("no peer review", "Article lacks peer review or editorial board."),
("not indexed", "Journal not indexed or recognized in the field.")
]
},
"Criterion 7": {
"title": "Artistic Exhibitions or Showcases",
"keywords": ["exhibit", "gallery", "artwork", "showcase", "installation", "display"],
"red_flags": [
("local", "Exhibition appears to be local or informal."),
("community", "Venue lacks artistic or national prestige."),
("not individual", "Exhibit does not highlight individual’s work.")
]
},
"Criterion 8": {
"title": "Leading or Critical Role in Distinguished Organizations",
"keywords": ["leader", "founder", "director", "head", "critical role", "project lead", "chief"],
"red_flags": [
("no impact", "Role not demonstrated to influence organization."),
("contractor", "Role appears to be limited or not senior."),
("no proof", "No documentation of contributions or results.")
]
},
"Criterion 9": {
"title": "High Salary or Remuneration",
"keywords": ["salary", "income", "remuneration", "compensation", "pay", "bonus", "offer letter"],
"red_flags": [
("no comparison", "No industry benchmark or comparative data."),
("prospective", "Salary offer is future or conditional."),
("no proof", "No pay stubs, tax returns, or official letters.")
]
},
"Criterion 10": {
"title": "Commercial Success in Performing Arts",
"keywords": ["box office", "album sales", "chart", "tour", "tickets", "downloads", "streaming", "royalties"],
"red_flags": [
("no revenue", "No data on commercial performance."),
("small venue", "Event may not demonstrate large-scale success."),
("no proof", "No press, revenue records, or independent reviews.")
]
}
}
evidence_expectations = {
"Criterion 1": ["award name", "national", "international", "competition", "selection", "number of recipients"],
"Criterion 2": ["review board", "nomination", "peer evaluation", "selection process"],
"Criterion 3": ["publication title", "media name", "author", "date", "quote about applicant"],
"Criterion 4": ["journal name", "review confirmation", "conference name", "dissertation"],
"Criterion 5": ["citation count", "h-index", "patent", "letter of impact", "commercial use"],
"Criterion 6": ["journal name", "impact factor", "peer-reviewed", "conference name"],
"Criterion 7": ["exhibition name", "venue", "city", "curator", "gallery"],
"Criterion 8": ["role title", "organization name", "project outcome", "performance data"],
"Criterion 9": ["salary amount", "comparative survey", "currency", "region", "position type"],
"Criterion 10": ["ticket sales", "album chart", "revenue", "box office", "platform"],
}

# Run Rule-Based Checks 
for filename, text in all_texts:
    print(f"\n📄 Scanning: {filename}")
    segments = segment_by_criterion(text)
    for header, content in segments.items():
        findings = apply_advanced_rule_based_check(content)
        for result in findings:
            if "None detected" not in result["issues"]:
                print(f"\n🔹 Criterion: {result['matched_criterion']}")
                print(f"Excerpt: {result['excerpt']}")
                print(f"⚠️ Issues: {result['issues']}")

#ML Model Training
training_json_path = os.path.join(base_dir, "training_data.json")

with open(training_json_path, "r") as f:
    data = [json.loads(line) for line in f]
    x = [entry["excerpt"] for entry in data]
    y = [1 if entry["issue_flag"] == "Strong Evidence" else 0 for entry in data]

# Combine and balance the dataset
combined = list(zip(x, y))
majority = [pair for pair in combined if pair[1] == 0]
minority = [pair for pair in combined if pair[1] == 1]

minority_upsampled = resample(minority, replace=True, n_samples=len(majority), random_state=42)
balanced = majority + minority_upsampled
random.shuffle(balanced)

x_bal, y_bal = zip(*balanced)

# Split the balanced dataset
x_train, x_test, y_train, y_test = train_test_split(x_bal, y_bal, random_state=42, test_size=0.2)

# Vectorize text
vect = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
x_train_vect = vect.fit_transform(x_train)
x_test_vect = vect.transform(x_test)

# Set parameter grid for GridSearch
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

# Train classifier with class weights
clf = RandomForestClassifier(random_state=42)
grid = GridSearchCV(clf, param_grid, scoring='f1_macro', cv=5, n_jobs=1, verbose=2)
grid.fit(x_train_vect, y_train)

# Evaluate
best_model = grid.best_estimator_
y_pred = best_model.predict(x_test_vect)

print("\n✅ Best Model:", best_model)
print("\n🎯 Accuracy Score:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n", classification_report(y_test, y_pred, zero_division=0))
print("\n🧾 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))


# Example usage inside your document loop
letters = extract_recommendation_letters(text)
rep_flags = detect_repetitive_letters(letters)

for l1, l2, score in rep_flags:
    print(f"⚠️ Repetition Detected: {l1} ↔ {l2} | Similarity: {score:.2f}")

@app.post("/analyze/")
async def analyze_eb1a_file(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[-1].lower()
        if ext not in [".pdf", ".docx", ".txt"]:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
            temp.write(await file.read())
            temp_path = temp.name

        text = load_document(temp_path)
        os.remove(temp_path)

        segments = segment_by_criterion(text)
        all_findings = []

        for header, content in segments.items():
            findings = apply_advanced_rule_based_check(content)
            all_findings.extend(findings)

        letters = extract_recommendation_letters(text)
        rep_flags = detect_repetitive_letters(letters)

        # ✅ Generate the PDF report
        pdf_path = generate_pdf_report({
            "rule_based_findings": all_findings,
            "repetitive_letters": [
                {"letter_1": l1, "letter_2": l2, "similarity": score}
                for l1, l2, score in rep_flags
            ]
        })

        print("✅ PDF saved at:", pdf_path)

        relative_pdf_path = os.path.join("reports", os.path.basename(pdf_path))

        return JSONResponse(content={
            "rule_based_findings": all_findings,
            "repetitive_letters": [
                {"letter_1": l1, "letter_2": l2, "similarity": score}
                for l1, l2, score in rep_flags
            ],
            "pdf_report_path": relative_pdf_path
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ✅ GET endpoint for PDF file
@app.get("/reports/{filename}")
def get_pdf(filename: str):
    file_path = os.path.join(os.getcwd(), "reports", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="application/pdf", filename=filename)
    raise HTTPException(status_code=404, detail="Report not found")

#Entry Point

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



