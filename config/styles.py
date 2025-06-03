"""
MedScript Pro - CSS Styles and Theming
This file contains all the CSS styling for the professional medical interface.
"""

# Main CSS Styles for the application
MAIN_CSS = """
<style>
    /* CSS Variables for consistent theming */
    :root {
        --primary-blue: #0096C7;
        --light-blue: #48CAE4;
        --darker-blue: #0077A3;
        --success-green: #28A745;
        --warning-orange: #FFC107;
        --error-red: #DC3545;
        --info-cyan: #17A2B8;
        --light-gray: #F8F9FA;
        --medium-gray: #6C757D;
        --dark-gray: #343A40;
        --form-bg: #0c2733;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --border-radius: 10px;
        --transition: all 0.3s ease;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main application styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, var(--primary-blue), var(--light-blue));
        padding: 1.5rem;
        border-radius: var(--border-radius);
        color: white;
        text-align: center;
        box-shadow: var(--card-shadow);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="medical" patternUnits="userSpaceOnUse" width="20" height="20"><path d="M10 2v6h6v4h-6v6h-4v-6H0V8h6V2z" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23medical)"/></svg>') repeat;
        opacity: 0.1;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Welcome message styling */
    .welcome-message {
        background: linear-gradient(45deg, var(--success-green), #20C997);
        color: white;
        padding: 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1.5rem;
        box-shadow: var(--card-shadow);
        text-align: center;
        font-weight: 600;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary-blue);
        transition: var(--transition);
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Patient status cards */
    .patient-completed {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border-left: 4px solid var(--success-green);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        transition: var(--transition);
    }
    
    .patient-completed:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(40, 167, 69, 0.2);
    }
    
    .patient-waiting {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b3 100%);
        border-left: 4px solid var(--warning-orange);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        transition: var(--transition);
    }
    
    .patient-waiting:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 193, 7, 0.2);
    }
    
    /* Status indicators */
    .status-completed {
        color: var(--success-green);
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .status-waiting {
        color: var(--warning-orange);
        font-weight: bold;  
        font-size: 1.1rem;
    }
    
    .status-emergency {
        color: var(--error-red);
        font-weight: bold;
        font-size: 1.1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-blue), var(--light-blue));
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: var(--transition);
        box-shadow: var(--card-shadow);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, var(--darker-blue), var(--primary-blue));
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 150, 199, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Success button */
    .success-button > button {
        background: linear-gradient(45deg, var(--success-green), #20C997) !important;
    }
    
    .success-button > button:hover {
        background: linear-gradient(45deg, #218838, var(--success-green)) !important;
        box-shadow: 0 6px 12px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Warning button */
    .warning-button > button {
        background: linear-gradient(45deg, var(--warning-orange), #FFB300) !important;
        color: var(--dark-gray) !important;
    }
    
    .warning-button > button:hover {
        background: linear-gradient(45deg, #E0A800, var(--warning-orange)) !important;
        box-shadow: 0 6px 12px rgba(255, 193, 7, 0.3) !important;
    }
    
    /* Danger button */
    .danger-button > button {
        background: linear-gradient(45deg, var(--error-red), #E74C3C) !important;
    }
    
    .danger-button > button:hover {
        background: linear-gradient(45deg, #C82333, var(--error-red)) !important;
        box-shadow: 0 6px 12px rgba(220, 53, 69, 0.3) !important;
    }
    
    /* Form styling */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        border: 1px solid #E9ECEF;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        border: 2px solid #E9ECEF;
        border-radius: 8px;
        padding: 0.75rem;
        transition: var(--transition);
        background: #FAFAFA;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 3px rgba(0, 150, 199, 0.1);
        background: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-blue) 0%, var(--darker-blue) 100%);
    }
    
    .css-1d391kg .css-1v3fvcr {
        color: white;
    }
    
    /* Metric styling */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-blue);
        transition: var(--transition);
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Alert styling */
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-green);
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--warning-orange);
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    
    .alert-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f1c0c4 100%);
        color: #721c24;
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-red);
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    
    .alert-info {
        background: linear-gradient(135deg, #cce7ff 0%, #b3d9ff 100%);
        color: #004085;
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--info-cyan);
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    
    /* Table styling */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: var(--border-radius);
        padding: 0.5rem;
        box-shadow: var(--card-shadow);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--medium-gray);
        padding: 0.75rem 1.5rem;
        transition: var(--transition);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, var(--primary-blue), var(--light-blue));
        color: white;
        box-shadow: var(--card-shadow);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, var(--light-gray), white);
        border-radius: var(--border-radius);
        border: 1px solid #E9ECEF;
        font-weight: 600;
        color: var(--dark-gray);
    }
    
    /* Progress bar styling */
    .stProgress .css-1inwz65 {
        background: linear-gradient(45deg, var(--primary-blue), var(--light-blue));
        border-radius: 10px;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: white;
        border: 2px dashed var(--primary-blue);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
    }
    
    .stFileUploader:hover {
        background: #F8F9FA;
        border-color: var(--darker-blue);
    }
    
    /* Chart container styling */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
    }
    
    /* Loading spinner customization */
    .stSpinner {
        color: var(--primary-blue);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F1F1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, var(--primary-blue), var(--light-blue));
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, var(--darker-blue), var(--primary-blue));
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .info-card {
            padding: 1rem;
        }
        
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
    }
    
    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
        40%, 43% { transform: translate3d(0, -30px, 0); }
        70% { transform: translate3d(0, -15px, 0); }
        90% { transform: translate3d(0, -4px, 0); }
    }
    
    /* Utility classes */
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    .bounce-in {
        animation: bounce 1s ease-out;
    }
    
    .text-center {
        text-align: center;
    }
    
    .text-left {
        text-align: left;
    }
    
    .text-right {
        text-align: right;
    }
    
    .font-bold {
        font-weight: bold;
    }
    
    .font-normal {
        font-weight: normal;
    }
    
    .text-primary {
        color: var(--primary-blue);
    }
    
    .text-success {
        color: var(--success-green);
    }
    
    .text-warning {
        color: var(--warning-orange);
    }
    
    .text-error {
        color: var(--error-red);
    }
    
    .bg-primary {
        background-color: var(--primary-blue);
    }
    
    .bg-light {
        background-color: var(--light-gray);
    }
    
    .border-primary {
        border: 1px solid var(--primary-blue);
    }
    
    .rounded {
        border-radius: var(--border-radius);
    }
    
    .shadow {
        box-shadow: var(--card-shadow);
    }
    
    .transition {
        transition: var(--transition);
    }
    
    /* Medical icons using CSS */
    .medical-icon {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    .medical-icon.stethoscope::before {
        content: "🩺";
        font-size: 18px;
    }
    
    .medical-icon.pill::before {
        content: "💊";
        font-size: 18px;
    }
    
    .medical-icon.syringe::before {
        content: "💉";
        font-size: 18px;
    }
    
    .medical-icon.heart::before {
        content: "❤️";
        font-size: 18px;
    }
    
    .medical-icon.user::before {
        content: "👤";
        font-size: 18px;
    }
    
    .medical-icon.calendar::before {
        content: "📅";
        font-size: 18px;
    }
    
    .medical-icon.report::before {
        content: "📋";
        font-size: 18px;
    }
    
    .medical-icon.analytics::before {
        content: "📊";
        font-size: 18px;
    }
    
    /* Print styles */
    @media print {
        .stButton,
        .stSidebar,
        .main-header {
            display: none !important;
        }
        
        .stApp {
            background: white !important;
        }
        
        .info-card {
            box-shadow: none !important;
            border: 1px solid #000 !important;
        }
    }
</style>
"""

# Additional CSS for specific components
COMPONENT_CSS = {
    'LOGIN_FORM': """
    <style>
        .login-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid #E9ECEF;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
            color: var(--primary-blue);
        }
        
        .login-header h2 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .login-header p {
            margin: 0.5rem 0 0 0;
            color: var(--medium-gray);
        }
    </style>
    """,
    
    'DASHBOARD_CARDS': """
    <style>
        .dashboard-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-blue);
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .dashboard-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .card-metric {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--primary-blue);
            margin: 0;
        }
        
        .card-label {
            font-size: 1rem;
            color: var(--medium-gray);
            margin: 0.5rem 0 0 0;
        }
    </style>
    """,
    
    'PATIENT_CARDS': """
    <style>
        .patient-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }
        
        .patient-card.completed {
            border-left-color: var(--success-green);
            background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
        }
        
        .patient-card.waiting {
            border-left-color: var(--warning-orange);
            background: linear-gradient(135deg, #fffef8 0%, #fff3e0 100%);
        }
        
        .patient-card.emergency {
            border-left-color: var(--error-red);
            background: linear-gradient(135deg, #fff8f8 0%, #ffeaea 100%);
            animation: pulse 2s infinite;
        }
        
        .patient-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        
        .patient-name {
            font-size: 1.3rem;
            font-weight: bold;
            color: var(--dark-gray);
            margin: 0 0 0.5rem 0;
        }
        
        .patient-info {
            color: var(--medium-gray);
            font-size: 0.9rem;
            margin: 0.25rem 0;
        }
        
        .patient-status {
            font-weight: bold;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .status-completed {
            background: var(--success-green);
            color: white;
        }
        
        .status-waiting {
            background: var(--warning-orange);
            color: var(--dark-gray);
        }
        
        .status-emergency {
            background: var(--error-red);
            color: white;
        }
    </style>
    """
}

# CSS for prescription form
PRESCRIPTION_CSS = """
<style>
    .prescription-form {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .patient-context {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid var(--info-cyan);
    }
    
    .ai-analysis {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #9C27B0;
    }
    
    .medication-item {
        background: #f8f9fa;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .lab-test-item {
        background: #fff3cd;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
    }
</style>
"""

# Function to inject CSS
def inject_css():
    """Inject the main CSS styles into the Streamlit app"""
    import streamlit as st
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

def inject_component_css(component_name):
    """Inject specific component CSS"""
    import streamlit as st
    if component_name in COMPONENT_CSS:
        st.markdown(COMPONENT_CSS[component_name], unsafe_allow_html=True)

def inject_prescription_css():
    """Inject prescription form CSS"""
    import streamlit as st
    st.markdown(PRESCRIPTION_CSS, unsafe_allow_html=True)