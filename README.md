MedTriage AI – Smart Patient Triage System

MedTriage AI is an intelligent hospital triage system that analyzes patient vitals, symptoms, and conditions to predict risk level and recommend the appropriate medical department.

The system helps hospitals prioritize patients and make faster clinical decisions.

🚀 Live Deployment

🌐 Website:
https://call-coders.up.railway.app/dashboard

🔐 Demo Login Credentials
Doctor Login

Username: doctor
Password: 1234
(Use these credentials to access the dashboard.)

🎯 Project Objective

To build an AI-powered system that:

Analyzes patient vitals and symptoms

Predicts risk level (Low, Medium, High)

Recommends the appropriate hospital department

Provides clinical interpretation and actions

Supports voice-based AI explanation

🧠 Key Features
AI Risk Prediction

Uses a trained machine learning model

Predicts patient risk level based on:

Age

Gender

Symptoms

Blood Pressure

Heart Rate

Temperature

Department Recommendation

Automatically suggests:

Emergency

Cardiology

Neurology

General Medicine

Orthopedics

Other departments

Smart Clinical Recommendations

Provides:

Clinical interpretation

Condition-specific actions

Priority level

Voice AI Explanation

AI explains patient condition using voice

Gives recommendations and next steps

Dashboard

View all patients

Add new patients

Analyze patient condition

Download patient report as PDF

🏗️ System Architecture
Frontend

HTML

Tailwind CSS

JavaScript

Chart.js (for vitals graph)

Web Speech API (voice AI)

Backend

Python

FastAPI

Jinja2 templates

Machine Learning

Scikit-learn

XGBoost

Joblib for model loading

Database

In-memory / file-based patient storage

Deployment

Railway Cloud Platform

Uvicorn ASGI server

📂 Project Structure
backend/
   main.py
   database.py
   rule_engine.py
   utils.py

templates/
   dashboard.html
   patient_detail.html
   login.html


⚙️ Installation (Local Setup)

Clone the repository

git clone https://github.com/loki353/kanini.git
cd kanini


Install dependencies

pip install -r requirements.txt


Run the server

uvicorn backend.main:app --reload


Open in browser

http://127.0.0.1:8000/dashboard

🧪 Technologies Used
Category	Tools
Backend	FastAPI, Python
Frontend	HTML, Tailwind CSS, JS
ML Model	Scikit-learn, XGBoost
Visualization	Chart.js
Voice AI	Web Speech API
Deployment	Railway
Server	Uvicorn

📊 AI Output Example

Risk Level: High

Department: Emergency

Confidence: 97%

Clinical Interpretation: Critical vitals detected

Recommended Actions: Immediate intervention

👨‍💻 Team

Team Name: Call Coders
Team Lead: B Lokesh,
Team Members :P Lalith Krishna;
              G Adhokshaja 
              M Chethan
Project: MedTriage AI
