from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    file_type = Column(String)

class ComplianceResult(Base):
    __tablename__ = "compliance_results"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    rule_type = Column(String)  # GDPR, HIPAA, SOX, etc.
    violation_type = Column(String)
    confidence_score = Column(Float)
    evidence = Column(Text)
    explanation = Column(Text)
    is_violation = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, index=True)
    rule_type = Column(String)  # GDPR, HIPAA, SOX
    description = Column(Text)
    pattern = Column(Text)  # Regex or search pattern
    severity = Column(String)  # HIGH, MEDIUM, LOW
    is_active = Column(Boolean, default=True)