# Compliance Monitoring System Configuration

# Application Settings
APP_NAME = "Compliance Monitoring System"
APP_VERSION = "1.0.0"
DEBUG = True

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

# Streamlit Settings
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
UPLOAD_DIRECTORY = "uploads"

# Database Settings
DEFAULT_DATABASE_URL = "sqlite:///./compliance.db"

# LLM Settings
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1
MAX_TOKENS = 1000

# Analysis Settings
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
HIGH_CONFIDENCE_THRESHOLD = 0.7
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Rule Settings
SUPPORTED_RULE_TYPES = ["GDPR", "HIPAA", "SOX"]
RULE_SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH"]

# UI Settings
PAGE_TITLE = "Compliance Monitor"
PAGE_ICON = "🔍"
LAYOUT = "wide"

# Security Settings
ENABLE_CORS = True
ALLOWED_ORIGINS = ["*"]

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"