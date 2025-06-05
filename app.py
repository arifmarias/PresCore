import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import json
import datetime
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import qrcode
from PIL import Image
import io
import requests
import time
import re

# Page configuration
st.set_page_config(
    page_title="MedScript Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional medical theme
st.markdown("""
<style>
:root {
    --primary-blue: #0096C7;
    --light-blue: #48CAE4;
    --success-green: #28A745;
    --warning-orange: #FFC107;
    --error-red: #DC3545;
    --form-bg: #0c2733;
}

.main-header {
    background: linear-gradient(90deg, var(--primary-blue), var(--light-blue));
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.patient-completed {
    background: #e8f5e8;
    border-left: 4px solid #4caf50;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.patient-waiting {
    background: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.stForm {
    background: var(--form-bg);
    padding: 2rem;
    border-radius: 10px;
    border: 1px solid #ddd;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid var(--primary-blue);
}

.success-message {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #c3e6cb;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
}

.prescription-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    border-left: 4px solid var(--primary-blue);
}

.ai-analysis {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Database setup and management
class DatabaseManager:
    def __init__(self):
        self.db_name = "medscript_pro.db"
        self.init_database()
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                medical_license TEXT,
                specialization TEXT,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )""",
            
            """CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                allergies TEXT,
                medical_conditions TEXT,
                emergency_contact TEXT,
                insurance_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )""",
            
            """CREATE TABLE IF NOT EXISTS patient_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_date DATE NOT NULL,
                visit_type TEXT NOT NULL,
                current_problems TEXT,
                is_followup BOOLEAN DEFAULT 0,
                is_report_consultation BOOLEAN DEFAULT 0,
                vital_signs TEXT,
                notes TEXT,
                created_by INTEGER NOT NULL,
                consultation_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                generic_name TEXT,
                brand_names TEXT,
                drug_class TEXT,
                dosage_forms TEXT,
                strengths TEXT,
                indications TEXT,
                contraindications TEXT,
                side_effects TEXT,
                interactions TEXT,
                is_controlled BOOLEAN DEFAULT 0,
                is_favorite BOOLEAN DEFAULT 0,
                created_by INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS lab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_category TEXT NOT NULL,
                normal_range TEXT,
                units TEXT,
                description TEXT,
                preparation_required TEXT,
                created_by INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT UNIQUE NOT NULL,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                visit_id INTEGER,
                diagnosis TEXT,
                notes TEXT,
                status TEXT DEFAULT 'active',
                ai_interaction_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users (id),
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (visit_id) REFERENCES patient_visits (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS prescription_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL,
                medication_id INTEGER NOT NULL,
                dosage TEXT NOT NULL,
                frequency TEXT NOT NULL,
                duration TEXT NOT NULL,
                quantity TEXT,
                refills INTEGER DEFAULT 0,
                instructions TEXT,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
                FOREIGN KEY (medication_id) REFERENCES medications (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS prescription_lab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL,
                lab_test_id INTEGER NOT NULL,
                instructions TEXT,
                urgency TEXT DEFAULT 'routine',
                FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
                FOREIGN KEY (lab_test_id) REFERENCES lab_tests (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                template_data TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )"""
        ]
        
        for table in tables:
            cursor.execute(table)
        
        conn.commit()
        self.populate_sample_data()
        conn.close()
    
    def populate_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Create users
        users = [
            ('superadmin', self.hash_password('admin123'), 'System Administrator', 'super_admin', None, None, 'admin@medscript.com', '555-0001'),
            ('doctor1', self.hash_password('doctor123'), 'Dr. Sarah Johnson', 'doctor', 'MD-12345', 'Internal Medicine', 'sarah.johnson@medscript.com', '555-0002'),
            ('assistant1', self.hash_password('assistant123'), 'Mike Chen', 'assistant', None, None, 'mike.chen@medscript.com', '555-0003')
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, password_hash, full_name, user_type, medical_license, specialization, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, users)
        
        # Create patients
        patients = [
            ('PT-20250602-001234', 'John', 'Smith', '1980-05-15', 'Male', '555-1001', 'john.smith@email.com', '123 Main St, City, State', 'Penicillin', 'Hypertension, Diabetes Type 2', 'Jane Smith - 555-1002', 'Blue Cross Blue Shield'),
            ('PT-20250602-001235', 'Emily', 'Davis', '1992-08-22', 'Female', '555-1003', 'emily.davis@email.com', '456 Oak Ave, City, State', 'None known', 'Asthma', 'Robert Davis - 555-1004', 'Aetna Health'),
            ('PT-20250602-001236', 'Robert', 'Wilson', '1975-12-03', 'Male', '555-1005', 'robert.wilson@email.com', '789 Pine St, City, State', 'Sulfa drugs', 'None', 'Mary Wilson - 555-1006', 'Medicare')
        ]
        
        cursor.executemany("""
            INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, gender, phone, email, address, allergies, medical_conditions, emergency_contact, insurance_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, patients)
        
        # Create today's visits
        today = datetime.date.today().isoformat()
        visits = [
            (1, today, 'Consultation', 'Chest pain, shortness of breath', 0, 0, 'BP: 140/90, HR: 88, Temp: 98.6°F', 'Patient reports chest discomfort for 2 days', 3, 0),
            (2, today, 'Follow-up', 'Asthma control check', 1, 0, 'BP: 120/80, HR: 72, Peak Flow: 450L/min', 'Regular asthma follow-up', 3, 0),
            (3, today, 'Report Consultation', 'Lab results review', 0, 1, 'BP: 130/85, HR: 76', 'Reviewing recent blood work', 3, 0)
        ]
        
        cursor.executemany("""
            INSERT INTO patient_visits (patient_id, visit_date, visit_type, current_problems, is_followup, is_report_consultation, vital_signs, notes, created_by, consultation_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, visits)
        
        # Populate medications
        medications = [
            ('Lisinopril', 'Lisinopril', 'Prinivil, Zestril', 'ACE Inhibitor', 'Tablet', '5mg, 10mg, 20mg', 'Hypertension, Heart failure', 'Pregnancy, Angioedema history', 'Dry cough, Dizziness', 'Potassium supplements, Diuretics', 0),
            ('Metformin', 'Metformin', 'Glucophage', 'Biguanide', 'Tablet, Extended-release', '500mg, 850mg, 1000mg', 'Type 2 Diabetes', 'Kidney disease, Metabolic acidosis', 'GI upset, Lactic acidosis (rare)', 'Contrast dyes, Alcohol', 0),
            ('Albuterol', 'Albuterol sulfate', 'ProAir, Ventolin', 'Beta-2 agonist', 'Inhaler, Nebulizer', '90mcg/puff, 2.5mg/3ml', 'Asthma, COPD', 'Hypersensitivity', 'Tremor, Palpitations', 'Beta blockers', 0),
            ('Atorvastatin', 'Atorvastatin', 'Lipitor', 'HMG-CoA reductase inhibitor', 'Tablet', '10mg, 20mg, 40mg, 80mg', 'High cholesterol', 'Active liver disease, Pregnancy', 'Muscle pain, Liver enzyme elevation', 'Cyclosporine, Gemfibrozil', 0),
            ('Omeprazole', 'Omeprazole', 'Prilosec', 'Proton pump inhibitor', 'Capsule, Tablet', '20mg, 40mg', 'GERD, Peptic ulcer', 'Hypersensitivity', 'Headache, Diarrhea', 'Clopidogrel, Warfarin', 0),
            ('Amlodipine', 'Amlodipine', 'Norvasc', 'Calcium channel blocker', 'Tablet', '2.5mg, 5mg, 10mg', 'Hypertension, Angina', 'Severe aortic stenosis', 'Peripheral edema, Dizziness', 'Simvastatin (high dose)', 0),
            ('Levothyroxine', 'Levothyroxine', 'Synthroid', 'Thyroid hormone', 'Tablet', '25mcg, 50mcg, 75mcg, 100mcg', 'Hypothyroidism', 'Hyperthyroidism, MI', 'Palpitations, Weight loss', 'Iron, Calcium', 0),
            ('Hydrochlorothiazide', 'Hydrochlorothiazide', 'Microzide', 'Thiazide diuretic', 'Tablet', '12.5mg, 25mg', 'Hypertension, Edema', 'Anuria, Sulfa allergy', 'Hypokalemia, Hyperuricemia', 'Lithium, Digoxin', 0),
            ('Simvastatin', 'Simvastatin', 'Zocor', 'HMG-CoA reductase inhibitor', 'Tablet', '5mg, 10mg, 20mg, 40mg', 'High cholesterol', 'Active liver disease', 'Muscle pain, Liver toxicity', 'Amiodarone, Verapamil', 0),
            ('Warfarin', 'Warfarin', 'Coumadin', 'Anticoagulant', 'Tablet', '1mg, 2mg, 5mg, 10mg', 'Atrial fibrillation, DVT', 'Bleeding disorders, Pregnancy', 'Bleeding, Bruising', 'Aspirin, Antibiotics', 0)
        ]
        
        cursor.executemany("""
            INSERT INTO medications (name, generic_name, brand_names, drug_class, dosage_forms, strengths, indications, contraindications, side_effects, interactions, is_controlled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, medications)
        
        # Populate lab tests
        lab_tests = [
            ('Complete Blood Count', 'Hematology', 'WBC: 4.5-11.0 K/uL, RBC: 4.2-5.4 M/uL', 'K/uL, M/uL', 'Complete blood cell analysis', 'None required'),
            ('Basic Metabolic Panel', 'Chemistry', 'Glucose: 70-100 mg/dL, Na: 136-145 mEq/L', 'mg/dL, mEq/L', 'Basic chemistry panel', 'Fasting 8-12 hours'),
            ('Lipid Panel', 'Chemistry', 'Total Chol: <200 mg/dL, LDL: <100 mg/dL', 'mg/dL', 'Cholesterol and triglycerides', 'Fasting 9-12 hours'),
            ('Thyroid Function Tests', 'Endocrinology', 'TSH: 0.4-4.0 mIU/L, Free T4: 0.8-1.8 ng/dL', 'mIU/L, ng/dL', 'Thyroid hormone levels', 'None required'),
            ('Hemoglobin A1C', 'Endocrinology', '<5.7% (Normal), 5.7-6.4% (Prediabetes)', '%', 'Average blood glucose 2-3 months', 'None required'),
            ('Liver Function Tests', 'Chemistry', 'ALT: 7-56 U/L, AST: 10-40 U/L', 'U/L', 'Liver enzyme assessment', 'None required'),
            ('Kidney Function Tests', 'Chemistry', 'BUN: 7-20 mg/dL, Creatinine: 0.6-1.2 mg/dL', 'mg/dL', 'Kidney function assessment', 'None required'),
            ('Urinalysis', 'Urology', 'Specific gravity: 1.005-1.030', 'Various', 'Urine analysis', 'Clean catch specimen'),
            ('Chest X-Ray', 'Radiology', 'Normal cardiac and pulmonary findings', 'Visual', 'Chest imaging', 'Remove metal objects'),
            ('ECG/EKG', 'Cardiology', 'Normal sinus rhythm', 'Visual', 'Heart rhythm analysis', 'None required')
        ]
        
        cursor.executemany("""
            INSERT INTO lab_tests (test_name, test_category, normal_range, units, description, preparation_required)
            VALUES (?, ?, ?, ?, ?, ?)
        """, lab_tests)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

# Authentication and session management
class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def authenticate_user(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.db.hash_password(password)
        cursor.execute("""
            SELECT id, username, full_name, user_type, medical_license, specialization
            FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        """, (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[2],
                'user_type': user[3],
                'medical_license': user[4],
                'specialization': user[5]
            }
        return None
    
    def logout(self):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

# AI Integration for drug interactions
class AIAnalyzer:
    def __init__(self):
        # Try to get API key from secrets, fallback to None for graceful degradation
        try:
            self.api_key = st.secrets.get("openrouter_api_key", None)
        except:
            self.api_key = None
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def analyze_drug_interactions(self, medications, patient_info):
        if not self.api_key:
            return self._fallback_analysis(medications, patient_info)
        
        try:
            # Prepare the prompt
            medication_list = [f"- {med['name']} ({med['dosage']}, {med['frequency']})" for med in medications]
            
            prompt = f"""
            Analyze drug interactions for the following prescription:
            
            Patient Information:
            - Age: {patient_info.get('age', 'Unknown')}
            - Gender: {patient_info.get('gender', 'Unknown')}
            - Allergies: {patient_info.get('allergies', 'None known')}
            - Medical Conditions: {patient_info.get('medical_conditions', 'None')}
            
            Medications:
            {chr(10).join(medication_list)}
            
            Please provide a comprehensive analysis in JSON format with the following structure:
            {{
                "interactions": [
                    {{"drugs": ["drug1", "drug2"], "severity": "major|moderate|minor", "description": "...", "recommendation": "..."}}
                ],
                "allergies": [
                    {{"drug": "drug_name", "allergy": "allergy_type", "risk": "description"}}
                ],
                "contraindications": [
                    {{"drug": "drug_name", "condition": "medical_condition", "risk": "description"}}
                ],
                "alternatives": [
                    {{"instead_of": "drug_name", "suggested": "alternative_drug", "reason": "..."}}
                ],
                "monitoring": [
                    {{"parameter": "what_to_monitor", "frequency": "how_often", "reason": "..."}}
                ],
                "overall_risk": "low|moderate|high",
                "summary": "Brief overall assessment"
            }}
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.1
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract JSON from the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_content = content[json_start:json_end]
                    return json.loads(json_content)
            
            return self._fallback_analysis(medications, patient_info)
            
        except Exception as e:
            st.warning(f"AI analysis unavailable: {str(e)}. Using basic interaction checking.")
            return self._fallback_analysis(medications, patient_info)
    
    def _fallback_analysis(self, medications, patient_info):
        """Basic fallback analysis when AI is unavailable"""
        interactions = []
        contraindications = []
        monitoring = []
        
        # Basic interaction rules
        med_names = [med['name'].lower() for med in medications]
        
        # Common interaction patterns
        if 'warfarin' in med_names and any('aspirin' in name or 'ibuprofen' in name for name in med_names):
            interactions.append({
                "drugs": ["Warfarin", "Aspirin/NSAIDs"],
                "severity": "major",
                "description": "Increased bleeding risk",
                "recommendation": "Monitor INR closely, consider gastroprotection"
            })
        
        if 'lisinopril' in med_names and 'potassium' in str(medications).lower():
            interactions.append({
                "drugs": ["Lisinopril", "Potassium"],
                "severity": "moderate",
                "description": "Risk of hyperkalemia",
                "recommendation": "Monitor potassium levels"
            })
        
        # Check allergies
        allergies = []
        patient_allergies = patient_info.get('allergies', '').lower()
        if 'penicillin' in patient_allergies:
            for med in medications:
                if 'penicillin' in med['name'].lower() or 'amoxicillin' in med['name'].lower():
                    allergies.append({
                        "drug": med['name'],
                        "allergy": "Penicillin",
                        "risk": "Allergic reaction possible"
                    })
        
        return {
            "interactions": interactions,
            "allergies": allergies,
            "contraindications": contraindications,
            "alternatives": [],
            "monitoring": monitoring,
            "overall_risk": "low" if not interactions and not allergies else "moderate",
            "summary": f"Basic analysis completed. Found {len(interactions)} interactions and {len(allergies)} allergy concerns."
        }

# PDF Generation
class PDFGenerator:
    def generate_prescription_pdf(self, prescription_data):
        # Import the enums inside the method to avoid import issues
        from fpdf.enums import XPos, YPos
        
        pdf = FPDF()
        pdf.add_page()
        
        # Use Helvetica instead of Arial to avoid deprecation warnings
        pdf.set_font('Helvetica', 'B', 16)
        
        # Header
        pdf.cell(0, 10, 'MEDICAL PRESCRIPTION', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)
        
        # Doctor information
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, f"Dr. {prescription_data['doctor_name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, f"Specialization: {prescription_data['specialization']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"License: {prescription_data['medical_license']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        
        # Prescription details
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, f"Prescription ID: {prescription_data['prescription_id']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Date: {prescription_data['date']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        
        # Patient information
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'PATIENT INFORMATION', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, f"Name: {prescription_data['patient_name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"Patient ID: {prescription_data['patient_id']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 6, f"DOB: {prescription_data['dob']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        
        # Diagnosis
        if prescription_data.get('diagnosis'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'DIAGNOSIS', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 6, prescription_data['diagnosis'])
            pdf.ln(3)
        
        # Medications
        if prescription_data.get('medications'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'MEDICATIONS', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 10)
            
            for i, med in enumerate(prescription_data['medications'], 1):
                pdf.cell(0, 6, f"{i}. {med['name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(10, 6, '', new_x=XPos.RIGHT, new_y=YPos.TOP)  # Indent
                pdf.cell(0, 6, f"   Dosage: {med['dosage']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(10, 6, '', new_x=XPos.RIGHT, new_y=YPos.TOP)  # Indent
                pdf.cell(0, 6, f"   Frequency: {med['frequency']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(10, 6, '', new_x=XPos.RIGHT, new_y=YPos.TOP)  # Indent
                pdf.cell(0, 6, f"   Duration: {med['duration']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if med.get('instructions'):
                    pdf.cell(10, 6, '', new_x=XPos.RIGHT, new_y=YPos.TOP)  # Indent
                    pdf.multi_cell(0, 6, f"   Instructions: {med['instructions']}")
                pdf.ln(2)
        
        # Lab tests
        if prescription_data.get('lab_tests'):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'RECOMMENDED LAB TESTS', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 10)
            
            for i, test in enumerate(prescription_data['lab_tests'], 1):
                pdf.cell(0, 6, f"{i}. {test['name']} ({test['urgency']})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if test.get('instructions'):
                    pdf.cell(10, 6, '', new_x=XPos.RIGHT, new_y=YPos.TOP)  # Indent
                    pdf.multi_cell(0, 6, f"   Instructions: {test['instructions']}")
        
        # Notes
        if prescription_data.get('notes'):
            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 8, 'NOTES', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 6, prescription_data['notes'])
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Helvetica', '', 8)
        pdf.cell(0, 6, f"Generated by MedScript Pro on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Get the PDF output and ensure it's bytes
        pdf_output = pdf.output()
        
        # Convert bytearray to bytes if necessary
        if isinstance(pdf_output, bytearray):
            return bytes(pdf_output)
        else:
            return pdf_output

# Initialize managers
@st.cache_resource
def get_managers():
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    ai_analyzer = AIAnalyzer()
    pdf_generator = PDFGenerator()
    return db_manager, auth_manager, ai_analyzer, pdf_generator

db_manager, auth_manager, ai_analyzer, pdf_generator = get_managers()

# Helper functions
def log_activity(user_id, action_type, entity_type=None, entity_id=None, metadata=None):
    """Log user activity for analytics"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analytics (user_id, action_type, entity_type, entity_id, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, action_type, entity_type, entity_id, json.dumps(metadata) if metadata else None))
    
    conn.commit()
    conn.close()

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = datetime.date.today()
    birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def generate_patient_id():
    """Generate unique patient ID"""
    today = datetime.date.today().strftime('%Y%m%d')
    import random
    random_num = random.randint(100000, 999999)
    return f"PT-{today}-{random_num:06d}"

def generate_prescription_id():
    """Generate unique prescription ID"""
    today = datetime.date.today().strftime('%Y%m%d')
    import random
    random_num = random.randint(1000, 9999)
    return f"RX-{today}-{random_num:04d}"

def display_ai_analysis(analysis_result):
    if not analysis_result or not isinstance(analysis_result, dict):
        st.info("No AI analysis data to display or data is not in the expected format.")
        return

    st.markdown("<div class='ai-analysis'>", unsafe_allow_html=True)
    st.subheader("🔍 AI Drug Interaction Analysis Results")

    # Overall Risk and Summary
    overall_risk = analysis_result.get('overall_risk', 'N/A').capitalize()
    summary = analysis_result.get('summary', 'No summary provided.')

    risk_color_map = {"Low": "green", "Moderate": "orange", "High": "red"}
    risk_color = risk_color_map.get(overall_risk, "normal") # default to normal if risk level unknown

    st.markdown(f"**Overall Risk:** <span style='color:{risk_color}; font-weight:bold;'>{overall_risk}</span>", unsafe_allow_html=True)
    st.markdown(f"**Summary:** {summary}")
    st.markdown("---")

    # Interactions
    interactions = analysis_result.get('interactions', [])
    if interactions:
        st.markdown("#### 💊 Drug Interactions:")
        for item in interactions:
            drugs = ", ".join(item.get('drugs', ['N/A']))
            severity = item.get('severity', 'N/A').capitalize()
            description = item.get('description', 'N/A')
            recommendation = item.get('recommendation', 'N/A')

            exp_title = f"Interaction: {drugs} (Severity: {severity})"
            with st.expander(exp_title):
                st.markdown(f"- **Drugs Involved:** {drugs}")
                st.markdown(f"- **Severity:** {severity}")
                st.markdown(f"- **Description:** {description}")
                st.markdown(f"- **Recommendation:** {recommendation}")
        st.markdown("---")

    # Allergies
    allergies = analysis_result.get('allergies', [])
    if allergies:
        st.markdown("#### ⚠️ Allergy Concerns:")
        for item in allergies:
            drug = item.get('drug', 'N/A')
            allergy_type = item.get('allergy', 'N/A')
            risk = item.get('risk', 'N/A')
            with st.expander(f"Allergy: {drug} with {allergy_type}"):
                st.markdown(f"- **Drug:** {drug}")
                st.markdown(f"- **Patient Allergy:** {allergy_type}")
                st.markdown(f"- **Risk/Note:** {risk}")
        st.markdown("---")

    # Contraindications
    contraindications = analysis_result.get('contraindications', [])
    if contraindications:
        st.markdown("#### ⛔ Contraindications (based on patient conditions):")
        for item in contraindications:
            drug = item.get('drug', 'N/A')
            condition = item.get('condition', 'N/A')
            risk = item.get('risk', 'N/A')
            with st.expander(f"Contraindication: {drug} with {condition}"):
                st.markdown(f"- **Drug:** {drug}")
                st.markdown(f"- **Patient Condition:** {condition}")
                st.markdown(f"- **Risk/Note:** {risk}")
        st.markdown("---")

    # Alternatives
    alternatives = analysis_result.get('alternatives', [])
    if alternatives:
        st.markdown("#### 🔄 Suggested Alternatives:")
        for item in alternatives:
            instead_of = item.get('instead_of', 'N/A')
            suggested = item.get('suggested', 'N/A')
            reason = item.get('reason', 'N/A')
            with st.expander(f"Alternative for {instead_of}: Suggest {suggested}"):
                st.markdown(f"- **Original Drug:** {instead_of}")
                st.markdown(f"- **Suggested Alternative:** {suggested}")
                st.markdown(f"- **Reason:** {reason}")
        st.markdown("---")

    # Monitoring
    monitoring = analysis_result.get('monitoring', [])
    if monitoring:
        st.markdown("#### 🔬 Recommended Monitoring:")
        for item in monitoring:
            parameter = item.get('parameter', 'N/A')
            frequency = item.get('frequency', 'N/A')
            reason = item.get('reason', 'N/A')
            with st.expander(f"Monitor: {parameter} ({frequency})"):
                st.markdown(f"- **Parameter to Monitor:** {parameter}")
                st.markdown(f"- **Frequency:** {frequency}")
                st.markdown(f"- **Reason:** {reason}")

    st.markdown("</div>", unsafe_allow_html=True)

# Authentication UI
def show_login():
    st.markdown('<div class="main-header"><h1>🏥 MedScript Pro</h1><p>Medical Prescription Management System</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Please Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                user = auth_manager.authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    log_activity(user['id'], 'login')
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.markdown("- Super Admin: `superadmin` / `admin123`")
        st.markdown("- Doctor: `doctor1` / `doctor123`")
        st.markdown("- Assistant: `assistant1` / `assistant123`")

# Navigation and sidebar
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user['full_name']}")
        st.markdown(f"**Role:** {st.session_state.user['user_type'].replace('_', ' ').title()}")
        
        st.markdown("---")
        
        # Navigation based on user role
        user_type = st.session_state.user['user_type']
        
        if user_type == 'super_admin':
            pages = {
                "Dashboard": "dashboard",
                "User Management": "users",
                "Patient Management": "patients", 
                "Medication Database": "medications",
                "Lab Tests Database": "lab_tests",
                "Analytics": "analytics"
            }
        elif user_type == 'doctor':
            pages = {
                "Today's Patients": "todays_patients",
                "Create Prescription": "create_prescription",
                "Patient Management": "patients",
                "Medication Database": "medications",
                "Lab Tests Database": "lab_tests",
                "Templates": "templates",
                "Analytics": "analytics"
            }
        else:  # assistant
            pages = {
                "Patient Management": "patients",
                "Visit Registration": "visit_registration",
                "Medication Database": "medications",
                "Lab Tests Database": "lab_tests",
                "My Analytics": "analytics"
            }
        
        # selected_page = st.radio("Navigation", list(pages.keys()))
        # st.session_state.current_page = pages[selected_page]
        #-----
        # Find the current page index for the radio button
        current_page_key = st.session_state.current_page
        current_page_name = None
        for page_name, page_key in pages.items():
            if page_key == current_page_key:
                current_page_name = page_name
                break

        # If current page is not found, default to first page
        if current_page_name is None:
            current_page_name = list(pages.keys())[0]
            st.session_state.current_page = pages[current_page_name]

        # Get the index of current page for radio button
        current_index = list(pages.keys()).index(current_page_name)

        # Show radio buttons with current selection
        selected_page = st.radio("Navigation", list(pages.keys()), index=current_index)

        # Only update current_page if user actually selected something different
        if pages[selected_page] != st.session_state.current_page:
            st.session_state.current_page = pages[selected_page]
            # Clear selected patient when navigating away from prescription page
            if st.session_state.current_page != 'create_prescription' and 'selected_patient' in st.session_state:
                del st.session_state.selected_patient
            st.rerun()
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            log_activity(st.session_state.user['id'], 'logout')
            auth_manager.logout()
            st.rerun()

# Dashboard for Super Admin
def show_dashboard():
    st.markdown('<div class="main-header"><h1>📊 System Dashboard</h1></div>', unsafe_allow_html=True)
    
    conn = db_manager.get_connection()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users_count = pd.read_sql("SELECT COUNT(*) as count FROM users WHERE is_active = 1", conn).iloc[0]['count']
        st.metric("Active Users", users_count)
    
    with col2:
        patients_count = pd.read_sql("SELECT COUNT(*) as count FROM patients WHERE is_active = 1", conn).iloc[0]['count']
        st.metric("Total Patients", patients_count)
    
    with col3:
        prescriptions_count = pd.read_sql("SELECT COUNT(*) as count FROM prescriptions", conn).iloc[0]['count']
        st.metric("Total Prescriptions", prescriptions_count)
    
    with col4:
        today_visits = pd.read_sql("SELECT COUNT(*) as count FROM patient_visits WHERE visit_date = date('now')", conn).iloc[0]['count']
        st.metric("Today's Visits", today_visits)
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Prescriptions")
        recent_prescriptions = pd.read_sql("""
            SELECT p.prescription_id, u.full_name as doctor, pt.first_name || ' ' || pt.last_name as patient, 
                   p.created_at
            FROM prescriptions p
            JOIN users u ON p.doctor_id = u.id
            JOIN patients pt ON p.patient_id = pt.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """, conn)
        
        if not recent_prescriptions.empty:
            st.dataframe(recent_prescriptions, use_container_width=True)
        else:
            st.info("No prescriptions yet")
    
    with col2:
        st.subheader("Today's Visits")
        todays_visits = pd.read_sql("""
            SELECT pt.first_name || ' ' || pt.last_name as patient, 
                   v.visit_type, v.current_problems, v.consultation_completed
            FROM patient_visits v
            JOIN patients pt ON v.patient_id = pt.id
            WHERE v.visit_date = date('now')
            ORDER BY v.created_at DESC
        """, conn)
        
        if not todays_visits.empty:
            st.dataframe(todays_visits, use_container_width=True)
        else:
            st.info("No visits scheduled for today")
    
    conn.close()

# User Management (Super Admin)
def show_user_management():
    st.markdown('<div class="main-header"><h1>👥 User Management</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View Users", "Add User"])
    
    with tab1:
        st.subheader("View and Manage Users")
        conn = db_manager.get_connection()
        users_df = pd.read_sql("""
            SELECT id, username, full_name, user_type, medical_license, specialization, 
                   email, phone, created_at, DATETIME(created_at, '+5 hours', '+30 minutes') as created_at_ist, is_active
            FROM users
            ORDER BY created_at DESC
        """, conn)
        conn.close()

        if not users_df.empty:
            # Search and filter
            col_search, col_filter_role, col_filter_status = st.columns([2,1,1])
            with col_search:
                search_term = st.text_input("Search users (name, username, email)...", key="user_search")
            with col_filter_role:
                user_type_filter = st.selectbox("Filter by role", ["All", "super_admin", "doctor", "assistant"], key="user_role_filter")
            with col_filter_status:
                status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive"], key="user_status_filter")

            # Apply filters
            filtered_df = users_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['full_name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['username'].str.contains(search_term, case=False, na=False) |
                    filtered_df['email'].str.contains(search_term, case=False, na=False)
                ]
            
            if user_type_filter != "All":
                filtered_df = filtered_df[filtered_df['user_type'] == user_type_filter]

            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['is_active'] == 1]
            elif status_filter == "Inactive":
                filtered_df = filtered_df[filtered_df['is_active'] == 0]

            # Display users with action buttons
            for index, row in filtered_df.iterrows():
                st.markdown("---")
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{row['full_name']}** ({row['username']})")
                    st.caption(f"ID: {row['id']} | Role: {row['user_type'].replace('_', ' ').title()} | Email: {row['email']}")
                    st.caption(f"Phone: {row['phone']} | License: {row['medical_license']} | Specialization: {row['specialization']}")
                    status_text = "Active" if row['is_active'] else "Inactive"
                    status_color = "green" if row['is_active'] else "red"
                    st.caption(f"Status: <span style='color:{status_color};'>{status_text}</span> | Created: {row['created_at_ist']}", unsafe_allow_html=True)

                with col2:
                    if st.button("Edit", key=f"edit_user_{row['id']}", use_container_width=True):
                        st.session_state.edit_user_id = row['id']
                        # This will trigger the edit form to show below or in a modal/expander

                with col3:
                    # Prevent super_admin from deleting themselves
                    if st.session_state.user['id'] == row['id'] and row['user_type'] == 'super_admin':
                        st.button("Delete", key=f"delete_user_{row['id']}", disabled=True, use_container_width=True, help="Super Admins cannot delete their own account.")
                    else:
                        if st.button("⚠️ Delete" if row['is_active'] else "✅ Restore", key=f"delete_user_{row['id']}", use_container_width=True):
                            st.session_state.delete_user_id = row['id']
                            st.session_state.action_user_active_status = row['is_active']
                            # This will trigger confirmation and action

            if not filtered_df.empty:
                 st.markdown("---") # Final separator

            # Handle Edit User action
            if 'edit_user_id' in st.session_state and st.session_state.edit_user_id:
                show_edit_user_form(st.session_state.edit_user_id)

            # Handle Delete/Restore User action
            if 'delete_user_id' in st.session_state and st.session_state.delete_user_id:
                confirm_and_delete_user(st.session_state.delete_user_id, st.session_state.action_user_active_status)

        else:
            st.info("No users found")
    
    with tab2:
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*")
                full_name = st.text_input("Full Name*")
                user_type = st.selectbox("User Type*", ["doctor", "assistant", "super_admin"])
                email = st.text_input("Email")
            
            with col2:
                password = st.text_input("Password*", type="password")
                medical_license = st.text_input("Medical License")
                specialization = st.text_input("Specialization")
                phone = st.text_input("Phone")
            
            submit_button = st.form_submit_button("Add User")
            
            if submit_button:
                if username and password and full_name:
                    try:
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        password_hash = db_manager.hash_password(password)
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, full_name, user_type, 
                                             medical_license, specialization, email, phone)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (username, password_hash, full_name, user_type, medical_license, 
                              specialization, email, phone))
                        
                        conn.commit()
                        conn.close()
                        
                        log_activity(st.session_state.user['id'], 'create_user', 'user')
                        st.success("User added successfully!")
                        st.rerun()
                        
                    except sqlite3.IntegrityError:
                        st.error("Username already exists!")
                    except Exception as e:
                        st.error(f"Error adding user: {str(e)}")
                else:
                    st.error("Please fill in all required fields!")

# Patient Management
def show_patient_management():
    st.markdown('<div class="main-header"><h1>👤 Patient Management</h1></div>', unsafe_allow_html=True)
    
    # Role check for edit/delete capabilities
    can_manage_patients = st.session_state.user['user_type'] in ['super_admin', 'doctor']

    tab1, tab2 = st.tabs(["View Patients", "Add Patient"])
    
    # Replace the "View Patients" tab section in show_patient_management() with this:

    with tab1:
        st.subheader("View and Manage Patients")

        # Role check for edit/delete capabilities
        can_manage_patients = st.session_state.user['user_type'] in ['super_admin', 'doctor']

        # Filters: Search, Status
        col_search, col_filter_status = st.columns([2,1])
        with col_search:
            search_term = st.text_input("Search patients (name, ID, email, phone)...", key="patient_search")
        with col_filter_status:
            patient_status_filter = st.selectbox("Filter by status", ["Active", "Inactive", "All"], key="patient_status_filter", index=0)

        # Pagination settings
        items_per_page = 10
        
        # Initialize page number in session state
        if 'patient_page' not in st.session_state:
            st.session_state.patient_page = 1

        # Build query based on status filter
        query = """
            SELECT id, patient_id, first_name, last_name, date_of_birth, gender, phone, email, address,
                allergies, medical_conditions, emergency_contact, insurance_info,
                created_at, DATETIME(created_at, '+5 hours', '+30 minutes') as created_at_ist, is_active
            FROM patients
        """
        params = []

        if patient_status_filter == "Active":
            query += " WHERE is_active = 1"
        elif patient_status_filter == "Inactive":
            query += " WHERE is_active = 0"
        # For "All", no WHERE clause for is_active is added initially

        # Apply search term
        if search_term:
            like_term = f"%{search_term}%"
            search_clause = """
                (first_name LIKE ? OR last_name LIKE ? OR patient_id LIKE ? OR email LIKE ? OR phone LIKE ?)
            """
            if "WHERE" in query:
                query += f" AND {search_clause}"
            else:
                query += f" WHERE {search_clause}"
            params.extend([like_term] * 5)

        query += " ORDER BY created_at DESC"

        conn = db_manager.get_connection()
        patients_df = pd.read_sql(query, conn, params=params)
        conn.close()

        if not patients_df.empty:
            # Calculate pagination
            total_items = len(patients_df)
            total_pages = (total_items - 1) // items_per_page + 1
            
            # Ensure current page is valid
            if st.session_state.patient_page > total_pages:
                st.session_state.patient_page = total_pages
            if st.session_state.patient_page < 1:
                st.session_state.patient_page = 1
            
            # Calculate start and end indices
            start_idx = (st.session_state.patient_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            
            # Get current page items
            current_page_patients = patients_df.iloc[start_idx:end_idx]
            
            # Display only basic info at top
            st.info(f"👤 Showing {start_idx + 1}-{end_idx} of {total_items} patients (Page {st.session_state.patient_page} of {total_pages})")
            
            # Display patients for current page
            for index, patient in current_page_patients.iterrows():
                status_text = "Active" if patient['is_active'] else "Inactive"
                status_emoji = "✅" if patient['is_active'] else "❌"
                expander_title = f"👤 {patient['first_name']} {patient['last_name']} ({patient['patient_id']}) {status_emoji} {status_text}"

                with st.expander(expander_title):
                    if can_manage_patients:
                        col_details, col_actions = st.columns([3,1])
                    else:
                        col_details = st.columns(1)[0]
                        col_actions = None

                    with col_details:
                        st.markdown(f"**Internal ID:** {patient['id']}")
                        st.markdown(f"**DOB:** {patient['date_of_birth']} | **Gender:** {patient['gender']}")
                        st.markdown(f"**Contact:** {patient['phone']} | {patient['email']}")
                        st.markdown(f"**Address:** {patient['address']}")
                        st.markdown(f"**Allergies:** {patient['allergies'] or 'None known'}")
                        st.markdown(f"**Medical Conditions:** {patient['medical_conditions'] or 'None'}")
                        st.markdown(f"**Emergency Contact:** {patient['emergency_contact'] or 'N/A'}")
                        st.markdown(f"**Insurance:** {patient['insurance_info'] or 'N/A'}")
                        st.caption(f"Registered: {patient['created_at_ist']}")

                    if can_manage_patients and col_actions:
                        with col_actions:
                            st.markdown("<br>", unsafe_allow_html=True) # Spacer
                            if st.button("Edit", key=f"edit_patient_{patient['id']}", use_container_width=True):
                                st.session_state.edit_patient_id = patient['id']

                            action_button_text = "⚠️ Deactivate" if patient['is_active'] else "✅ Restore"
                            if st.button(action_button_text, key=f"action_patient_{patient['id']}", use_container_width=True):
                                st.session_state.action_patient_id = patient['id']
                                st.session_state.action_patient_current_status = patient['is_active']
                    
                    # Prescription history button (visible to super_admin and doctor)
                    if st.session_state.user['user_type'] in ['doctor', 'super_admin']:
                        if st.button(f"View Prescription History", key=f"history_{patient['patient_id']}"):
                            st.session_state.show_prescription_history = patient['patient_id']
                            st.rerun()

            # Pagination controls at bottom
            st.markdown("---")
            
            # Main pagination controls
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=(st.session_state.patient_page <= 1), key="pt_prev"):
                    st.session_state.patient_page -= 1
                    st.rerun()
            
            with col2:
                if st.button("Next ➡️", disabled=(st.session_state.patient_page >= total_pages), key="pt_next"):
                    st.session_state.patient_page += 1
                    st.rerun()
            
            with col3:
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {st.session_state.patient_page} of {total_pages}</div>", unsafe_allow_html=True)
            
            with col4:
                # Jump to page
                target_page = st.number_input("Go to page:", min_value=1, max_value=total_pages, 
                                            value=st.session_state.patient_page, key="pt_page_jump")
            
            with col5:
                if st.button("Go", key="pt_go_page"):
                    st.session_state.patient_page = target_page
                    st.rerun()

        else:
            st.info("No patients found matching your criteria.")

        # Handle Edit Patient action
        if 'edit_patient_id' in st.session_state and st.session_state.edit_patient_id:
            show_edit_patient_form(st.session_state.edit_patient_id)

        # Handle Deactivate/Restore Patient action
        if 'action_patient_id' in st.session_state and st.session_state.action_patient_id:
            confirm_and_action_patient(st.session_state.action_patient_id, st.session_state.action_patient_current_status)
    
    with tab2:
        st.subheader("Add New Patient")
        
        with st.form("add_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                date_of_birth = st.date_input("Date of Birth*")
                gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
                phone = st.text_input("Phone")
                email = st.text_input("Email")
            
            with col2:
                address = st.text_area("Address")
                allergies = st.text_area("Known Allergies")
                medical_conditions = st.text_area("Medical Conditions")
                emergency_contact = st.text_input("Emergency Contact")
                insurance_info = st.text_input("Insurance Information")
            
            submit_button = st.form_submit_button("Add Patient")
            
            if submit_button:
                if first_name and last_name and date_of_birth and gender:
                    try:
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        patient_id = generate_patient_id()
                        cursor.execute("""
                            INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, 
                                                gender, phone, email, address, allergies, medical_conditions,
                                                emergency_contact, insurance_info)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (patient_id, first_name, last_name, date_of_birth.isoformat(), gender,
                              phone, email, address, allergies, medical_conditions, emergency_contact, insurance_info))
                        
                        conn.commit()
                        conn.close()
                        
                        log_activity(st.session_state.user['id'], 'create_patient', 'patient')
                        st.success(f"Patient added successfully! Patient ID: {patient_id}")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error adding patient: {str(e)}")
                else:
                    st.error("Please fill in all required fields!")
    if 'show_prescription_history' in st.session_state and st.session_state.show_prescription_history:
        st.markdown("---")
        show_patient_prescription_history(st.session_state.show_prescription_history, use_expanders=True)
        
        if st.button("Close Prescription History", key="close_history"):
            del st.session_state.show_prescription_history
            st.rerun()
            
# Function to show edit patient form
def show_edit_patient_form(patient_internal_id):
    conn = db_manager.get_connection()
    # Fetch by internal primary key 'id'
    patient_data_series = pd.read_sql("SELECT * FROM patients WHERE id = ?", conn, params=(patient_internal_id,)).iloc[0]
    conn.close()

    # Convert pandas Series to dict for easier handling if needed, or access directly
    patient_data = patient_data_series.to_dict()

    with st.expander(f"Edit Patient: {patient_data['first_name']} {patient_data['last_name']} (ID: {patient_data['patient_id']})", expanded=True):
        with st.form(key=f"edit_patient_form_{patient_internal_id}"):
            st.subheader(f"Editing Patient Record: {patient_data['patient_id']}")

            col1, col2 = st.columns(2)
            with col1:
                new_first_name = st.text_input("First Name*", value=patient_data['first_name'])
                new_last_name = st.text_input("Last Name*", value=patient_data['last_name'])
                try:
                    dob_val = datetime.datetime.strptime(patient_data['date_of_birth'], '%Y-%m-%d').date()
                except:
                    dob_val = datetime.date.today() # Fallback, should not happen with good data
                new_date_of_birth = st.date_input("Date of Birth*", value=dob_val)
                gender_options = ["Male", "Female", "Other"]
                current_gender_index = gender_options.index(patient_data['gender']) if patient_data['gender'] in gender_options else 0
                new_gender = st.selectbox("Gender*", gender_options, index=current_gender_index)
                new_phone = st.text_input("Phone", value=patient_data['phone'])
                new_email = st.text_input("Email", value=patient_data['email'])

            with col2:
                new_address = st.text_area("Address", value=patient_data['address'])
                new_allergies = st.text_area("Known Allergies", value=patient_data['allergies'])
                new_medical_conditions = st.text_area("Medical Conditions", value=patient_data['medical_conditions'])
                new_emergency_contact = st.text_input("Emergency Contact", value=patient_data['emergency_contact'])
                new_insurance_info = st.text_input("Insurance Information", value=patient_data['insurance_info'])
                new_is_active = st.checkbox("Is Active", value=bool(patient_data['is_active']))

            submit_button = st.form_submit_button("Save Patient Changes")

            if submit_button:
                if new_first_name and new_last_name and new_date_of_birth and new_gender:
                    updated_fields_dict = {
                        "first_name": new_first_name, "last_name": new_last_name,
                        "date_of_birth": new_date_of_birth.isoformat(), "gender": new_gender,
                        "phone": new_phone, "email": new_email, "address": new_address,
                        "allergies": new_allergies, "medical_conditions": new_medical_conditions,
                        "emergency_contact": new_emergency_contact, "insurance_info": new_insurance_info,
                        "is_active": new_is_active
                    }

                    # Determine actual changes for logging
                    changed_fields_log = []
                    for key, value in updated_fields_dict.items():
                        # Special handling for boolean as it might be stored as int
                        if key == 'is_active':
                            if bool(patient_data[key]) != bool(value):
                                changed_fields_log.append(key)
                        elif str(patient_data[key]) != str(value): # Compare as strings for simplicity
                            changed_fields_log.append(key)

                    if not changed_fields_log:
                        st.info("No changes detected.")
                        st.session_state.edit_patient_id = None # Close form
                        st.rerun()
                        return

                    try:
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()

                        set_clause = ", ".join([f"{key} = ?" for key in updated_fields_dict.keys()])
                        values = list(updated_fields_dict.values())
                        values.append(patient_internal_id) # For the WHERE id = ?

                        cursor.execute(f"UPDATE patients SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", tuple(values))
                        conn.commit()
                        conn.close()

                        log_activity(st.session_state.user['id'], 'update_patient', 'patient', patient_data['patient_id'],
                                     metadata={"updated_fields": changed_fields_log, "patient_internal_id": patient_internal_id})
                        st.success(f"Patient {new_first_name} {new_last_name} updated successfully!")
                        st.session_state.edit_patient_id = None # Close form
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error updating patient: {str(e)}")
                else:
                    st.error("Please fill in all required fields (*).")

# Function to confirm and perform deactivate/restore action on a patient
def confirm_and_action_patient(patient_internal_id, is_currently_active):
    action_verb = "Deactivate" if is_currently_active else "Restore"
    action_desc = "deactivating" if is_currently_active else "restoring"

    # Fetch patient_id for display message
    conn = db_manager.get_connection()
    patient_display_id = pd.read_sql("SELECT patient_id FROM patients WHERE id = ?", conn, params=(patient_internal_id,)).iloc[0]['patient_id']
    conn.close()

    st.warning(f"Are you sure you want to {action_verb.lower()} patient ID {patient_display_id} (Internal ID: {patient_internal_id})?")

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button(f"Yes, {action_verb} Patient", key=f"confirm_action_patient_{patient_internal_id}", type="primary"):
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()

                new_status = 0 if is_currently_active else 1
                cursor.execute("UPDATE patients SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, patient_internal_id))
                conn.commit()
                conn.close()

                log_activity(st.session_state.user['id'], f'{action_desc}_patient', 'patient', patient_display_id,
                             metadata={"new_status": "active" if new_status else "inactive", "patient_internal_id": patient_internal_id})
                st.success(f"Patient {patient_display_id} successfully {action_desc}d.")
                st.session_state.action_patient_id = None # Reset and close confirmation
                st.rerun()

            except Exception as e:
                st.error(f"Error {action_desc} patient: {str(e)}")

    with col2:
        if st.button("Cancel", key=f"cancel_action_patient_{patient_internal_id}"):
            st.session_state.action_patient_id = None # Reset and close confirmation
            st.rerun()

def show_patient_prescription_history(patient_id, use_expanders=True):
    """Show prescription history for a patient"""
    conn = db_manager.get_connection()
    
    prescriptions = pd.read_sql("""
        SELECT p.prescription_id, p.diagnosis, p.notes, p.created_at,
               u.full_name as doctor_name
        FROM prescriptions p
        JOIN users u ON p.doctor_id = u.id
        JOIN patients pt ON p.patient_id = pt.id
        WHERE pt.patient_id = ?
        ORDER BY p.created_at DESC
    """, conn, params=[patient_id])
    
    if not prescriptions.empty:
        if use_expanders:
            st.subheader(f"Prescription History for {patient_id}")
        else:
            st.markdown(f"**📋 Prescription History for {patient_id}**")
        
        for _, prescription in prescriptions.iterrows():
            prescription_title = f"📋 {prescription['prescription_id']} - {prescription['created_at'][:10]}"
            
            if use_expanders:
                with st.expander(prescription_title):
                    display_prescription_details(prescription, conn)
            else:
                st.markdown(f"**{prescription_title}**")
                with st.container():
                    display_prescription_details(prescription, conn)
                st.markdown("---")
    else:
        st.info("No prescription history found for this patient")
    
    conn.close()
def display_prescription_details(prescription, conn):
    """Helper function to display prescription details"""
    st.write(f"**Doctor:** {prescription['doctor_name']}")
    st.write(f"**Diagnosis:** {prescription['diagnosis']}")
    
    # Get medications for this prescription
    medications = pd.read_sql("""
        SELECT m.name, pi.dosage, pi.frequency, pi.duration, pi.instructions
        FROM prescription_items pi
        JOIN medications m ON pi.medication_id = m.id
        JOIN prescriptions p ON pi.prescription_id = p.id
        WHERE p.prescription_id = ?
    """, conn, params=[prescription['prescription_id']])
    
    if not medications.empty:
        st.write("**Medications:**")
        for _, med in medications.iterrows():
            st.write(f"• {med['name']} - {med['dosage']}, {med['frequency']}, {med['duration']}")
    
    if prescription['notes']:
        st.write(f"**Notes:** {prescription['notes']}")
        
# Today's Patients (Doctor only)
def show_todays_patients():
    st.markdown('<div class="main-header"><h1>📅 Today\'s Patients</h1></div>', unsafe_allow_html=True)
    
    conn = db_manager.get_connection()
    
    # Get today's visits with patient information
    todays_patients = pd.read_sql("""
        SELECT v.id as visit_id, p.id as patient_db_id, p.patient_id, p.first_name, p.last_name, 
               p.date_of_birth, p.gender, p.allergies, p.medical_conditions,
               v.visit_type, v.current_problems, v.vital_signs, v.notes, v.consultation_completed,
               v.is_followup, v.is_report_consultation
        FROM patient_visits v
        JOIN patients p ON v.patient_id = p.id
        WHERE v.visit_date = date('now')
        ORDER BY v.consultation_completed ASC, v.created_at ASC
    """, conn)
    
    if not todays_patients.empty:
        # Search functionality
        search_term = st.text_input("Search today's patients...")
        
        filtered_patients = todays_patients.copy()
        if search_term:
            filtered_patients = filtered_patients[
                filtered_patients['first_name'].str.contains(search_term, case=False, na=False) |
                filtered_patients['last_name'].str.contains(search_term, case=False, na=False) |
                filtered_patients['patient_id'].str.contains(search_term, case=False, na=False)
            ]
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_patients = len(filtered_patients)
            st.metric("Total Patients", total_patients)
        with col2:
            completed = len(filtered_patients[filtered_patients['consultation_completed'] == 1])
            st.metric("Completed", completed)
        with col3:
            waiting = total_patients - completed
            st.metric("Waiting", waiting)
        
        st.markdown("---")
        
        # Display patient cards
        for _, patient in filtered_patients.iterrows():
            status_class = "patient-completed" if patient['consultation_completed'] else "patient-waiting"
            status_icon = "✅" if patient['consultation_completed'] else "⏳"
            
            st.markdown(f'<div class="{status_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {status_icon} {patient['first_name']} {patient['last_name']}")
                st.markdown(f"**Patient ID:** {patient['patient_id']}")
                
                age = calculate_age(patient['date_of_birth'])
                st.markdown(f"**Age/Gender:** {age} years, {patient['gender']}")
                
                st.markdown(f"**Visit Type:** {patient['visit_type']}")
                if patient['is_followup']:
                    st.markdown("🔄 **Follow-up Visit**")
                if patient['is_report_consultation']:
                    st.markdown("📋 **Report Consultation**")
                
                st.markdown(f"**Current Problems:** {patient['current_problems']}")
                
                if patient['vital_signs']:
                    st.markdown(f"**Vital Signs:** {patient['vital_signs']}")
                
                if patient['allergies']:
                    st.markdown(f"⚠️ **Allergies:** {patient['allergies']}")
                
                if patient['medical_conditions']:
                    st.markdown(f"🏥 **Medical Conditions:** {patient['medical_conditions']}")
            
            with col2:
                if not patient['consultation_completed']:
                    if st.button(f"📝 Prescribe", key=f"prescribe_{patient['visit_id']}"):
                        # Set the page first
                        st.session_state.current_page = 'create_prescription'
                        # Then set the patient data
                        st.session_state.selected_patient = {
                            'visit_id': patient['visit_id'],
                            'patient_db_id': patient['patient_db_id'],
                            'patient_id': patient['patient_id'],
                            'name': f"{patient['first_name']} {patient['last_name']}",
                            'age': calculate_age(patient['date_of_birth']),
                            'gender': patient['gender'],
                            'allergies': patient['allergies'] or 'None known',
                            'medical_conditions': patient['medical_conditions'] or 'None',
                            'current_problems': patient['current_problems'],
                            'date_of_birth': patient['date_of_birth']  # Add this for PDF generation
                        }
                        
                        # Clear any existing prescription data to start fresh
                        if 'prescription_medications' in st.session_state:
                            st.session_state.prescription_medications = []
                        if 'prescription_lab_tests' in st.session_state:
                            st.session_state.prescription_lab_tests = []
                        if 'ai_analysis_result' in st.session_state:
                            del st.session_state.ai_analysis_result
                        
                        # Force a rerun to navigate to the prescription page
                        st.rerun()
                else:
                    st.success("Consultation Completed")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("No patients scheduled for today")
    
    conn.close()

# Create Prescription (Doctor only)
def show_create_prescription():
    st.markdown('<div class="main-header"><h1>📝 Create Prescription</h1></div>', unsafe_allow_html=True)
    
    # Initialize session state for prescription items if not exists
    if 'prescription_medications' not in st.session_state:
        st.session_state.prescription_medications = []
    if 'prescription_lab_tests' not in st.session_state:
        st.session_state.prescription_lab_tests = []
    
    # Patient selection
    patient_info = None
    if 'selected_patient' in st.session_state and st.session_state.selected_patient:
        patient_info = st.session_state.selected_patient
        st.success(f"Creating prescription for: {patient_info['name']} ({patient_info['patient_id']}). Visit ID: {patient_info.get('visit_id', 'N/A')}")
    elif 'manual_patient_id_selected' in st.session_state and st.session_state.manual_patient_id_selected:
        # Fetch patient details for manually selected patient
        conn = db_manager.get_connection()
        p_data = pd.read_sql("SELECT * FROM patients WHERE id = ?", conn, params=(st.session_state.manual_patient_id_selected,)).iloc[0]
        conn.close()
        patient_info = {
            'patient_db_id': p_data['id'],
            'patient_id': p_data['patient_id'],
            'name': f"{p_data['first_name']} {p_data['last_name']}",
            'age': calculate_age(p_data['date_of_birth']),
            'gender': p_data['gender'],
            'allergies': p_data['allergies'] or 'None known',
            'medical_conditions': p_data['medical_conditions'] or 'None',
            'current_problems': st.session_state.get('manual_patient_current_problems', '') # Get problems if entered
            # visit_id will be None for this case, or we could create a visit on the fly if needed
        }
        st.info(f"Manually selected patient: {patient_info['name']} ({patient_info['patient_id']})")

    else:
        st.subheader("Select Patient for Prescription")
        conn = db_manager.get_connection()
        patients_df = pd.read_sql("SELECT id, patient_id, first_name, last_name FROM patients WHERE is_active = 1 ORDER BY last_name, first_name", conn)
        conn.close()

        if patients_df.empty:
            st.error("No active patients available. Please add patients first.")
            return

        patient_options = {f"{row['first_name']} {row['last_name']} ({row['patient_id']})": row['id'] for _, row in patients_df.iterrows()}
        
        selected_patient_display_name = st.selectbox("Choose Patient*", list(patient_options.keys()), index=None, placeholder="Select a patient...")
        
        # Optional: Allow entering current problems if not coming from a visit
        manual_current_problems = st.text_area("Current Problems/Reason for Prescription (if not linked to a specific visit)", key="manual_patient_current_problems_input")

        if st.button("Load Patient for Prescription"):
            if selected_patient_display_name:
                st.session_state.manual_patient_id_selected = patient_options[selected_patient_display_name]
                st.session_state.manual_patient_current_problems = manual_current_problems # Save problems
                # Clear selected_patient from today's list if it exists
                if 'selected_patient' in st.session_state:
                    del st.session_state.selected_patient
                st.rerun()
            else:
                st.error("Please select a patient.")
        return # Stop further rendering until patient is loaded

    if not patient_info:
        st.warning("Please select a patient to proceed.")
        return

    # --- Prescription Form Starts Here ---
    st.markdown("---")
    st.subheader("1. Diagnosis and Notes")
    diagnosis = st.text_area("Diagnosis*", value=patient_info.get('current_problems', '')) # Pre-fill with current problems
    general_notes = st.text_area("General Notes for Prescription")

    # --- Medications Section ---
    st.subheader("2. Medications")
    
    with st.form(key="add_medication_item_form", clear_on_submit=True):
        col_med_select, col_med_dose, col_med_freq, col_med_dur = st.columns(4)

        conn = db_manager.get_connection()
        medications_list = pd.read_sql("SELECT id, name, strengths FROM medications WHERE is_active = 1 ORDER BY name", conn)
        conn.close()
        medication_options = {f"{row['name']} ({row['strengths'] or 'N/A'})": row['id'] for _, row in medications_list.iterrows()}

        with col_med_select:
            selected_med_name = st.selectbox("Select Medication", list(medication_options.keys()), index=None, key="med_select")
        with col_med_dose:
            dosage = st.text_input("Dosage", key="med_dosage")
        with col_med_freq:
            frequency = st.text_input("Frequency", key="med_frequency")
        with col_med_dur:
            duration = st.text_input("Duration", key="med_duration")

        med_instructions = st.text_input("Instructions (e.g., before/after food)", key="med_instructions")

        add_med_submit_button = st.form_submit_button("Add Medication to Prescription")

        if add_med_submit_button:
            if selected_med_name and dosage and frequency and duration:
                med_id = medication_options[selected_med_name]
                med_name_display = selected_med_name # Use the display name which includes strength for clarity

                st.session_state.prescription_medications.append({
                    "id": med_id, "name": med_name_display, "dosage": dosage,
                    "frequency": frequency, "duration": duration, "instructions": med_instructions
                })
                # Manual clearing of session state for inputs is removed due to clear_on_submit=True
                st.rerun()
            else:
                st.error("Please fill in Medication, Dosage, Frequency, and Duration.")

    if st.session_state.prescription_medications:
        st.markdown("**Current Medications in Prescription:**")
        for i, med in enumerate(st.session_state.prescription_medications):
            col_disp_med, col_disp_action = st.columns([4,1])
            with col_disp_med:
                st.markdown(f"• **{med['name']}**: {med['dosage']}, {med['frequency']}, for {med['duration']}. *Instructions: {med['instructions'] or 'N/A'}*")
            with col_disp_action:
                if st.button(f"Remove##med{i}", key=f"remove_med_{i}"):
                    st.session_state.prescription_medications.pop(i)
                    st.rerun()
        st.markdown("---")

    # --- Lab Tests Section ---
    st.subheader("3. Lab Tests")

    with st.form(key="add_lab_test_item_form", clear_on_submit=True):
        col_lab_select, col_lab_urgency = st.columns(2)

        conn = db_manager.get_connection()
        lab_tests_list = pd.read_sql("SELECT id, test_name FROM lab_tests WHERE is_active = 1 ORDER BY test_name", conn)
        conn.close()
        lab_test_options = {row['test_name']: row['id'] for _, row in lab_tests_list.iterrows()}

        with col_lab_select:
            selected_lab_test_name = st.selectbox("Select Lab Test", list(lab_test_options.keys()), index=None, key="lab_select")
        with col_lab_urgency:
            lab_urgency = st.selectbox("Urgency", ["Routine", "Urgent", "STAT"], key="lab_urgency") # Default is "Routine"

        lab_instructions = st.text_input("Instructions for Lab Test", key="lab_instructions")

        add_lab_submit_button = st.form_submit_button("Add Lab Test to Prescription")

        if add_lab_submit_button:
            if selected_lab_test_name:
                test_id = lab_test_options[selected_lab_test_name]
                st.session_state.prescription_lab_tests.append({
                    "id": test_id, "name": selected_lab_test_name,
                    "urgency": lab_urgency, "instructions": lab_instructions
                })
                # Manual clearing of session state for inputs is removed due to clear_on_submit=True
                # For selectbox 'lab_urgency', clear_on_submit will reset it to its initial default ("Routine")
                st.rerun()
            else:
                st.error("Please select a Lab Test.")

    if st.session_state.prescription_lab_tests:
        st.markdown("**Current Lab Tests in Prescription:**")
        for i, test in enumerate(st.session_state.prescription_lab_tests):
            col_disp_lab, col_disp_action_lab = st.columns([4,1])
            with col_disp_lab:
                st.markdown(f"• **{test['name']}** ({test['urgency']}). *Instructions: {test['instructions'] or 'N/A'}*")
            with col_disp_action_lab:
                if st.button(f"Remove##lab{i}", key=f"remove_lab_{i}"):
                    st.session_state.prescription_lab_tests.pop(i)
                    st.rerun()
        st.markdown("---")

    # --- AI Analysis Section ---
    st.subheader("4. AI Drug Interaction Analysis")
    if st.button("Analyze Drug Interactions", key="analyze_interactions_button"):
        if not st.session_state.prescription_medications:
            st.warning("Please add medications to analyze interactions.")
        else:
            with st.spinner("Analyzing drug interactions..."):
                # Prepare medication data for AI
                meds_for_ai = []
                for med_item in st.session_state.prescription_medications:
                    # Find original medication name without strength for better AI processing if needed
                    # For now, using the name as is from med_item['name'] which might include strength
                    meds_for_ai.append({
                        "name": med_item['name'].split(' (')[0], # Attempt to get base name
                        "dosage": med_item['dosage'],
                        "frequency": med_item['frequency']
                    })

                ai_patient_info = {
                    'age': patient_info.get('age', 'Unknown'),
                    'gender': patient_info.get('gender', 'Unknown'),
                    'allergies': patient_info.get('allergies', 'None known'),
                    'medical_conditions': patient_info.get('medical_conditions', 'None')
                }
                st.session_state.ai_analysis_result = ai_analyzer.analyze_drug_interactions(meds_for_ai, ai_patient_info)
                
    if 'ai_analysis_result' in st.session_state and st.session_state.ai_analysis_result:
        display_ai_analysis(st.session_state.ai_analysis_result)

    # --- Finalize and Save Section ---
    st.markdown("---")
    st.subheader("5. Finalize and Save Prescription")

    # QR Code Placeholder
    qr_placeholder = st.empty()

    if st.button("✅ Finalize and Save Prescription", use_container_width=True, type="primary"):
        if not diagnosis:
            st.error("Diagnosis is a required field.")
        elif not st.session_state.prescription_medications and not st.session_state.prescription_lab_tests:
            st.error("Prescription must contain at least one medication or lab test.")
        else:
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()

                prescription_id_text = generate_prescription_id()
                ai_analysis_json = json.dumps(st.session_state.get('ai_analysis_result')) if st.session_state.get('ai_analysis_result') else None

                # Insert into prescriptions table
                cursor.execute("""
                    INSERT INTO prescriptions (prescription_id, doctor_id, patient_id, visit_id, diagnosis, notes, ai_interaction_analysis, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                """, (prescription_id_text, st.session_state.user['id'], patient_info['patient_db_id'],
                      patient_info.get('visit_id'), diagnosis, general_notes, ai_analysis_json))

                db_prescription_id = cursor.lastrowid # Get the ID of the inserted prescription

                # Insert medication items
                for med in st.session_state.prescription_medications:
                    cursor.execute("""
                        INSERT INTO prescription_items (prescription_id, medication_id, dosage, frequency, duration, instructions)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (db_prescription_id, med['id'], med['dosage'], med['frequency'], med['duration'], med['instructions']))

                # Insert lab test items
                for test in st.session_state.prescription_lab_tests:
                    cursor.execute("""
                        INSERT INTO prescription_lab_tests (prescription_id, lab_test_id, urgency, instructions)
                        VALUES (?, ?, ?, ?)
                    """, (db_prescription_id, test['id'], test['urgency'], test['instructions']))

                # Mark visit as completed if applicable
                if patient_info.get('visit_id'):
                    cursor.execute("UPDATE patient_visits SET consultation_completed = 1 WHERE id = ?", (patient_info['visit_id'],))

                conn.commit()

                # Log activity
                log_activity(st.session_state.user['id'], 'create_prescription', 'prescription', db_prescription_id,
                             metadata={'prescription_id_text': prescription_id_text, 'patient_id': patient_info['patient_id']})

                st.success(f"Prescription {prescription_id_text} saved successfully!")

                # Generate PDF data
                pdf_data = {
                    "prescription_id": prescription_id_text,
                    "doctor_name": st.session_state.user['full_name'],
                    "specialization": st.session_state.user.get('specialization', 'N/A'),
                    "medical_license": st.session_state.user.get('medical_license', 'N/A'),
                    "date": datetime.date.today().isoformat(),
                    "patient_name": patient_info['name'],
                    "patient_id": patient_info['patient_id'],
                    "dob": patient_info.get('age', 'N/A'), # PDF expects DOB, but patient_info has age. This might need adjustment or passing DOB.
                                                          # For now, using age. Let's assume PDFGenerator can handle 'age' or we adjust patient_info.
                                                          # Corrected: PDF needs DOB. Let's fetch it if not available.
                                                          # If patient_info came from selected_patient, it has raw date_of_birth.
                                                          # If from manual selection, p_data['date_of_birth'] is available.
                    "diagnosis": diagnosis,
                    "medications": st.session_state.prescription_medications,
                    "lab_tests": st.session_state.prescription_lab_tests,
                    "notes": general_notes
                }
                # Ensure DOB is correct for PDF
                if 'date_of_birth' in patient_info: # From today's patients
                     pdf_data["dob"] = patient_info['date_of_birth']
                elif 'manual_patient_id_selected' in st.session_state : # From manual selection
                     conn_temp = db_manager.get_connection()
                     p_dob = pd.read_sql("SELECT date_of_birth FROM patients WHERE id = ?", conn_temp, params=(st.session_state.manual_patient_id_selected,)).iloc[0]['date_of_birth']
                     conn_temp.close()
                     pdf_data["dob"] = p_dob


                pdf_bytes = pdf_generator.generate_prescription_pdf(pdf_data)
                st.download_button(
                    label="📄 Download Prescription PDF",
                    data=pdf_bytes,
                    file_name=f"prescription_{prescription_id_text}.pdf",
                    mime="application/pdf"
                )

                # Generate and display QR code for the prescription ID
                qr_img = qrcode.make(f"Prescription ID: {prescription_id_text}\nPatient: {patient_info['name']}\nDate: {pdf_data['date']}")
                img_byte_arr = io.BytesIO()
                qr_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                with qr_placeholder.container(): # Use the placeholder
                    st.image(img_byte_arr, caption="Scan for Prescription Details", width=150)

                # Clear session state for next prescription
                st.session_state.prescription_medications = []
                st.session_state.prescription_lab_tests = []
                if 'ai_analysis_result' in st.session_state:
                    del st.session_state.ai_analysis_result
                if 'selected_patient' in st.session_state: # Navigated from Today's Patients
                    del st.session_state.selected_patient
                if 'manual_patient_id_selected' in st.session_state: # Manually selected
                    del st.session_state.manual_patient_id_selected
                if 'manual_patient_current_problems' in st.session_state:
                    del st.session_state.manual_patient_current_problems
                # Consider not rerunning immediately to let user download PDF/see QR
                # st.rerun()

            except Exception as e:
                st.error(f"Error saving prescription: {str(e)}")
                conn.rollback() # Rollback on error
            finally:
                if conn:
                    conn.close()

# Templates Management (Doctor)
def show_templates():
    st.markdown('<div class="main-header"><h1>📋 Prescription Templates</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["My Templates", "Create Template"])
    
    with tab1:
        conn = db_manager.get_connection()
        templates_df = pd.read_sql("""
            SELECT id, name, category, template_data, created_at
            FROM templates
            WHERE doctor_id = ? AND is_active = 1
            ORDER BY category, name
        """, conn, params=[st.session_state.user['id']])
        conn.close()
        
        if not templates_df.empty:
            # Group by category
            categories = templates_df['category'].unique()
            
            for category in categories:
                st.subheader(f"📂 {category or 'Uncategorized'}")
                category_templates = templates_df[templates_df['category'] == category]
                
                for _, template in category_templates.iterrows():
                    with st.expander(f"📋 {template['name']}"):
                        template_data = json.loads(template['template_data']) if template['template_data'] else {}
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Created:** {template['created_at'][:10]}")
                            
                            if template_data.get('medications'):
                                st.write("**Medications:**")
                                for med in template_data['medications']:
                                    st.write(f"• {med['name']} - {med['dosage']}, {med['frequency']}, {med['duration']}")
                            
                            if template_data.get('lab_tests'):
                                st.write("**Lab Tests:**")
                                for test in template_data['lab_tests']:
                                    st.write(f"• {test['name']} ({test['urgency']})")
                        
                        with col2:
                            if st.button(f"Use Template", key=f"use_{template['id']}"):
                                apply_template(template_data)
                                st.session_state.current_page = 'create_prescription'
                                st.rerun()
                            
                            if st.button(f"Delete", key=f"delete_{template['id']}"):
                                delete_template(template['id'])
                                st.rerun()
        else:
            st.info("No templates created yet")
    
    with tab2:
        st.subheader("Create New Template")
        
        with st.form("create_template_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.text_input("Template Name*")
                template_category = st.text_input("Category", placeholder="e.g., Cardiology, General")
            
            # Medication selection for template
            st.subheader("Medications")
            
            # Get medications
            conn = db_manager.get_connection()
            medications_df = pd.read_sql("SELECT id, name FROM medications WHERE is_active = 1 ORDER BY name", conn)
            conn.close()
            
            selected_medications = st.multiselect("Select Medications", 
                                                 options=medications_df['name'].tolist())
            
            # Lab tests selection
            st.subheader("Lab Tests")
            
            conn = db_manager.get_connection()
            lab_tests_df = pd.read_sql("SELECT id, test_name FROM lab_tests WHERE is_active = 1 ORDER BY test_name", conn)
            conn.close()
            
            selected_lab_tests = st.multiselect("Select Lab Tests", 
                                               options=lab_tests_df['test_name'].tolist())
            
            submit_button = st.form_submit_button("Create Template")
            
            if submit_button:
                if template_name:
                    try:
                        # Prepare template data
                        template_data = {
                            'medications': [{'name': med, 'dosage': '', 'frequency': '', 'duration': ''} 
                                          for med in selected_medications],
                            'lab_tests': [{'name': test, 'urgency': 'routine'} 
                                        for test in selected_lab_tests]
                        }
                        
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            INSERT INTO templates (doctor_id, name, category, template_data)
                            VALUES (?, ?, ?, ?)
                        """, (st.session_state.user['id'], template_name, template_category, 
                              json.dumps(template_data)))
                        
                        conn.commit()
                        conn.close()
                        
                        log_activity(st.session_state.user['id'], 'create_template', 'template')
                        st.success("Template created successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error creating template: {str(e)}")
                else:
                    st.error("Please provide a template name!")

def apply_template(template_data):
    """Apply template to current prescription"""
    st.session_state.prescription_medications = template_data.get('medications', [])
    st.session_state.prescription_lab_tests = template_data.get('lab_tests', [])

def delete_template(template_id):
    """Delete a template"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE templates SET is_active = 0 WHERE id = ?", (template_id,))
    
    conn.commit()
    conn.close()
    
    log_activity(st.session_state.user['id'], 'delete_template', 'template', template_id)

# Analytics Dashboard
def show_analytics():
    st.markdown('<div class="main-header"><h1>📊 Analytics Dashboard</h1></div>', unsafe_allow_html=True)
    
    user_type = st.session_state.user['user_type']
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=datetime.date.today() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("To Date", value=datetime.date.today())
    
    conn = db_manager.get_connection()
    
    # Key Metrics
    st.subheader("📈 Key Metrics")
    
    if user_type == 'super_admin':
        # Super admin sees all data
        total_prescriptions = pd.read_sql("""
            SELECT COUNT(*) as count FROM prescriptions 
            WHERE DATE(created_at) BETWEEN ? AND ?
        """, conn, params=[start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_patients = pd.read_sql("""
            SELECT COUNT(DISTINCT patient_id) as count FROM prescriptions 
            WHERE DATE(created_at) BETWEEN ? AND ?
        """, conn, params=[start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_visits = pd.read_sql("""
            SELECT COUNT(*) as count FROM patient_visits 
            WHERE visit_date BETWEEN ? AND ?
        """, conn, params=[start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
    elif user_type == 'doctor':
        # Doctor sees only their data
        total_prescriptions = pd.read_sql("""
            SELECT COUNT(*) as count FROM prescriptions 
            WHERE doctor_id = ? AND DATE(created_at) BETWEEN ? AND ?
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_patients = pd.read_sql("""
            SELECT COUNT(DISTINCT patient_id) as count FROM prescriptions 
            WHERE doctor_id = ? AND DATE(created_at) BETWEEN ? AND ?
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_visits = pd.read_sql("""
            SELECT COUNT(*) as count FROM patient_visits v
            JOIN prescriptions p ON v.id = p.visit_id
            WHERE p.doctor_id = ? AND v.visit_date BETWEEN ? AND ?
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
    else:  # assistant
        # Assistant sees only their registered visits
        total_visits = pd.read_sql("""
            SELECT COUNT(*) as count FROM patient_visits 
            WHERE created_by = ? AND visit_date BETWEEN ? AND ?
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_patients = pd.read_sql("""
            SELECT COUNT(DISTINCT patient_id) as count FROM patient_visits 
            WHERE created_by = ? AND visit_date BETWEEN ? AND ?
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()]).iloc[0]['count']
        
        total_prescriptions = 0  # Assistants don't create prescriptions
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Prescriptions", total_prescriptions)
    with col2:
        st.metric("Total Patients", total_patients)
    with col3:
        st.metric("Total Visits", total_visits)
    
    # Charts and visualizations
    if user_type != 'assistant':
        st.subheader("📊 Prescription Trends")
        
        # Prescriptions over time
        if user_type == 'super_admin':
            prescriptions_over_time = pd.read_sql("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM prescriptions
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date
            """, conn, params=[start_date.isoformat(), end_date.isoformat()])
        else:  # doctor
            prescriptions_over_time = pd.read_sql("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM prescriptions
                WHERE doctor_id = ? AND DATE(created_at) BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY date
            """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()])
        
        if not prescriptions_over_time.empty:
            fig_line = px.line(prescriptions_over_time, x='date', y='count', 
                              title='Prescriptions Over Time',
                              labels={'date': 'Date', 'count': 'Number of Prescriptions'})
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Top medications
        st.subheader("💊 Most Prescribed Medications")
        
        if user_type == 'super_admin':
            top_medications = pd.read_sql("""
                SELECT m.name, COUNT(*) as count
                FROM prescription_items pi
                JOIN medications m ON pi.medication_id = m.id
                JOIN prescriptions p ON pi.prescription_id = p.id
                WHERE DATE(p.created_at) BETWEEN ? AND ?
                GROUP BY m.name
                ORDER BY count DESC
                LIMIT 10
            """, conn, params=[start_date.isoformat(), end_date.isoformat()])
        else:  # doctor
            top_medications = pd.read_sql("""
                SELECT m.name, COUNT(*) as count
                FROM prescription_items pi
                JOIN medications m ON pi.medication_id = m.id
                JOIN prescriptions p ON pi.prescription_id = p.id
                WHERE p.doctor_id = ? AND DATE(p.created_at) BETWEEN ? AND ?
                GROUP BY m.name
                ORDER BY count DESC
                LIMIT 10
            """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()])

        if not top_medications.empty:
            try:
                # Create the chart with proper Plotly syntax
                fig_bar = px.bar(
                    top_medications, 
                    x='name', 
                    y='count',
                    title='Top 10 Most Prescribed Medications',
                    labels={'name': 'Medication', 'count': 'Times Prescribed'}
                )
                
                # Update layout instead of using update_xaxis
                fig_bar.update_layout(
                    xaxis_title="Medication",
                    yaxis_title="Times Prescribed",
                    xaxis={'tickangle': 45},
                    showlegend=False,
                    height=500
                )
                
                # Display the chart
                st.plotly_chart(fig_bar, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error creating medications chart: {str(e)}")
                # Fallback: Display as table if chart fails
                st.subheader("Top 10 Most Prescribed Medications (Table View)")
                st.dataframe(top_medications, use_container_width=True)
        else:
            st.info("No medication prescription data available for the selected date range.")
    
    # Visit analytics for all user types
    st.subheader("🏥 Visit Analytics")
    
    if user_type == 'assistant':
        visit_types = pd.read_sql("""
            SELECT visit_type, COUNT(*) as count
            FROM patient_visits
            WHERE created_by = ? AND visit_date BETWEEN ? AND ?
            GROUP BY visit_type
        """, conn, params=[st.session_state.user['id'], start_date.isoformat(), end_date.isoformat()])
    else:
        visit_types = pd.read_sql("""
            SELECT visit_type, COUNT(*) as count
            FROM patient_visits
            WHERE visit_date BETWEEN ? AND ?
            GROUP BY visit_type
        """, conn, params=[start_date.isoformat(), end_date.isoformat()])
    
    if not visit_types.empty:
        fig_pie = px.pie(visit_types, values='count', names='visit_type',
                        title='Visit Types Distribution')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    
    if user_type == 'assistant':
        recent_activity = pd.read_sql("""
            SELECT action_type, entity_type, timestamp, metadata
            FROM analytics
            WHERE user_id = ? AND action_type NOT IN ('login', 'logout')
            ORDER BY timestamp DESC
            LIMIT 10
        """, conn, params=[st.session_state.user['id']])
    elif user_type == 'doctor':
        recent_activity = pd.read_sql("""
            SELECT action_type, entity_type, timestamp, metadata
            FROM analytics
            WHERE user_id = ? AND action_type NOT IN ('login', 'logout')
            ORDER BY timestamp DESC
            LIMIT 10
        """, conn, params=[st.session_state.user['id']])
    else:  # super_admin
        recent_activity = pd.read_sql("""
            SELECT a.action_type, a.entity_type, a.timestamp, u.full_name, a.metadata
            FROM analytics a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 20
        """, conn)
    
    if not recent_activity.empty:
        st.dataframe(recent_activity, use_container_width=True)
    else:
        st.info("No recent activity")
    
    conn.close()

# Main application logic
def show_edit_user_form(user_id):
    conn = db_manager.get_connection()
    user_data = pd.read_sql("SELECT * FROM users WHERE id = ?", conn, params=(user_id,)).iloc[0]
    conn.close()

    with st.expander(f"Edit User: {user_data['full_name']} ({user_data['username']})", expanded=True):
        with st.form(key=f"edit_user_form_{user_id}"):
            st.subheader("Edit User Details")

            current_user_is_super_admin = st.session_state.user['user_type'] == 'super_admin'
            editing_self = st.session_state.user['id'] == user_id

            col1, col2 = st.columns(2)
            with col1:
                new_full_name = st.text_input("Full Name", value=user_data['full_name'])
                new_email = st.text_input("Email", value=user_data['email'])

                # User type modification constraints
                if editing_self and user_data['user_type'] == 'super_admin':
                    new_user_type = st.selectbox("User Type (Cannot change own type)", [user_data['user_type']], disabled=True, index=0)
                    st.caption("Super Admins cannot change their own user type.")
                else:
                    user_types = ["doctor", "assistant", "super_admin"]
                    current_type_index = user_types.index(user_data['user_type']) if user_data['user_type'] in user_types else 0
                    new_user_type = st.selectbox("User Type", user_types, index=current_type_index)

            with col2:
                new_phone = st.text_input("Phone", value=user_data['phone'])
                new_medical_license = st.text_input("Medical License", value=user_data['medical_license'])
                new_specialization = st.text_input("Specialization", value=user_data['specialization'])

                # Active status modification constraints
                if editing_self and user_data['user_type'] == 'super_admin':
                    new_is_active = st.checkbox("Is Active (Cannot deactivate own account)", value=bool(user_data['is_active']), disabled=True)
                    st.caption("Super Admins cannot deactivate their own account.")
                else:
                    new_is_active = st.checkbox("Is Active", value=bool(user_data['is_active']))

            st.markdown("---")
            st.subheader("Reset Password (Optional)")
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")

            submit_button = st.form_submit_button("Save Changes")

            if submit_button:
                if new_password != confirm_new_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()

                        update_fields = {
                            "full_name": new_full_name, "email": new_email, "user_type": new_user_type,
                            "phone": new_phone, "medical_license": new_medical_license,
                            "specialization": new_specialization, "is_active": new_is_active
                        }

                        # Apply constraints for super admin editing themselves
                        if editing_self and user_data['user_type'] == 'super_admin':
                            update_fields["user_type"] = user_data['user_type'] # Cannot change own type
                            update_fields["is_active"] = True # Cannot deactivate self

                        set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
                        values = list(update_fields.values())

                        if new_password:
                            set_clause += ", password_hash = ?"
                            values.append(db_manager.hash_password(new_password))

                        values.append(user_id)

                        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(values))
                        conn.commit()
                        conn.close()

                        log_activity(st.session_state.user['id'], 'update_user', 'user', user_id,
                                     metadata={"updated_fields": list(update_fields.keys()) + (["password"] if new_password else [])})
                        st.success("User details updated successfully!")
                        st.session_state.edit_user_id = None # Close form
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error updating user: {str(e)}")

def confirm_and_delete_user(user_id_to_action, is_active_status):
    action_verb = "Deactivate" if is_active_status else "Restore"
    action_desc = "deactivating" if is_active_status else "restoring"

    st.warning(f"Are you sure you want to {action_verb.lower()} user ID {user_id_to_action}?")

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button(f"Yes, {action_verb} User", key=f"confirm_delete_{user_id_to_action}", type="primary"):
            try:
                # Super admin self-delete/deactivate prevention (already handled by button disable, but double check)
                if st.session_state.user['id'] == user_id_to_action and is_active_status:
                     st.error("Operation not allowed: Super Admins cannot deactivate their own account.")
                     st.session_state.delete_user_id = None # Reset
                     st.rerun()
                     return

                conn = db_manager.get_connection()
                cursor = conn.cursor()

                new_status = 0 if is_active_status else 1
                cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id_to_action))
                conn.commit()
                conn.close()

                log_activity(st.session_state.user['id'], f'{action_desc}_user', 'user', user_id_to_action, metadata={"new_status": "active" if new_status else "inactive"})
                st.success(f"User successfully {action_desc}d.")
                st.session_state.delete_user_id = None # Reset and close confirmation
                st.rerun()

            except Exception as e:
                st.error(f"Error {action_desc} user: {str(e)}")

    with col2:
        if st.button("Cancel", key=f"cancel_delete_{user_id_to_action}"):
            st.session_state.delete_user_id = None # Reset and close confirmation
            st.rerun()

# Main application logic
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Show sidebar navigation
    show_sidebar()
    
    # Route to appropriate page based on user selection
    page = st.session_state.current_page
    
    try:
        if page == 'dashboard':
            show_dashboard()
        elif page == 'users':
            show_user_management()
        elif page == 'patients':
            show_patient_management()
        elif page == 'todays_patients':
            show_todays_patients()
        elif page == 'create_prescription':
            show_create_prescription()
        elif page == 'medications': # Placeholder for now
            show_medication_database()
            # st.markdown('<div class="main-header"><h1>💊 Medication Database</h1></div>', unsafe_allow_html=True)
            # st.info("Medication database management will be implemented here.")
        elif page == 'lab_tests':
            show_lab_tests_database()
        elif page == 'visit_registration':
            show_visit_registration()
        elif page == 'templates':
            show_templates()
        elif page == 'analytics':
            show_analytics()
        else:
            st.error("Page not found")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or contact support if the problem persists.")

# --- Medication Database Management START ---
def _display_medications_view(is_super_admin):
    st.subheader("Medication List")

    # Filters: Search, Status, Controlled Status
    col_search, col_filter_status, col_filter_controlled = st.columns([2,1,1])
    with col_search:
        search_term = st.text_input("Search by Name, Generic Name, Brand Names, or Drug Class...", key="med_view_search")
    with col_filter_status:
        status_filter = st.selectbox("Filter by Status", ["Active", "Inactive", "All"], key="med_view_status_filter", index=0)
    with col_filter_controlled:
        controlled_filter = st.selectbox("Filter by Controlled Status", ["All", "Controlled", "Not Controlled"], key="med_view_controlled_filter", index=0)

    # Pagination settings
    items_per_page = 10
    
    # Initialize page number in session state
    if 'medication_page' not in st.session_state:
        st.session_state.medication_page = 1

    # Construct SQL query
    query = """SELECT id, name, generic_name, brand_names, drug_class, dosage_forms, strengths,
                      indications, contraindications, side_effects, interactions,
                      is_controlled, is_favorite, created_by, is_active
               FROM medications"""
    params = []
    conditions = []

    if status_filter == "Active":
        conditions.append("is_active = 1")
    elif status_filter == "Inactive":
        conditions.append("is_active = 0")

    if controlled_filter == "Controlled":
        conditions.append("is_controlled = 1")
    elif controlled_filter == "Not Controlled":
        conditions.append("is_controlled = 0")

    if search_term:
        like_term = f"%{search_term}%"
        search_clause = "(name LIKE ? OR generic_name LIKE ? OR brand_names LIKE ? OR drug_class LIKE ?)"
        conditions.append(search_clause)
        params.extend([like_term] * 4)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY name ASC"

    conn = db_manager.get_connection()
    medications_df = pd.read_sql(query, conn, params=params)
    conn.close()

    if not medications_df.empty:
        # Calculate pagination
        total_items = len(medications_df)
        total_pages = (total_items - 1) // items_per_page + 1
        
        # Ensure current page is valid
        if st.session_state.medication_page > total_pages:
            st.session_state.medication_page = total_pages
        if st.session_state.medication_page < 1:
            st.session_state.medication_page = 1
        
        # Calculate start and end indices
        start_idx = (st.session_state.medication_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get current page items
        current_page_medications = medications_df.iloc[start_idx:end_idx]
        
        # Display only basic info at top
        st.info(f"📊 Showing {start_idx + 1}-{end_idx} of {total_items} medications (Page {st.session_state.medication_page} of {total_pages})")
        
        # Display medications for current page
        for index, med in current_page_medications.iterrows():
            med_id = med['id']
            med_name = med['name']
            is_active = med['is_active']
            is_controlled = med['is_controlled']

            status_text = "Active" if is_active else "Inactive"
            status_emoji = "✅" if is_active else "❌"
            controlled_text = " 🔒" if is_controlled else ""

            expander_title = f"**{med_name}** ({med['generic_name'] or 'N/A'}) {status_emoji} {status_text}{controlled_text}"

            with st.expander(expander_title):
                if is_super_admin:
                    col_details, col_actions = st.columns([3,1])
                    with col_details:
                        st.markdown(f"**Brand Names:** {med['brand_names'] or 'N/A'}")
                        st.markdown(f"**Drug Class:** {med['drug_class'] or 'N/A'}")
                        st.markdown(f"**Dosage Forms:** {med['dosage_forms'] or 'N/A'} | **Strengths:** {med['strengths'] or 'N/A'}")
                        st.markdown(f"**Indications:** {med['indications'] or 'N/A'}")
                        st.markdown(f"**Contraindications:** {med['contraindications'] or 'N/A'}")
                        st.markdown(f"**Side Effects:** {med['side_effects'] or 'N/A'}")
                        st.markdown(f"**Interactions:** {med['interactions'] or 'N/A'}")
                        st.caption(f"Favorite: {'Yes' if med['is_favorite'] else 'No'} | Created by User ID: {med['created_by'] or 'N/A'} | Internal ID: {med['id']}")

                    with col_actions:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Edit", key=f"edit_med_{med['id']}", use_container_width=True):
                            st.session_state.edit_medication_id = med['id']
                            if 'action_medication_id' in st.session_state:
                                del st.session_state.action_medication_id
                            st.rerun()

                        action_button_text = "⚠️ Deactivate" if med['is_active'] else "✅ Restore"
                        if st.button(action_button_text, key=f"action_med_{med['id']}", use_container_width=True):
                            st.session_state.action_medication_id = med['id']
                            st.session_state.action_medication_current_status = med['is_active']
                            if 'edit_medication_id' in st.session_state:
                                del st.session_state.edit_medication_id
                            st.rerun()
                else: # Doctor or Assistant - display details directly
                    st.markdown(f"**Brand Names:** {med['brand_names'] or 'N/A'}")
                    st.markdown(f"**Drug Class:** {med['drug_class'] or 'N/A'}")
                    st.markdown(f"**Dosage Forms:** {med['dosage_forms'] or 'N/A'} | **Strengths:** {med['strengths'] or 'N/A'}")
                    st.markdown(f"**Indications:** {med['indications'] or 'N/A'}")
                    st.markdown(f"**Contraindications:** {med['contraindications'] or 'N/A'}")
                    st.markdown(f"**Side Effects:** {med['side_effects'] or 'N/A'}")
                    st.markdown(f"**Interactions:** {med['interactions'] or 'N/A'}")
                    st.caption(f"Favorite: {'Yes' if med['is_favorite'] else 'No'} | Created by User ID: {med['created_by'] or 'N/A'} | Internal ID: {med['id']}")
        
        # Pagination controls at bottom
        st.markdown("---")
        
        # Main pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⬅️ Previous", disabled=(st.session_state.medication_page <= 1)):
                st.session_state.medication_page -= 1
                st.rerun()
        
        with col2:
            if st.button("Next ➡️", disabled=(st.session_state.medication_page >= total_pages)):
                st.session_state.medication_page += 1
                st.rerun()
        
        with col3:
            st.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {st.session_state.medication_page} of {total_pages}</div>", unsafe_allow_html=True)
        
        with col4:
            # Jump to page
            target_page = st.number_input("Go to page:", min_value=1, max_value=total_pages, 
                                        value=st.session_state.medication_page, key="med_page_jump")
        
        with col5:
            if st.button("Go", key="med_go_page"):
                st.session_state.medication_page = target_page
                st.rerun()
        
    else:
        st.info("No medications found matching your criteria.")

    if is_super_admin:
        if 'edit_medication_id' in st.session_state and st.session_state.edit_medication_id is not None:
            _display_edit_medication_form(st.session_state.edit_medication_id)
        elif 'action_medication_id' in st.session_state and st.session_state.action_medication_id is not None:
            _confirm_and_action_medication(st.session_state.action_medication_id, st.session_state.action_medication_current_status)

def _display_add_medication_form():
    st.subheader("Add New Medication Record")
    with st.form("add_medication_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Medication Name*")
            generic_name = st.text_input("Generic Name")
            brand_names = st.text_input("Brand Names (comma-separated)")
            drug_class = st.text_input("Drug Class")
            dosage_forms = st.text_input("Dosage Forms (e.g., Tablet, Capsule)")
            strengths = st.text_input("Strengths (e.g., 10mg, 20mg/5ml)")
        with col2:
            indications = st.text_area("Indications")
            contraindications = st.text_area("Contraindications")
            side_effects = st.text_area("Common Side Effects")
            interactions = st.text_area("Drug Interactions")
            is_controlled = st.checkbox("Is Controlled Substance?")
            is_favorite = st.checkbox("Mark as Favorite?")

        submit_button = st.form_submit_button("Add Medication")

        if submit_button:
            if not name.strip():
                st.error("Medication Name is a required field.")
            else:
                try:
                    conn = db_manager.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO medications (name, generic_name, brand_names, drug_class, dosage_forms, strengths,
                                               indications, contraindications, side_effects, interactions,
                                               is_controlled, is_favorite, created_by, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (name, generic_name, brand_names, drug_class, dosage_forms, strengths,
                          indications, contraindications, side_effects, interactions,
                          is_controlled, is_favorite, st.session_state.user['id']))
                    conn.commit()
                    new_med_id = cursor.lastrowid
                    conn.close()
                    log_activity(st.session_state.user['id'], 'create_medication', 'medication', new_med_id, metadata={"name": name})
                    st.success(f"Medication '{name}' added successfully!")
                    # No st.rerun() here, clear_on_submit=True handles form reset. View tab will show new item on next interaction.
                except Exception as e:
                    st.error(f"Error adding medication: {str(e)}")

def _display_edit_medication_form(medication_id):
    conn = db_manager.get_connection()
    med_data_series = pd.read_sql("SELECT * FROM medications WHERE id = ?", conn, params=(medication_id,))
    conn.close()

    if med_data_series.empty:
        st.error("Medication not found or already deleted. Please refresh.")
        st.session_state.edit_medication_id = None
        st.rerun()
        return

    med_data = med_data_series.iloc[0].to_dict()

    st.subheader(f"Edit Medication: {med_data['name']}")
    with st.form(key=f"edit_med_form_{medication_id}"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Medication Name*", value=med_data['name'])
            new_generic_name = st.text_input("Generic Name", value=med_data['generic_name'])
            new_brand_names = st.text_input("Brand Names", value=med_data['brand_names'])
            new_drug_class = st.text_input("Drug Class", value=med_data['drug_class'])
            new_dosage_forms = st.text_input("Dosage Forms", value=med_data['dosage_forms'])
            new_strengths = st.text_input("Strengths", value=med_data['strengths'])
        with col2:
            new_indications = st.text_area("Indications", value=med_data['indications'])
            new_contraindications = st.text_area("Contraindications", value=med_data['contraindications'])
            new_side_effects = st.text_area("Side Effects", value=med_data['side_effects'])
            new_interactions = st.text_area("Interactions", value=med_data['interactions'])
            new_is_controlled = st.checkbox("Is Controlled Substance?", value=bool(med_data['is_controlled']))
            new_is_favorite = st.checkbox("Mark as Favorite?", value=bool(med_data['is_favorite']))
            new_is_active = st.checkbox("Is Active?", value=bool(med_data['is_active']))

        col_save, col_cancel, col_empty = st.columns([1,1,5])
        with col_save:
            submit_button = st.form_submit_button("Save Changes")
        with col_cancel:
            if st.form_submit_button("Cancel", type="secondary"):
                st.session_state.edit_medication_id = None
                st.rerun()

        if submit_button:
            if not new_name.strip():
                st.error("Medication Name is required.")
            else:
                updated_fields_map = {
                    "name": new_name, "generic_name": new_generic_name, "brand_names": new_brand_names,
                    "drug_class": new_drug_class, "dosage_forms": new_dosage_forms, "strengths": new_strengths,
                    "indications": new_indications, "contraindications": new_contraindications,
                    "side_effects": new_side_effects, "interactions": new_interactions,
                    "is_controlled": new_is_controlled, "is_favorite": new_is_favorite, "is_active": new_is_active
                }

                fields_to_update = {}
                for key, new_value in updated_fields_map.items():
                    old_value = med_data.get(key)
                    if isinstance(new_value, bool):
                        if bool(old_value) != new_value:
                            fields_to_update[key] = new_value
                    elif str(old_value or '') != str(new_value or ''):
                        fields_to_update[key] = new_value

                if not fields_to_update:
                    st.info("No changes detected.")
                    st.session_state.edit_medication_id = None
                    st.rerun()
                else:
                    try:
                        conn_update = db_manager.get_connection()
                        cursor = conn_update.cursor()
                        set_clause = ", ".join([f"{key} = ?" for key in fields_to_update.keys()])
                        values = list(fields_to_update.values())
                        values.append(medication_id)
                        cursor.execute(f"UPDATE medications SET {set_clause} WHERE id = ?", tuple(values))
                        conn_update.commit()
                        conn_update.close()
                        log_activity(st.session_state.user['id'], 'update_medication', 'medication', medication_id, metadata={"updated_fields": list(fields_to_update.keys())})
                        st.success(f"Medication '{new_name}' updated successfully!")
                        st.session_state.edit_medication_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating medication: {str(e)}")

def _confirm_and_action_medication(medication_id, is_currently_active):
    action_verb = "Deactivate" if is_currently_active else "Restore"
    action_desc = "deactivating" if is_currently_active else "restoring"

    conn = db_manager.get_connection()
    med_name_series = pd.read_sql("SELECT name FROM medications WHERE id = ?", conn, params=(medication_id,))
    conn.close()

    if med_name_series.empty:
        st.error("Medication not found. It might have been deleted by another user. Refreshing list.")
        st.session_state.action_medication_id = None
        st.rerun()
        return

    med_name = med_name_series.iloc[0]['name']

    st.subheader(f"{action_verb} Medication: {med_name}")
    st.markdown(f"Are you sure you want to {action_verb.lower()} medication **'{med_name}'** (ID: {medication_id})?")

    col1, col2, _ = st.columns([1,1,3])
    with col1:
        if st.button(f"Yes, {action_verb}", key=f"confirm_action_med_{medication_id}", type="primary"):
            try:
                conn_action = db_manager.get_connection()
                cursor = conn_action.cursor()
                new_status = 0 if is_currently_active else 1
                cursor.execute("UPDATE medications SET is_active = ? WHERE id = ?", (new_status, medication_id))
                conn_action.commit()
                conn_action.close()
                log_activity(st.session_state.user['id'], f'{action_desc}_medication', 'medication', medication_id, metadata={"name": med_name, "new_status": "active" if new_status else "inactive"})
                st.success(f"Medication '{med_name}' successfully {action_desc}d.")
                st.session_state.action_medication_id = None
                st.rerun()
            except Exception as e:
                st.error(f"Error {action_desc} medication: {str(e)}")
    with col2:
        if st.button("Cancel", key=f"cancel_action_med_{medication_id}", type="secondary"):
            st.session_state.action_medication_id = None
            st.rerun()

def show_medication_database():
    st.markdown('<div class="main-header"><h1>💊 Medication Database</h1></div>', unsafe_allow_html=True)
    user_type = st.session_state.user['user_type']

    if user_type == 'super_admin':
        if 'edit_medication_id' not in st.session_state:
            st.session_state.edit_medication_id = None
        if 'action_medication_id' not in st.session_state:
            st.session_state.action_medication_id = None
        # action_medication_current_status is set when action_medication_id is set.

        if st.session_state.edit_medication_id is None and st.session_state.action_medication_id is None:
            view_tab, add_tab = st.tabs(["View Medications", "Add New Medication"])
            with view_tab:
                _display_medications_view(is_super_admin=True)
            with add_tab:
                _display_add_medication_form()
        elif st.session_state.edit_medication_id is not None:
            _display_edit_medication_form(st.session_state.edit_medication_id)
        elif st.session_state.action_medication_id is not None:
             _confirm_and_action_medication(st.session_state.action_medication_id, st.session_state.action_medication_current_status)
    else:
        _display_medications_view(is_super_admin=False)
# --- Medication Database Management END ---

# --- Lab Tests Database Management START ---
def _display_lab_tests_view(is_super_admin):
    st.subheader("Lab Test List")

    col_search, col_filter_status, col_filter_category = st.columns([2,1,1])
    with col_search:
        search_term = st.text_input("Search by Test Name, Category, or Description...", key="lt_view_search")
    with col_filter_status:
        status_filter = st.selectbox("Filter by Status", ["Active", "Inactive", "All"], key="lt_status_filter", index=0)

    conn_cat = db_manager.get_connection()
    try:
        categories_df = pd.read_sql("SELECT DISTINCT test_category FROM lab_tests WHERE test_category IS NOT NULL ORDER BY test_category ASC", conn_cat)
        categories = categories_df['test_category'].tolist()
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
        categories = []
    finally:
        conn_cat.close()

    with col_filter_category:
        category_filter = st.selectbox("Filter by Category", ["All"] + categories, key="lt_category_filter")

    # Pagination settings
    items_per_page = 10
    
    # Initialize page number in session state
    if 'lab_test_page' not in st.session_state:
        st.session_state.lab_test_page = 1

    query = """SELECT id, test_name, test_category, normal_range, units, description,
                      preparation_required, created_by, is_active
               FROM lab_tests"""
    params = []
    conditions = []

    if status_filter == "Active": 
        conditions.append("is_active = 1")
    elif status_filter == "Inactive": 
        conditions.append("is_active = 0")
    if category_filter != "All": 
        conditions.append("test_category = ?")
        params.append(category_filter)

    if search_term:
        like_term = f"%{search_term}%"
        search_clause = "(test_name LIKE ? OR test_category LIKE ? OR description LIKE ?)"
        conditions.append(search_clause)
        params.extend([like_term] * 3)

    if conditions: 
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY test_name ASC"

    conn = db_manager.get_connection()
    lab_tests_df = pd.read_sql(query, conn, params=params)
    conn.close()

    if not lab_tests_df.empty:
        # Calculate pagination
        total_items = len(lab_tests_df)
        total_pages = (total_items - 1) // items_per_page + 1
        
        # Ensure current page is valid
        if st.session_state.lab_test_page > total_pages:
            st.session_state.lab_test_page = total_pages
        if st.session_state.lab_test_page < 1:
            st.session_state.lab_test_page = 1
        
        # Calculate start and end indices
        start_idx = (st.session_state.lab_test_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get current page items
        current_page_tests = lab_tests_df.iloc[start_idx:end_idx]
        
        # Display only basic info at top
        st.info(f"🔬 Showing {start_idx + 1}-{end_idx} of {total_items} lab tests (Page {st.session_state.lab_test_page} of {total_pages})")
        
        # Display lab tests for current page
        for index, test in current_page_tests.iterrows():
            test_id = test['id']
            test_name = test['test_name']
            is_active = test['is_active']
            
            status_text = "Active" if is_active else "Inactive"
            status_emoji = "✅" if is_active else "❌"
            
            expander_title = f"**{test_name}** ({test['test_category'] or 'N/A'}) {status_emoji} {status_text}"
            
            with st.expander(expander_title):
                if is_super_admin:
                    col_details, col_actions = st.columns([3,1])
                    with col_details:
                        st.markdown(f"**Normal Range:** {test['normal_range'] or 'N/A'} | **Units:** {test['units'] or 'N/A'}")
                        st.markdown(f"**Description:** {test['description'] or 'N/A'}")
                        st.markdown(f"**Preparation Required:** {test['preparation_required'] or 'None'}")
                        st.caption(f"Created by User ID: {test['created_by'] or 'N/A'} | Internal ID: {test['id']}")

                    with col_actions:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Edit", key=f"edit_lt_{test['id']}", use_container_width=True):
                            st.session_state.edit_lab_test_id = test['id']
                            if 'action_lab_test_id' in st.session_state:
                                del st.session_state.action_lab_test_id
                            st.rerun()

                        action_button_text = "⚠️ Deactivate" if test['is_active'] else "✅ Restore"
                        if st.button(action_button_text, key=f"action_lt_{test['id']}", use_container_width=True):
                            st.session_state.action_lab_test_id = test['id']
                            st.session_state.action_lab_test_current_status = test['is_active']
                            if 'edit_lab_test_id' in st.session_state:
                                del st.session_state.edit_lab_test_id
                            st.rerun()
                else: # Doctor or Assistant - display details directly
                    st.markdown(f"**Normal Range:** {test['normal_range'] or 'N/A'} | **Units:** {test['units'] or 'N/A'}")
                    st.markdown(f"**Description:** {test['description'] or 'N/A'}")
                    st.markdown(f"**Preparation Required:** {test['preparation_required'] or 'None'}")
                    st.caption(f"Created by User ID: {test['created_by'] or 'N/A'} | Internal ID: {test['id']}")
        
        # Pagination controls at bottom
        st.markdown("---")
        
        # Main pagination controls
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⬅️ Previous", disabled=(st.session_state.lab_test_page <= 1), key="lt_prev"):
                st.session_state.lab_test_page -= 1
                st.rerun()
        
        with col2:
            if st.button("Next ➡️", disabled=(st.session_state.lab_test_page >= total_pages), key="lt_next"):
                st.session_state.lab_test_page += 1
                st.rerun()
        
        with col3:
            st.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {st.session_state.lab_test_page} of {total_pages}</div>", unsafe_allow_html=True)
        
        with col4:
            # Jump to page
            target_page = st.number_input("Go to page:", min_value=1, max_value=total_pages, 
                                        value=st.session_state.lab_test_page, key="lt_page_jump")
        
        with col5:
            if st.button("Go", key="lt_go_page"):
                st.session_state.lab_test_page = target_page
                st.rerun()
        
    else: 
        st.info("No lab tests found matching your criteria.")

    # Handle edit and action forms (same as before but with unique keys)
    if hasattr(st.session_state, 'edit_lab_test_id') and st.session_state.edit_lab_test_id is not None:
        _display_edit_lab_test_form(st.session_state.edit_lab_test_id)
    elif hasattr(st.session_state, 'action_lab_test_id') and st.session_state.action_lab_test_id is not None:
        _confirm_and_action_lab_test(st.session_state.action_lab_test_id, st.session_state.get('action_lab_test_current_status', False))

def _display_add_lab_test_form():
    st.subheader("Add New Lab Test Record")
    with st.form("add_lab_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            test_name = st.text_input("Test Name*")
            test_category = st.text_input("Test Category*")
            normal_range = st.text_input("Normal Range")
            units = st.text_input("Units")
        with col2:
            description = st.text_area("Description")
            preparation_required = st.text_area("Preparation Required")
        submit_button = st.form_submit_button("Add Lab Test")
        if submit_button:
            if not test_name.strip() or not test_category.strip():
                st.error("Test Name and Test Category are required fields.")
            else:
                try:
                    conn = db_manager.get_connection(); cursor = conn.cursor()
                    cursor.execute("INSERT INTO lab_tests (test_name, test_category, normal_range, units, description, preparation_required, created_by, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                                   (test_name, test_category, normal_range, units, description, preparation_required, st.session_state.user['id']))
                    conn.commit(); new_test_id = cursor.lastrowid; conn.close()
                    log_activity(st.session_state.user['id'], 'create_lab_test', 'lab_test', new_test_id, metadata={"name": test_name})
                    st.success(f"Lab Test '{test_name}' added successfully!")
                except Exception as e: st.error(f"Error adding lab test: {str(e)}")

def _display_edit_lab_test_form(lab_test_id):
    conn = db_manager.get_connection();
    lt_data_series = pd.read_sql("SELECT * FROM lab_tests WHERE id = ?", conn, params=(lab_test_id,))
    conn.close()
    if lt_data_series.empty:
        st.error("Lab Test not found or already deleted. Please refresh.")
        st.session_state.edit_lab_test_id = None; st.rerun(); return
    lt_data = lt_data_series.iloc[0].to_dict()
    st.subheader(f"Edit Lab Test: {lt_data['test_name']}")
    with st.form(key=f"edit_lt_form_{lab_test_id}"):
        col1, col2 = st.columns(2)
        with col1:
            new_test_name = st.text_input("Test Name*", value=lt_data['test_name'])
            new_test_category = st.text_input("Test Category*", value=lt_data['test_category'])
            new_normal_range = st.text_input("Normal Range", value=lt_data['normal_range'])
            new_units = st.text_input("Units", value=lt_data['units'])
        with col2:
            new_description = st.text_area("Description", value=lt_data['description'])
            new_preparation_required = st.text_area("Preparation Required", value=lt_data['preparation_required'])
            new_is_active = st.checkbox("Is Active?", value=bool(lt_data['is_active']))
        col_save, col_cancel, _ = st.columns([1,1,5])
        with col_save: submit_button = st.form_submit_button("Save Changes")
        with col_cancel:
            if st.form_submit_button("Cancel", type="secondary"):
                st.session_state.edit_lab_test_id = None; st.rerun()
        if submit_button:
            if not new_test_name.strip() or not new_test_category.strip():
                st.error("Test Name and Test Category are required.")
            else:
                updated_fields = {"test_name": new_test_name, "test_category": new_test_category, "normal_range": new_normal_range, "units": new_units, "description": new_description, "preparation_required": new_preparation_required, "is_active": new_is_active}
                changed_log = {k: v for k,v in updated_fields.items() if str(lt_data.get(k) or '') != str(v or '')}
                if not changed_log:
                    st.info("No changes detected.")
                    st.session_state.edit_lab_test_id = None; st.rerun()
                else:
                    try:
                        conn_update = db_manager.get_connection(); cursor = conn_update.cursor()
                        set_clause = ", ".join([f"{key} = ?" for key in changed_log.keys()]); values = list(changed_log.values()); values.append(lab_test_id)
                        cursor.execute(f"UPDATE lab_tests SET {set_clause} WHERE id = ?", tuple(values)); conn_update.commit(); conn_update.close()
                        log_activity(st.session_state.user['id'], 'update_lab_test', 'lab_test', lab_test_id, metadata={"updated_fields": list(changed_log.keys())})
                        st.success(f"Lab Test '{new_test_name}' updated successfully!"); st.session_state.edit_lab_test_id = None; st.rerun()
                    except Exception as e: st.error(f"Error updating lab test: {str(e)}")

def _confirm_and_action_lab_test(lab_test_id, is_currently_active):
    action_verb = "Deactivate" if is_currently_active else "Restore"; action_desc = "deactivating" if is_currently_active else "restoring"
    conn = db_manager.get_connection(); lt_name_series = pd.read_sql("SELECT test_name FROM lab_tests WHERE id = ?", conn, params=(lab_test_id,)); conn.close()
    if lt_name_series.empty:
        st.error("Lab Test not found or already deleted. Refreshing list.")
        st.session_state.action_lab_test_id = None; st.rerun(); return
    lt_name = lt_name_series.iloc[0]['test_name']
    st.subheader(f"{action_verb} Lab Test: {lt_name}")
    st.markdown(f"Are you sure you want to {action_verb.lower()} lab test **'{lt_name}'** (ID: {lab_test_id})?")
    col1, col2, _ = st.columns([1,1,3])
    with col1:
        if st.button(f"Yes, {action_verb}", key=f"confirm_action_lt_{lab_test_id}", type="primary"):
            try:
                conn_action = db_manager.get_connection(); cursor = conn_action.cursor(); new_status = 0 if is_currently_active else 1
                cursor.execute("UPDATE lab_tests SET is_active = ? WHERE id = ?", (new_status, lab_test_id)); conn_action.commit(); conn_action.close()
                log_activity(st.session_state.user['id'], f'{action_desc}_lab_test', 'lab_test', lab_test_id, metadata={"name": lt_name, "new_status": "active" if new_status else "inactive"})
                st.success(f"Lab Test '{lt_name}' successfully {action_desc}d."); st.session_state.action_lab_test_id = None; st.rerun()
            except Exception as e: st.error(f"Error {action_desc} lab test: {str(e)}")
    with col2:
        if st.button("Cancel", key=f"cancel_action_lt_{lab_test_id}", type="secondary"):
            st.session_state.action_lab_test_id = None; st.rerun()

def show_lab_tests_database():
    st.markdown('<div class="main-header"><h1>🔬 Lab Tests Database</h1></div>', unsafe_allow_html=True)
    user_type = st.session_state.user['user_type']

    if user_type == 'super_admin':
        # Initialize session state keys if they don't exist for safety
        if 'edit_lab_test_id' not in st.session_state:
            st.session_state.edit_lab_test_id = None
        if 'action_lab_test_id' not in st.session_state:
            st.session_state.action_lab_test_id = None
        # action_lab_test_current_status is set when action_lab_test_id is set

        # Logic to display tabs or specific forms based on session state
        if st.session_state.edit_lab_test_id is not None:
            _display_edit_lab_test_form(st.session_state.edit_lab_test_id)
        elif st.session_state.action_lab_test_id is not None:
            _confirm_and_action_lab_test(st.session_state.action_lab_test_id, st.session_state.get('action_lab_test_current_status', False))
        else:
            view_tab, add_tab = st.tabs(["View Lab Tests", "Add New Lab Test"])
            with view_tab:
                _display_lab_tests_view(is_super_admin=True)
            with add_tab:
                _display_add_lab_test_form()
    else: # Doctor or Assistant
        _display_lab_tests_view(is_super_admin=False)
# --- Lab Tests Database Management END ---

if __name__ == "__main__":
    main()
