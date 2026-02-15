from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import joblib
import pandas as pd
from datetime import datetime
import os

# PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from backend.rule_engine import rule_based_risk
from backend.utils import recommend_department
from backend.database import patients

app = FastAPI()

# Session middleware (login)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="templates")

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load ML model
model = joblib.load("triage_model.pkl")
le_gender = joblib.load("le_gender.pkl")
le_condition = joblib.load("le_condition.pkl")
le_risk = joblib.load("le_risk.pkl")

# Dummy doctor credentials
DOCTOR_USERNAME = "doctor"
DOCTOR_PASSWORD = "1234"


# ===============================
# Generate Patient ID
# ===============================
def generate_patient_id(dob):
    dob_str = dob.replace("-", "")
    count = patients.count_documents({"dob": dob})
    return f"P{dob_str}-{count+1:03d}"


# ===============================
# Login
# ===============================
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == DOCTOR_USERNAME and password == DOCTOR_PASSWORD:
        request.session["doctor"] = username
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid credentials"
    })


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# ===============================
# Add Patient Page
# ===============================
@app.get("/add_patient", response_class=HTMLResponse)
async def add_patient_page(request: Request):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("add_patient.html", {"request": request})


# ===============================
# Save Patient
# ===============================
@app.post("/add_patient")
async def add_patient(
    name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    condition: str = Form(...),
    symptoms: list[str] = Form([]),
    custom_symptom: str = Form(""),
    bp: int = Form(...),
    hr: int = Form(...),
    temp: float = Form(...),
    ehr_file: UploadFile = File(None)
):
    if temp > 45:
        temp = (temp - 32) * 5 / 9

    birth = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

    patient_id = generate_patient_id(dob)

    # Ensure symptoms is always a list
    if isinstance(symptoms, str):
        symptom_list = [symptoms]
    else:
        symptom_list = symptoms.copy()

    if custom_symptom.strip():
        symptom_list.append(custom_symptom.strip())

    all_symptoms = ", ".join(symptom_list) if symptom_list else "—"

    # Save EHR
    ehr_path = ""
    if ehr_file and ehr_file.filename:
        filename = f"{patient_id}_{ehr_file.filename}"
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_location, "wb") as f:
            f.write(await ehr_file.read())
        ehr_path = file_location

    patients.insert_one({
        "patient_id": patient_id,
        "name": name,
        "dob": dob,
        "age": age,
        "gender": gender,
        "condition": condition,
        "symptoms": all_symptoms,
        "bp": bp,
        "hr": hr,
        "temp": temp,
        "ehr_file": ehr_path,
        "risk": None,
        "department": None,
        "confidence": None,
        "timestamp": datetime.now()
    })

    return RedirectResponse("/dashboard", status_code=303)


# ===============================
# Safe Condition Encoder
# ===============================
def safe_encode_condition(condition):
    known_conditions = list(le_condition.classes_)
    if condition in known_conditions:
        return le_condition.transform([condition])[0]
    return le_condition.transform([known_conditions[0]])[0]


# ===============================
# Analyze Patient
# ===============================
@app.get("/analyze/{patient_id}")
async def analyze_patient(request: Request, patient_id: str):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)

    patient = patients.find_one({"patient_id": patient_id})
    if not patient:
        return HTMLResponse("Patient not found", status_code=404)

    age = patient["age"]
    gender = patient["gender"]
    condition = patient["condition"]
    bp = patient["bp"]
    hr = patient["hr"]
    temp = patient["temp"]

    gender_encoded = le_gender.transform([gender])[0]
    condition_encoded = safe_encode_condition(condition)

    input_df = pd.DataFrame(
        [[age, gender_encoded, bp, hr, temp, condition_encoded]],
        columns=["Age", "Gender", "BloodPressure", "HeartRate", "Temperature", "Condition"]
    )

    ml_prediction = model.predict(input_df)
    ml_risk = le_risk.inverse_transform(ml_prediction)[0]

    probabilities = model.predict_proba(input_df)[0]
    confidence = float(round(max(probabilities) * 100, 2))

    rule_risk = rule_based_risk(bp, hr, temp)

    if rule_risk == "High" or ml_risk == "High":
        final_risk = "High"
    elif rule_risk == "Medium" or ml_risk == "Medium":
        final_risk = "Medium"
    else:
        final_risk = "Low"

    department = recommend_department(bp, hr)

    patients.update_one(
        {"patient_id": patient_id},
        {"$set": {
            "risk": final_risk,
            "department": department,
            "confidence": confidence
        }}
    )

    return RedirectResponse("/dashboard", status_code=303)


# ===============================
# Patient Detail Page (FIXED)
# ===============================
@app.get("/patient/{patient_id}", response_class=HTMLResponse)
async def patient_detail(request: Request, patient_id: str):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)

    patient = patients.find_one({"patient_id": patient_id})
    if not patient:
        return HTMLResponse("Patient not found", status_code=404)

    return templates.TemplateResponse("patient_detail.html", {
        "request": request,
        "patient": patient
    })


# ===============================
# PDF Report (FIXED)
# ===============================
@app.get("/patient/{patient_id}/pdf")
async def patient_pdf(request: Request, patient_id: str):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)

    patient = patients.find_one({"patient_id": patient_id})
    if not patient:
        return HTMLResponse("Patient not found", status_code=404)

    file_path = f"{patient_id}_report.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("MedTriage AI – Patient Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    info = [
        f"Patient ID: {patient['patient_id']}",
        f"Name: {patient['name']}",
        f"Age: {patient['age']}",
        f"Gender: {patient['gender']}",
        f"Condition: {patient['condition']}",
        f"Symptoms: {patient.get('symptoms','—')}",
        f"Blood Pressure: {patient['bp']}",
        f"Heart Rate: {patient['hr']}",
        f"Temperature: {round(patient['temp'],2)}",
        f"Risk Level: {patient.get('risk','Not analyzed')}",
        f"Department: {patient.get('department','-')}",
        f"Confidence: {patient.get('confidence','-')}%"
    ]

    for line in info:
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 4))

    doc.build(elements)

    return FileResponse(file_path, filename=file_path, media_type="application/pdf")


# ===============================
# CSV Export
# ===============================
@app.get("/download_csv")
async def download_csv(request: Request):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)

    patient_list = list(patients.find({}, {"_id": 0}))

    if not patient_list:
        return HTMLResponse("No patient data available", status_code=404)

    df = pd.DataFrame(patient_list)
    file_path = "patients.csv"
    df.to_csv(file_path, index=False)

    return FileResponse(file_path, filename="patients.csv", media_type="text/csv")


# ===============================
# Dashboard (Protected)
# ===============================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("doctor"):
        return RedirectResponse("/", status_code=303)

    patient_list = list(patients.find())

    total_patients = len(patient_list)
    high_count = sum(1 for p in patient_list if p.get("risk") == "High")
    medium_count = sum(1 for p in patient_list if p.get("risk") == "Medium")
    low_count = sum(1 for p in patient_list if p.get("risk") == "Low")

    department_counts = {}
    for p in patient_list:
        dept = p.get("department") or "Unassigned"
        department_counts[dept] = department_counts.get(dept, 0) + 1

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "patients": patient_list,
        "total": total_patients,
        "high": high_count,
        "medium": medium_count,
        "low": low_count,
        "department_counts": department_counts
    })

