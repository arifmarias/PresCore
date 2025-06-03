"""
MedScript Pro - Application Settings and Constants
This file contains all configuration settings, constants, and application parameters.
"""

import os
from datetime import datetime

# Application Information
APP_NAME = "MedScript Pro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Medical Prescription Management System"
APP_AUTHOR = "MedScript Development Team"

# Database Configuration
DATABASE_NAME = "medscript_pro.db"
DATABASE_PATH = os.path.join(os.getcwd(), DATABASE_NAME)

# User Roles
USER_ROLES = {
    'SUPER_ADMIN': 'super_admin',
    'DOCTOR': 'doctor',
    'ASSISTANT': 'assistant'
}

# User Types (for database storage)
USER_TYPES = ['super_admin', 'doctor', 'assistant']

# Default Admin Credentials
DEFAULT_ADMIN = {
    'username': 'superadmin',
    'password': 'admin123',
    'full_name': 'System Administrator',
    'user_type': 'super_admin',
    'email': 'admin@medscript.com',
    'phone': '+1234567890'
}

# Demo User Credentials
DEMO_USERS = [
    {
        'username': 'doctor1',
        'password': 'doctor123',
        'full_name': 'Dr. Sarah Johnson',
        'user_type': 'doctor',
        'medical_license': 'MD-2023-001',
        'specialization': 'Internal Medicine',
        'email': 'dr.johnson@medscript.com',
        'phone': '+1234567891'
    },
    {
        'username': 'assistant1',
        'password': 'assistant123',
        'full_name': 'Emily Davis',
        'user_type': 'assistant',
        'email': 'emily.davis@medscript.com',
        'phone': '+1234567892'
    }
]

# OpenRouter API Configuration
OPENROUTER_CONFIG = {
    'BASE_URL': 'https://openrouter.ai/api/v1/chat/completions',
    'MODEL': 'anthropic/claude-3-haiku',
    'MAX_TOKENS': 1000,
    'TEMPERATURE': 0.1,
    'TIMEOUT': 30,
    'RATE_LIMIT_DELAY': 1  # seconds between requests
}

# AI Analysis Configuration
AI_ANALYSIS_CONFIG = {
    'ENABLE_AI': True,
    'FALLBACK_ENABLED': True,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 2  # seconds
}

# Prescription Configuration
PRESCRIPTION_CONFIG = {
    'ID_PREFIX': 'RX',
    'ID_FORMAT': 'RX-{date}-{sequence:06d}',  # RX-YYYYMMDD-000001
    'PDF_FILENAME_FORMAT': 'Prescription_{prescription_id}_{patient_name}.pdf',
    'MAX_MEDICATIONS_PER_PRESCRIPTION': 20,
    'MAX_LAB_TESTS_PER_PRESCRIPTION': 15
}

# Patient Configuration
PATIENT_CONFIG = {
    'ID_PREFIX': 'PT',
    'ID_FORMAT': 'PT-{date}-{sequence:06d}',  # PT-YYYYMMDD-000001
    'AGE_CALCULATION_BASE': datetime.now().year
}

# Visit Types
VISIT_TYPES = [
    'Initial Consultation',
    'Follow-up',
    'Emergency',
    'Routine Check-up',
    'Vaccination',
    'Report Consultation',
    'Teleconsultation'
]

# Gender Options
GENDER_OPTIONS = ['Male', 'Female', 'Other']

# Medication Configuration
MEDICATION_CONFIG = {
    'DOSAGE_FORMS': [
        'Tablet', 'Capsule', 'Syrup', 'Injection', 'Cream', 'Ointment',
        'Drops', 'Inhaler', 'Patch', 'Suspension', 'Solution', 'Gel'
    ],
    'FREQUENCIES': [
        'Once daily', 'Twice daily', 'Three times daily', 'Four times daily',
        'Every 4 hours', 'Every 6 hours', 'Every 8 hours', 'Every 12 hours',
        'As needed', 'Before meals', 'After meals', 'At bedtime'
    ],
    'DURATIONS': [
        '3 days', '5 days', '7 days', '10 days', '14 days', '21 days',
        '1 month', '2 months', '3 months', '6 months', 'Ongoing', 'As directed'
    ]
}

# Lab Test Configuration
LAB_TEST_CONFIG = {
    'CATEGORIES': [
        'Hematology', 'Clinical Chemistry', 'Endocrinology', 'Immunology',
        'Microbiology', 'Pathology', 'Radiology', 'Cardiology', 'Pulmonology'
    ],
    'URGENCY_LEVELS': ['Routine', 'Urgent', 'STAT'],
    'SAMPLE_TYPES': [
        'Blood', 'Urine', 'Stool', 'Sputum', 'CSF', 'Tissue', 'Swab'
    ]
}

# Template Configuration
TEMPLATE_CONFIG = {
    'CATEGORIES': [
        'General Medicine', 'Cardiology', 'Endocrinology', 'Gastroenterology',
        'Pulmonology', 'Neurology', 'Psychiatry', 'Orthopedics', 'Dermatology',
        'Pediatrics', 'Geriatrics', 'Emergency', 'Preventive Care'
    ]
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'DEFAULT_DAYS_RANGE': 30,
    'MAX_DAYS_RANGE': 365,
    'CHART_COLORS': [
        '#0096C7', '#48CAE4', '#90E0EF', '#ADE8F4', '#CAF0F8',
        '#28A745', '#FFC107', '#DC3545', '#6F42C1', '#FD7E14'
    ]
}

# PDF Configuration
PDF_CONFIG = {
    'FONT_SIZE': {
        'TITLE': 16,
        'HEADER': 12,
        'NORMAL': 10,
        'SMALL': 8
    },
    'MARGINS': {
        'TOP': 20,
        'LEFT': 20,
        'RIGHT': 20,
        'BOTTOM': 20
    },
    'LINE_HEIGHT': 5,
    'PAGE_SIZE': 'A4'
}

# Status Options
STATUS_OPTIONS = {
    'PRESCRIPTION': ['Active', 'Completed', 'Cancelled'],
    'PATIENT': ['Active', 'Inactive'],
    'USER': ['Active', 'Inactive'],
    'VISIT': ['Scheduled', 'In Progress', 'Completed', 'Cancelled']
}

# Drug Classes (for medication database)
DRUG_CLASSES = [
    'Analgesics', 'Antibiotics', 'Antivirals', 'Antifungals', 'Anti-inflammatory',
    'Antihypertensives', 'Antidiabetics', 'Antidepressants', 'Antihistamines',
    'Bronchodilators', 'Corticosteroids', 'Diuretics', 'Hormones', 'Vaccines',
    'Vitamins & Supplements', 'Gastrointestinal', 'Cardiovascular', 'Neurological'
]

# Medical Conditions (common conditions for patient profiles)
COMMON_CONDITIONS = [
    'Hypertension', 'Diabetes Mellitus', 'Asthma', 'COPD', 'Heart Disease',
    'Kidney Disease', 'Liver Disease', 'Thyroid Disorders', 'Arthritis',
    'Depression', 'Anxiety', 'Allergies', 'Migraine', 'Osteoporosis'
]

# Common Allergies
COMMON_ALLERGIES = [
    'Penicillin', 'Sulfa drugs', 'Aspirin', 'NSAIDs', 'Codeine',
    'Latex', 'Iodine', 'Peanuts', 'Shellfish', 'Eggs', 'Milk', 'Soy'
]

# Validation Rules
VALIDATION_RULES = {
    'USERNAME': {
        'MIN_LENGTH': 3,
        'MAX_LENGTH': 50,
        'PATTERN': r'^[a-zA-Z0-9_]+$'
    },
    'PASSWORD': {
        'MIN_LENGTH': 6,
        'MAX_LENGTH': 100
    },
    'PHONE': {
        'PATTERN': r'^\+?[1-9]\d{1,14}$'
    },
    'EMAIL': {
        'PATTERN': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'MEDICAL_LICENSE': {
        'PATTERN': r'^[A-Z]{2}-\d{4}-\d{3}$'  # MD-2023-001
    }
}

# Session Configuration
SESSION_CONFIG = {
    'TIMEOUT_MINUTES': 60,
    'MAX_FAILED_ATTEMPTS': 5,
    'LOCKOUT_DURATION_MINUTES': 15
}

# File Upload Configuration
UPLOAD_CONFIG = {
    'MAX_FILE_SIZE_MB': 10,
    'ALLOWED_EXTENSIONS': ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'],
    'UPLOAD_DIRECTORY': 'uploads'
}

# Pagination Configuration
PAGINATION_CONFIG = {
    'DEFAULT_PAGE_SIZE': 25,
    'MAX_PAGE_SIZE': 100,
    'PAGE_SIZE_OPTIONS': [10, 25, 50, 100]
}

# Error Messages
ERROR_MESSAGES = {
    'LOGIN_FAILED': 'Invalid username or password',
    'ACCESS_DENIED': 'You do not have permission to access this page',
    'SESSION_EXPIRED': 'Your session has expired. Please log in again.',
    'DATABASE_ERROR': 'Database operation failed. Please try again.',
    'API_ERROR': 'External service temporarily unavailable',
    'VALIDATION_ERROR': 'Please check your input and try again',
    'FILE_UPLOAD_ERROR': 'File upload failed. Please check file size and format.'
}

# Success Messages
SUCCESS_MESSAGES = {
    'LOGIN_SUCCESS': 'Welcome to MedScript Pro!',
    'LOGOUT_SUCCESS': 'You have been logged out successfully',
    'DATA_SAVED': 'Data saved successfully',
    'DATA_UPDATED': 'Data updated successfully',
    'DATA_DELETED': 'Data deleted successfully',
    'PRESCRIPTION_CREATED': 'Prescription created successfully',
    'PDF_GENERATED': 'PDF generated successfully'
}

# Date and Time Formats
DATE_FORMATS = {
    'DISPLAY': '%B %d, %Y',  # January 01, 2024
    'INPUT': '%Y-%m-%d',     # 2024-01-01
    'FILENAME': '%Y%m%d',    # 20240101
    'TIMESTAMP': '%Y-%m-%d %H:%M:%S'  # 2024-01-01 12:30:45
}

# Chart Configuration
CHART_CONFIG = {
    'HEIGHT': 400,
    'COLORS': {
        'PRIMARY': '#0096C7',
        'SECONDARY': '#48CAE4',
        'SUCCESS': '#28A745',
        'WARNING': '#FFC107',
        'DANGER': '#DC3545'
    },
    'FONTS': {
        'FAMILY': 'Arial, sans-serif',
        'SIZE': 12
    }
}

# Application URLs
APP_URLS = {
    'SUPPORT_EMAIL': 'support@medscript.com',
    'DOCUMENTATION': 'https://docs.medscript.com',
    'TERMS_OF_SERVICE': 'https://medscript.com/terms',
    'PRIVACY_POLICY': 'https://medscript.com/privacy'
}

# Feature Flags
FEATURE_FLAGS = {
    'ENABLE_AI_ANALYSIS': True,
    'ENABLE_PDF_GENERATION': True,
    'ENABLE_QR_CODES': True,
    'ENABLE_ANALYTICS': True,
    'ENABLE_TEMPLATES': True,
    'ENABLE_NOTIFICATIONS': False,  # Future feature
    'ENABLE_AUDIT_LOG': True,
    'ENABLE_BACKUP': False  # Future feature
}