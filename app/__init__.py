"""
Compliance Monitoring System - Main Application Package

This package contains the core compliance monitoring functionality including:
- FastAPI web application
- Compliance analysis engine
- Database models and operations
- Rule management system
"""

__version__ = "1.0.0"
__author__ = "Compliance Monitoring Team"
__description__ = "Advanced compliance monitoring and analysis system"

# Import main components for easy access
from .main import app
from .compliance_engine import ComplianceEngine
from .models import Document, ComplianceResult, ComplianceRule
from .database import get_database, create_tables

__all__ = [
    "app",
    "ComplianceEngine", 
    "Document",
    "ComplianceResult",
    "ComplianceRule",
    "get_database",
    "create_tables"
]
