import uuid
from datetime import datetime

from app.session import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


# Table for Application Configuration Settings
class ApplicationConfig(Base):
    __tablename__ = "application_config"

    id = Column(Integer, primary_key=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ApplicationConfig(key='{self.config_key}', value='{self.config_value[:50]}...')>"


# Table for Prompt Templates
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    document_type = Column(
        String, nullable=False
    )  # e.g., 'Quote', 'Invoice', 'LPO', 'Contract'
    template_content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PromptTemplate(name='{self.name}', document_type='{self.document_type}')>"


# Table for Document Generation History
class DocumentHistory(Base):
    __tablename__ = "document_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=False
    )
    input_data = Column(Text)  # Store the dynamic form input data as JSON or Text
    generated_content = Column(Text)  # Store the generated document content
    document_format = Column(String)  # e.g., 'pdf', 'docx'
    generated_at = Column(DateTime, default=datetime.utcnow)
    # Assuming a relationship to the template used
    template = relationship("PromptTemplate")

    def __repr__(self):
        return f"<DocumentHistory(id={self.id}, document_type='{self.template.document_type}', generated_at='{self.generated_at}')>"
