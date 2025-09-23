# Compliance Monitoring System - Quick Start

## Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   - Edit `.env` file to add your OpenAI or Anthropic API keys for enhanced LLM analysis
   - System will work without API keys using pattern-based analysis only

## Running the Application

### Option 1: Quick Start (Windows)
Double-click `start_system.bat` to start both services automatically.

### Option 2: Manual Start

**Terminal 1 - Backend API:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend UI:**
```bash
streamlit run ui/streamlit_app.py
```

## Access the Application

- **Streamlit UI:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

## Usage

1. **Upload Documents:** Go to "Upload & Analyze" page
2. **Select Compliance Rules:** Choose GDPR, HIPAA, SOX frameworks
3. **Analyze:** Click "Upload & Analyze" to process documents
4. **View Results:** Check detailed compliance reports and visualizations
5. **Manage Documents:** Use "Document Library" to view all uploaded files
6. **Reports:** Generate comprehensive compliance reports with charts

## Features

- ✅ Multi-format document support (PDF, DOCX, TXT)
- ✅ Pattern-based compliance checking
- ✅ LLM-powered analysis (with API keys)
- ✅ Interactive dashboards and visualizations
- ✅ Compliance scoring and reporting
- ✅ Document library management
- ✅ Rule management interface

## Troubleshooting

- **API Connection Issues:** Ensure FastAPI server is running on port 8000
- **File Upload Errors:** Check file format and size (max 10MB)
- **LLM Analysis Not Working:** Add valid API keys to `.env` file
- **Database Issues:** Delete `compliance.db` to reset database

## File Structure

```
compliance-monitoring-system/
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── compliance_engine.py # Core analysis engine
│   ├── models.py          # Database models
│   ├── database.py        # Database configuration
│   └── rules/             # Compliance rule definitions
├── ui/                    # Streamlit frontend
│   └── streamlit_app.py   # Main UI application
├── uploads/               # Uploaded documents storage
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── start_system.bat       # Quick start script
```