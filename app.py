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
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Header
        pdf.cell(0, 10, 'MEDICAL PRESCRIPTION', 0, 1, 'C')
        pdf.ln(5)
        
        # Doctor information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"Dr. {prescription_data['doctor_name']}", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Specialization: {prescription_data['specialization']}", 0, 1)
        pdf.cell(0, 6, f"License: {prescription_data['medical_license']}", 0, 1)
        pdf.ln(5)
        
        # Prescription details
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, f"Prescription ID: {prescription_data['prescription_id']}", 0, 1)
        pdf.cell(0, 6, f"Date: {prescription_data['date']}", 0, 1)
        pdf.ln(3)
        
        # Patient information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'PATIENT INFORMATION', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Name: {prescription_data['patient_name']}", 0, 1)
        pdf.cell(0, 6, f"Patient ID: {prescription_data['patient_id']}", 0, 1)
        pdf.cell(0, 6, f"DOB: {prescription_data['dob']}", 0, 1)
        pdf.ln(5)
        
        # Diagnosis
        if prescription_data.get('diagnosis'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'DIAGNOSIS', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, prescription_data['diagnosis'])
            pdf.ln(3)
        
        # Medications
        if prescription_data.get('medications'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'MEDICATIONS', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for i, med in enumerate(prescription_data['medications'], 1):
                pdf.cell(0, 6, f"{i}. {med['name']}", 0, 1)
                pdf.cell(10, 6, '', 0, 0)  # Indent
                pdf.cell(0, 6, f"   Dosage: {med['dosage']}", 0, 1)
                pdf.cell(10, 6, '', 0, 0)  # Indent
                pdf.cell(0, 6, f"   Frequency: {med['frequency']}", 0, 1)
                pdf.cell(10, 6, '', 0, 0)  # Indent
                pdf.cell(0, 6, f"   Duration: {med['duration']}", 0, 1)
                if med.get('instructions'):
                    pdf.cell(10, 6, '', 0, 0)  # Indent
                    pdf.multi_cell(0, 6, f"   Instructions: {med['instructions']}")
                pdf.ln(2)
        
        # Lab tests
        if prescription_data.get('lab_tests'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'RECOMMENDED LAB TESTS', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for i, test in enumerate(prescription_data['lab_tests'], 1):
                pdf.cell(0, 6, f"{i}. {test['name']} ({test['urgency']})", 0, 1)
                if test.get('instructions'):
                    pdf.cell(10, 6, '', 0, 0)  # Indent
                    pdf.multi_cell(0, 6, f"   Instructions: {test['instructions']}")
        
        # Notes
        if prescription_data.get('notes'):
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'NOTES', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, prescription_data['notes'])
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 6, f"Generated by MedScript Pro on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        
        return pdf.output(dest='S').encode('latin-1')

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
        
        selected_page = st.radio("Navigation", list(pages.keys()))
        st.session_state.current_page = pages[selected_page]
        
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
        conn = db_manager.get_connection()
        users_df = pd.read_sql("""
            SELECT id, username, full_name, user_type, medical_license, specialization, 
                   email, phone, created_at, is_active
            FROM users
            ORDER BY created_at DESC
        """, conn)
        conn.close()
        
        if not users_df.empty:
            # Search and filter
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("Search users...")
            with col2:
                user_type_filter = st.selectbox("Filter by role", ["All", "super_admin", "doctor", "assistant"])
            
            # Apply filters
            filtered_df = users_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['full_name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['username'].str.contains(search_term, case=False, na=False)
                ]
            
            if user_type_filter != "All":
                filtered_df = filtered_df[filtered_df['user_type'] == user_type_filter]
            
            st.dataframe(filtered_df, use_container_width=True)
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
    
    tab1, tab2 = st.tabs(["View Patients", "Add Patient"])
    
    with tab1:
        conn = db_manager.get_connection()
        patients_df = pd.read_sql("""
            SELECT patient_id, first_name, last_name, date_of_birth, gender, phone, 
                   allergies, medical_conditions, created_at
            FROM patients
            WHERE is_active = 1
            ORDER BY created_at DESC
        """, conn)
        conn.close()
        
        if not patients_df.empty:
            # Search functionality
            search_term = st.text_input("Search patients by name or ID...")
            
            if search_term:
                patients_df = patients_df[
                    patients_df['patient_id'].str.contains(search_term, case=False, na=False) |
                    patients_df['first_name'].str.contains(search_term, case=False, na=False) |
                    patients_df['last_name'].str.contains(search_term, case=False, na=False)
                ]
            
            # Display patients with actions
            for _, patient in patients_df.iterrows():
                with st.expander(f"👤 {patient['first_name']} {patient['last_name']} ({patient['patient_id']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**DOB:** {patient['date_of_birth']}")
                        st.write(f"**Gender:** {patient['gender']}")
                        st.write(f"**Phone:** {patient['phone']}")
                    
                    with col2:
                        st.write(f"**Allergies:** {patient['allergies'] or 'None known'}")
                        st.write(f"**Medical Conditions:** {patient['medical_conditions'] or 'None'}")
                    
                    # Show prescription history if user is doctor or super admin
                    if st.session_state.user['user_type'] in ['doctor', 'super_admin']:
                        if st.button(f"View Prescription History", key=f"history_{patient['patient_id']}"):
                            show_patient_prescription_history(patient['patient_id'])
        else:
            st.info("No patients found")
    
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

def show_patient_prescription_history(patient_id):
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
        st.subheader(f"Prescription History for {patient_id}")
        
        for _, prescription in prescriptions.iterrows():
            with st.expander(f"📋 {prescription['prescription_id']} - {prescription['created_at'][:10]}"):
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
    else:
        st.info("No prescription history found for this patient")
    
    conn.close()

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
                        st.session_state.selected_patient = {
                            'visit_id': patient['visit_id'],
                            'patient_db_id': patient['patient_db_id'],
                            'patient_id': patient['patient_id'],
                            'name': f"{patient['first_name']} {patient['last_name']}",
                            'age': calculate_age(patient['date_of_birth']),
                            'gender': patient['gender'],
                            'allergies': patient['allergies'] or 'None known',
                            'medical_conditions': patient['medical_conditions'] or 'None',
                            'current_problems': patient['current_problems']
                        }
                        st.session_state.current_page = 'create_prescription'
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
    if 'selected_patient' in st.session_state:
        patient_info = st.session_state.selected_patient
        st.success(f"Creating prescription for: {patient_info['name']} ({patient_info['patient_id']})")
    else:
        # Manual patient selection
        conn = db_manager.get_connection()
        patients = pd.read_sql("SELECT id, patient_id, first_name, last_name FROM patients WHERE is_active = 1", conn)
        conn.close()
        
        if patients.empty:
            st.error("No patients available. Please add patients first.")
            return
        
        patient_options = {f"{row['first_name']} {row['last_name']} ({row['patient_id']})": row['id'] for _, row in patients.iterrows()}
        
        with st.form("visit_registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_patient = st.selectbox("Select Patient*", list(patient_options.keys()))
                visit_date = st.date_input("Visit Date*", value=datetime.date.today())
                visit_type = st.selectbox("Visit Type*", ["Consultation", "Follow-up", "Emergency", "Routine Check-up"])
                current_problems = st.text_area("Current Problems/Complaints*")
            
            with col2:
                is_followup = st.checkbox("Follow-up Visit")
                is_report_consultation = st.checkbox("Report Consultation")
                vital_signs = st.text_area("Vital Signs", placeholder="BP, HR, Temp, etc.")
                notes = st.text_area("Additional Notes")
            
            submit_button = st.form_submit_button("Register Visit")
            
            if submit_button:
                if selected_patient and visit_date and visit_type and current_problems:
                    try:
                        patient_id = patient_options[selected_patient]
                        
                        conn = db_manager.get_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            INSERT INTO patient_visits (patient_id, visit_date, visit_type, current_problems,
                                                       is_followup, is_report_consultation, vital_signs, notes, created_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (patient_id, visit_date.isoformat(), visit_type, current_problems,
                              is_followup, is_report_consultation, vital_signs, notes, st.session_state.user['id']))
                        
                        conn.commit()
                        conn.close()
                        
                        log_activity(st.session_state.user['id'], 'create_visit', 'visit')
                        st.success("Visit registered successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error registering visit: {str(e)}")
                else:
                    st.error("Please fill in all required fields!")
    
    with tab2:
        st.subheader("Visit History")
        
        conn = db_manager.get_connection()
        visits_df = pd.read_sql("""
            SELECT v.id, p.patient_id, p.first_name, p.last_name, v.visit_date, v.visit_type,
                   v.current_problems, v.consultation_completed, v.created_at
            FROM patient_visits v
            JOIN patients p ON v.patient_id = p.id
            WHERE v.created_by = ?
            ORDER BY v.visit_date DESC, v.created_at DESC
        """, conn, params=[st.session_state.user['id']])
        conn.close()
        
        if not visits_df.empty:
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", value=datetime.date.today() - datetime.timedelta(days=30))
            with col2:
                end_date = st.date_input("To Date", value=datetime.date.today())
            
            # Filter by date range
            filtered_visits = visits_df[
                (pd.to_datetime(visits_df['visit_date']).dt.date >= start_date) &
                (pd.to_datetime(visits_df['visit_date']).dt.date <= end_date)
            ]
            
            # Display visits
            for _, visit in filtered_visits.iterrows():
                status_icon = "✅" if visit['consultation_completed'] else "⏳"
                
                with st.expander(f"{status_icon} {visit['first_name']} {visit['last_name']} - {visit['visit_date']} ({visit['visit_type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Patient ID:** {visit['patient_id']}")
                        st.write(f"**Visit Type:** {visit['visit_type']}")
                        st.write(f"**Problems:** {visit['current_problems']}")
                    
                    with col2:
                        st.write(f"**Status:** {'Completed' if visit['consultation_completed'] else 'Waiting'}")
                        st.write(f"**Registered:** {visit['created_at'][:16]}")
        else:
            st.info("No visits registered yet")

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
            fig_bar = px.bar(top_medications, x='name', y='count',
                            title='Top 10 Most Prescribed Medications',
                            labels={'name': 'Medication', 'count': 'Times Prescribed'})
            fig_bar.update_xaxis(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
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
            SELECT action_type, entity_type, timestamp
            FROM analytics
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, conn, params=[st.session_state.user['id']])
    elif user_type == 'doctor':
        recent_activity = pd.read_sql("""
            SELECT action_type, entity_type, timestamp
            FROM analytics
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, conn, params=[st.session_state.user['id']])
    else:  # super_admin
        recent_activity = pd.read_sql("""
            SELECT a.action_type, a.entity_type, a.timestamp, u.full_name
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
        elif page == 'medications':
            show_medication_database()
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

if __name__ == "__main__":
    main()