import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Base Schema ---
# Common configuration for Pydantic models to work with SQLAlchemy ORM objects
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# --- ApplicationConfig Schemas ---
class ApplicationConfigBase(BaseSchema):
    config_key: str = Field(
        ..., description="The unique key for the configuration setting."
    )
    config_value: str = Field(
        ..., description="The value of the configuration setting."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the config setting."
    )


class ApplicationConfigCreate(ApplicationConfigBase):
    pass


class ApplicationConfigUpdate(BaseSchema):
    config_key: Optional[str] = Field(
        None, description="The unique key for the configuration setting."
    )
    config_value: Optional[str] = Field(
        None, description="The value of the configuration setting."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the config setting."
    )


class ApplicationConfigSchema(ApplicationConfigBase):
    id: int


# --- PromptTemplate Schemas ---
class PromptTemplateBase(BaseSchema):
    name: str = Field(..., description="The name of the prompt template.")
    document_type: str = Field(
        ..., description="The type of document this template generates (e.g., 'Quote')."
    )
    template_content: str = Field(
        ..., description="The content of the prompt template."
    )
    is_active: bool = Field(
        True, description="Whether the template is currently active."
    )


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseSchema):
    name: Optional[str] = Field(None, description="The name of the prompt template.")
    document_type: Optional[str] = Field(
        None,
        description="The type of document this template generates (e.g., 'Quote').",
    )
    template_content: Optional[str] = Field(
        None, description="The content of the prompt template."
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the template is currently active."
    )


class PromptTemplateSchema(PromptTemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# --- DocumentHistory Schemas ---
class DocumentHistoryBase(BaseSchema):
    template_id: uuid.UUID = Field(..., description="The ID of the template used.")
    input_data: Optional[str] = Field(
        None, description="The input data used for generation (e.g., JSON string)."
    )
    generated_content: Optional[str] = Field(
        None, description="The generated document content or reference."
    )
    document_format: Optional[str] = Field(
        None, description="The format of the generated document (e.g., 'pdf')."
    )


class DocumentHistoryCreate(DocumentHistoryBase):
    pass


class DocumentHistoryUpdate(BaseSchema):
    input_data: Optional[str] = Field(
        None, description="The input data used for generation (e.e., JSON string)."
    )
    generated_content: Optional[str] = Field(
        None, description="The generated document content or reference."
    )
    document_format: Optional[str] = Field(
        None, description="The format of the generated document (e.g., 'pdf')."
    )


class DocumentHistorySchema(DocumentHistoryBase):
    id: uuid.UUID
    generated_at: datetime
