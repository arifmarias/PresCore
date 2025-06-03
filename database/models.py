"""
MedScript Pro - Database Models and Schema Definitions
This file contains all the database table definitions and relationships for the medical prescription system.
"""

from config.database import execute_query, execute_transaction
import streamlit as st

# Database schema version
DATABASE_VERSION = 1

def create_all_tables():
    """
    Create all database tables with proper relationships and constraints
    
    Returns:
        bool: True if all tables created successfully, False otherwise
    """
    try:
        # List of all table creation queries
        table_creation_queries = [
            create_users_table(),
            create_patients_table(),
            create_patient_visits_table(),
            create_medications_table(),
            create_lab_tests_table(),
            create_prescriptions_table(),
            create_prescription_items_table(),
            create_prescription_lab_tests_table(),
            create_templates_table(),
            create_analytics_table()
        ]
        
        # Execute all table creation queries in a transaction
        queries_and_params = [(query, None) for query in table_creation_queries]
        
        # Add database version setting
        queries_and_params.append((f"PRAGMA user_version = {DATABASE_VERSION}", None))
        
        success = execute_transaction(queries_and_params)
        
        if success:
            st.success("All database tables created successfully!")
            create_indexes()
        else:
            st.error("Failed to create database tables")
        
        return success
        
    except Exception as e:
        st.error(f"Error creating database tables: {str(e)}")
        return False

def create_users_table() -> str:
    """Create users table for authentication and role management"""
    return """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        user_type TEXT NOT NULL CHECK (user_type IN ('super_admin', 'doctor', 'assistant')),
        medical_license TEXT,
        specialization TEXT,
        email TEXT,
        phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        last_login DATETIME,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until DATETIME
    )
    """

def create_patients_table() -> str:
    """Create patients table for patient information management"""
    return """
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
        phone TEXT,
        email TEXT,
        address TEXT,
        allergies TEXT,
        medical_conditions TEXT,
        emergency_contact TEXT,
        emergency_phone TEXT,
        insurance_info TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        is_active BOOLEAN DEFAULT 1,
        notes TEXT,
        blood_group TEXT,
        weight REAL,
        height REAL,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """

def create_patient_visits_table() -> str:
    """Create patient visits table for visit tracking"""
    return """
    CREATE TABLE IF NOT EXISTS patient_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        visit_date DATE NOT NULL,
        visit_time TIME,
        visit_type TEXT NOT NULL,
        current_problems TEXT,
        is_followup BOOLEAN DEFAULT 0,
        is_report_consultation BOOLEAN DEFAULT 0,
        vital_signs TEXT,
        blood_pressure TEXT,
        temperature REAL,
        pulse_rate INTEGER,
        respiratory_rate INTEGER,
        oxygen_saturation REAL,
        notes TEXT,
        created_by INTEGER NOT NULL,
        consultation_completed BOOLEAN DEFAULT 0,
        prescription_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users (id),
        FOREIGN KEY (prescription_id) REFERENCES prescriptions (id)
    )
    """

def create_medications_table() -> str:
    """Create medications table for drug database"""
    return """
    CREATE TABLE IF NOT EXISTS medications (
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
        precautions TEXT,
        dosage_guidelines TEXT,
        is_controlled BOOLEAN DEFAULT 0,
        is_favorite BOOLEAN DEFAULT 0,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        manufacturer TEXT,
        storage_conditions TEXT,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """

def create_lab_tests_table() -> str:
    """Create lab tests table for laboratory test database"""
    return """
    CREATE TABLE IF NOT EXISTS lab_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_name TEXT NOT NULL,
        test_code TEXT UNIQUE,
        test_category TEXT NOT NULL,
        normal_range TEXT,
        units TEXT,
        description TEXT,
        preparation_required TEXT,
        sample_type TEXT,
        test_method TEXT,
        turnaround_time TEXT,
        cost REAL,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """

def create_prescriptions_table() -> str:
    """Create prescriptions table for main prescription records"""
    return """
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_id TEXT UNIQUE NOT NULL,
        doctor_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        visit_id INTEGER,
        diagnosis TEXT,
        chief_complaint TEXT,
        notes TEXT,
        status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'Completed', 'Cancelled')),
        ai_interaction_analysis TEXT,
        follow_up_date DATE,
        follow_up_instructions TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        consultation_fee REAL,
        total_medications INTEGER DEFAULT 0,
        total_lab_tests INTEGER DEFAULT 0,
        FOREIGN KEY (doctor_id) REFERENCES users (id),
        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
        FOREIGN KEY (visit_id) REFERENCES patient_visits (id)
    )
    """

def create_prescription_items_table() -> str:
    """Create prescription items table for individual medications"""
    return """
    CREATE TABLE IF NOT EXISTS prescription_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_id INTEGER NOT NULL,
        medication_id INTEGER NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        duration TEXT NOT NULL,
        quantity TEXT,
        refills INTEGER DEFAULT 0,
        instructions TEXT,
        route_of_administration TEXT,
        start_date DATE,
        end_date DATE,
        is_substitutable BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prescription_id) REFERENCES prescriptions (id) ON DELETE CASCADE,
        FOREIGN KEY (medication_id) REFERENCES medications (id)
    )
    """

def create_prescription_lab_tests_table() -> str:
    """Create prescription lab tests table for lab tests ordered with prescriptions"""
    return """
    CREATE TABLE IF NOT EXISTS prescription_lab_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_id INTEGER NOT NULL,
        lab_test_id INTEGER NOT NULL,
        instructions TEXT,
        urgency TEXT DEFAULT 'Routine' CHECK (urgency IN ('Routine', 'Urgent', 'STAT')),
        sample_collection_date DATE,
        fasting_required BOOLEAN DEFAULT 0,
        special_instructions TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prescription_id) REFERENCES prescriptions (id) ON DELETE CASCADE,
        FOREIGN KEY (lab_test_id) REFERENCES lab_tests (id)
    )
    """

def create_templates_table() -> str:
    """Create templates table for prescription templates"""
    return """
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        template_data TEXT NOT NULL,
        medications_data TEXT,
        lab_tests_data TEXT,
        diagnosis_template TEXT,
        instructions_template TEXT,
        is_active BOOLEAN DEFAULT 1,
        usage_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """

def create_analytics_table() -> str:
    """Create analytics table for user activity logging"""
    return """
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        entity_type TEXT,
        entity_id INTEGER,
        metadata TEXT,
        ip_address TEXT,
        user_agent TEXT,
        session_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        execution_time_ms INTEGER,
        success BOOLEAN DEFAULT 1,
        error_message TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """

def create_indexes():
    """Create database indexes for better performance"""
    try:
        index_queries = [
            # Users table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)",
            "CREATE INDEX IF NOT EXISTS idx_users_user_type ON users (user_type)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active)",
            
            # Patients table indexes
            "CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_patients_name ON patients (first_name, last_name)",
            "CREATE INDEX IF NOT EXISTS idx_patients_created_by ON patients (created_by)",
            "CREATE INDEX IF NOT EXISTS idx_patients_is_active ON patients (is_active)",
            
            # Patient visits table indexes
            "CREATE INDEX IF NOT EXISTS idx_visits_patient_id ON patient_visits (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_visits_visit_date ON patient_visits (visit_date)",
            "CREATE INDEX IF NOT EXISTS idx_visits_created_by ON patient_visits (created_by)",
            "CREATE INDEX IF NOT EXISTS idx_visits_consultation_completed ON patient_visits (consultation_completed)",
            
            # Medications table indexes
            "CREATE INDEX IF NOT EXISTS idx_medications_name ON medications (name)",
            "CREATE INDEX IF NOT EXISTS idx_medications_generic_name ON medications (generic_name)",
            "CREATE INDEX IF NOT EXISTS idx_medications_drug_class ON medications (drug_class)",
            "CREATE INDEX IF NOT EXISTS idx_medications_is_active ON medications (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_medications_is_favorite ON medications (is_favorite)",
            
            # Lab tests table indexes
            "CREATE INDEX IF NOT EXISTS idx_lab_tests_name ON lab_tests (test_name)",
            "CREATE INDEX IF NOT EXISTS idx_lab_tests_code ON lab_tests (test_code)",
            "CREATE INDEX IF NOT EXISTS idx_lab_tests_category ON lab_tests (test_category)",
            "CREATE INDEX IF NOT EXISTS idx_lab_tests_is_active ON lab_tests (is_active)",
            
            # Prescriptions table indexes
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_prescription_id ON prescriptions (prescription_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_doctor_id ON prescriptions (doctor_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_id ON prescriptions (patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_visit_id ON prescriptions (visit_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_status ON prescriptions (status)",
            "CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions (created_at)",
            
            # Prescription items table indexes
            "CREATE INDEX IF NOT EXISTS idx_prescription_items_prescription_id ON prescription_items (prescription_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescription_items_medication_id ON prescription_items (medication_id)",
            
            # Prescription lab tests table indexes
            "CREATE INDEX IF NOT EXISTS idx_prescription_lab_tests_prescription_id ON prescription_lab_tests (prescription_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescription_lab_tests_lab_test_id ON prescription_lab_tests (lab_test_id)",
            "CREATE INDEX IF NOT EXISTS idx_prescription_lab_tests_urgency ON prescription_lab_tests (urgency)",
            
            # Templates table indexes
            "CREATE INDEX IF NOT EXISTS idx_templates_doctor_id ON templates (doctor_id)",
            "CREATE INDEX IF NOT EXISTS idx_templates_category ON templates (category)",
            "CREATE INDEX IF NOT EXISTS idx_templates_is_active ON templates (is_active)",
            
            # Analytics table indexes
            "CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_action_type ON analytics (action_type)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_entity_type ON analytics (entity_type)"
        ]
        
        # Execute all index creation queries
        queries_and_params = [(query, None) for query in index_queries]
        success = execute_transaction(queries_and_params)
        
        if success:
            st.success("Database indexes created successfully!")
        else:
            st.error("Failed to create some database indexes")
        
        return success
        
    except Exception as e:
        st.error(f"Error creating database indexes: {str(e)}")
        return False

def create_triggers():
    """Create database triggers for automatic updates"""
    try:
        trigger_queries = [
            # Update timestamp triggers for users table
            """
            CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
            AFTER UPDATE ON users
            BEGIN
                UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for patients table
            """
            CREATE TRIGGER IF NOT EXISTS update_patients_timestamp 
            AFTER UPDATE ON patients
            BEGIN
                UPDATE patients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for patient_visits table
            """
            CREATE TRIGGER IF NOT EXISTS update_visits_timestamp 
            AFTER UPDATE ON patient_visits
            BEGIN
                UPDATE patient_visits SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for medications table
            """
            CREATE TRIGGER IF NOT EXISTS update_medications_timestamp 
            AFTER UPDATE ON medications
            BEGIN
                UPDATE medications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for lab_tests table
            """
            CREATE TRIGGER IF NOT EXISTS update_lab_tests_timestamp 
            AFTER UPDATE ON lab_tests
            BEGIN
                UPDATE lab_tests SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for prescriptions table
            """
            CREATE TRIGGER IF NOT EXISTS update_prescriptions_timestamp 
            AFTER UPDATE ON prescriptions
            BEGIN
                UPDATE prescriptions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update timestamp triggers for templates table
            """
            CREATE TRIGGER IF NOT EXISTS update_templates_timestamp 
            AFTER UPDATE ON templates
            BEGIN
                UPDATE templates SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """,
            
            # Update medication count in prescriptions when items are added
            """
            CREATE TRIGGER IF NOT EXISTS update_prescription_med_count_insert
            AFTER INSERT ON prescription_items
            BEGIN
                UPDATE prescriptions 
                SET total_medications = (
                    SELECT COUNT(*) FROM prescription_items 
                    WHERE prescription_id = NEW.prescription_id
                )
                WHERE id = NEW.prescription_id;
            END
            """,
            
            # Update medication count in prescriptions when items are deleted
            """
            CREATE TRIGGER IF NOT EXISTS update_prescription_med_count_delete
            AFTER DELETE ON prescription_items
            BEGIN
                UPDATE prescriptions 
                SET total_medications = (
                    SELECT COUNT(*) FROM prescription_items 
                    WHERE prescription_id = OLD.prescription_id
                )
                WHERE id = OLD.prescription_id;
            END
            """,
            
            # Update lab test count in prescriptions when tests are added
            """
            CREATE TRIGGER IF NOT EXISTS update_prescription_lab_count_insert
            AFTER INSERT ON prescription_lab_tests
            BEGIN
                UPDATE prescriptions 
                SET total_lab_tests = (
                    SELECT COUNT(*) FROM prescription_lab_tests 
                    WHERE prescription_id = NEW.prescription_id
                )
                WHERE id = NEW.prescription_id;
            END
            """,
            
            # Update lab test count in prescriptions when tests are deleted
            """
            CREATE TRIGGER IF NOT EXISTS update_prescription_lab_count_delete
            AFTER DELETE ON prescription_lab_tests
            BEGIN
                UPDATE prescriptions 
                SET total_lab_tests = (
                    SELECT COUNT(*) FROM prescription_lab_tests 
                    WHERE prescription_id = OLD.prescription_id
                )
                WHERE id = OLD.prescription_id;
            END
            """,
            
            # Update template usage count when used
            """
            CREATE TRIGGER IF NOT EXISTS update_template_usage
            AFTER INSERT ON prescriptions
            WHEN NEW.diagnosis LIKE '%template%'
            BEGIN
                UPDATE templates 
                SET usage_count = usage_count + 1 
                WHERE doctor_id = NEW.doctor_id;
            END
            """
        ]
        
        # Execute all trigger creation queries
        queries_and_params = [(query, None) for query in trigger_queries]
        success = execute_transaction(queries_and_params)
        
        if success:
            st.success("Database triggers created successfully!")
        else:
            st.error("Failed to create some database triggers")
        
        return success
        
    except Exception as e:
        st.error(f"Error creating database triggers: {str(e)}")
        return False

def drop_all_tables():
    """Drop all tables (for reset/cleanup purposes)"""
    try:
        drop_queries = [
            "DROP TABLE IF EXISTS analytics",
            "DROP TABLE IF EXISTS templates",
            "DROP TABLE IF EXISTS prescription_lab_tests",
            "DROP TABLE IF EXISTS prescription_items",
            "DROP TABLE IF EXISTS prescriptions",
            "DROP TABLE IF EXISTS lab_tests",
            "DROP TABLE IF EXISTS medications",
            "DROP TABLE IF EXISTS patient_visits",
            "DROP TABLE IF EXISTS patients",
            "DROP TABLE IF EXISTS users"
        ]
        
        queries_and_params = [(query, None) for query in drop_queries]
        success = execute_transaction(queries_and_params)
        
        if success:
            st.success("All tables dropped successfully!")
        else:
            st.error("Failed to drop some tables")
        
        return success
        
    except Exception as e:
        st.error(f"Error dropping tables: {str(e)}")
        return False

def get_database_schema() -> dict:
    """Get the complete database schema information"""
    try:
        schema = {}
        
        # Get all tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables = execute_query(tables_query, fetch='all')
        
        for table in tables:
            table_name = table['name']
            
            # Get table info
            table_info_query = f"PRAGMA table_info({table_name})"
            columns = execute_query(table_info_query, fetch='all')
            
            # Get foreign keys
            fk_query = f"PRAGMA foreign_key_list({table_name})"
            foreign_keys = execute_query(fk_query, fetch='all')
            
            # Get indexes
            index_query = f"PRAGMA index_list({table_name})"
            indexes = execute_query(index_query, fetch='all')
            
            schema[table_name] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        
        return schema
        
    except Exception as e:
        st.error(f"Error getting database schema: {str(e)}")
        return {}

def validate_database_integrity() -> bool:
    """Validate database integrity and relationships"""
    try:
        # Check foreign key constraints
        integrity_check = execute_query("PRAGMA foreign_key_check", fetch='all')
        
        if integrity_check:
            st.error(f"Foreign key constraint violations found: {integrity_check}")
            return False
        
        # Check database integrity
        integrity_result = execute_query("PRAGMA integrity_check", fetch='one')
        
        if integrity_result and integrity_result.get('integrity_check') != 'ok':
            st.error(f"Database integrity check failed: {integrity_result}")
            return False
        
        st.success("Database integrity validation passed!")
        return True
        
    except Exception as e:
        st.error(f"Error validating database integrity: {str(e)}")
        return False