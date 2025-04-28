# routes.py
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

import openai
from app.models import ApplicationConfig, DocumentHistory, PromptTemplate
from app.schemas import (
    ApplicationConfigCreate,
    ApplicationConfigSchema,
    ApplicationConfigUpdate,
    DocumentHistoryCreate,
    DocumentHistorySchema,
    PromptTemplateCreate,
    PromptTemplateSchema,
    PromptTemplateUpdate,
)
from app.session import get_db
from app.utils import get_config_value
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# General Router for shared endpoints
general_router = APIRouter(prefix="/api", tags=["General"])


@general_router.get("/")
def read_root():
    """Basic root endpoint."""
    return {"message": "SME Document Generator API"}


# --- Helper function to get OpenAI API key ---
def get_openai_api_key(db: Session) -> str:
    """Retrieves the OpenAI API key from the database configuration."""
    api_key = get_config_value(
        db, "openai_api_key"
    )  # Get key from DB using a utility function
    if not api_key:
        # Consider adding environment variable fallback here as a robust option
        # import os
        # api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured in the database.",
            )
    return api_key


# --- Endpoint to test OpenAI Connection ---
@general_router.get("/settings/llm/test-connection", summary="Test LLM Connection")
def test_llm_connection(db: Session = Depends(get_db)):
    """
    Tests the connection to the configured LLM provider (e.g., OpenAI)
    using the API key stored in the application config.
    """
    try:
        api_key = get_openai_api_key(db)
        # You might get the base URL and model from config too
        llm_api_base_url = get_config_value(
            db, "llm_api_base_url", default="https://api.openai.com/v1"
        )
        llm_model_test = get_config_value(
            db, "llm_model_test", default="gpt-3.5-turbo"
        )  # Use a specific test model config if available

        # Initialize the OpenAI client with the API key
        client = openai.OpenAI(
            api_key=api_key, base_url=llm_api_base_url  # Use base_url parameter
        )

        # Make a small, cheap API call to verify the connection and key
        response = client.chat.completions.create(
            model=llm_model_test,  # Use the test model
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=5,
            timeout=10.0,  # Set a timeout for the test call
        )
        print(response)  # Log the response for debugging

        # If the call succeeds without raising an exception, the connection is likely valid
        return {"message": "LLM connection successful!", "status": "ok"}

    except openai.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LLM Authentication failed. Check your API key.",
        )
    except openai.APIConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM API connection error: Could not connect to the API endpoint. Details: {e}",
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="LLM API rate limit exceeded.",
        )
    except openai.APIStatusError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=f"LLM API error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while testing LLM connection: {e}",
        )


# --- ApplicationConfig Endpoints (General & LLM Settings) ---
@general_router.get(
    "/settings",
    response_model=List[ApplicationConfigSchema],
    summary="Fetch All Application Settings",
)
def get_all_settings(db: Session = Depends(get_db)):
    """Retrieve all application configuration settings."""
    settings = db.query(ApplicationConfig).all()
    return settings


@general_router.get(
    "/settings/{config_key}",
    response_model=ApplicationConfigSchema,
    summary="Fetch Specific Application Setting",
)
def get_specific_setting(config_key: str, db: Session = Depends(get_db)):
    """Retrieve a specific application configuration setting by key."""
    db_setting = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )
    return db_setting


@general_router.post(
    "/settings",
    response_model=ApplicationConfigSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Application Setting",
)
def create_setting(
    setting_create: ApplicationConfigCreate, db: Session = Depends(get_db)
):
    """Create a new application configuration setting."""
    db_setting = ApplicationConfig(
        config_key=setting_create.config_key,
        config_value=setting_create.config_value,
        description=setting_create.description,
    )
    try:
        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)
        return db_setting
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Setting with key '{setting_create.config_key}' already exists.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the setting: {e}",
        )


@general_router.put(
    "/settings/{config_key}",
    response_model=ApplicationConfigSchema,
    summary="Update Application Setting",
)
def update_setting(
    config_key: str,
    setting_update: ApplicationConfigUpdate,
    db: Session = Depends(get_db),
):
    """Update a specific application configuration setting by key."""
    db_setting = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )

    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    # Update fields from the Pydantic model
    update_data = setting_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_setting, key, value)

    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    return db_setting


@general_router.delete(
    "/settings/{config_key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Application Setting",
)
def delete_setting(config_key: str, db: Session = Depends(get_db)):
    """Delete a specific application configuration setting by key."""
    db_setting = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )

    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found"
        )

    db.delete(db_setting)
    db.commit()
    return  # Returns 204 No Content on successful deletion


# --- PromptTemplate Endpoints ---
@general_router.post(
    "/templates",
    response_model=PromptTemplateSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Prompt Template",
)
def create_template(
    template_create: PromptTemplateCreate, db: Session = Depends(get_db)
):
    """Create a new prompt template."""
    db_template = PromptTemplate(
        name=template_create.name,
        document_type=template_create.document_type,
        template_content=template_create.template_content,
        is_active=template_create.is_active,
    )
    try:
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template with name '{template_create.name}' already exists.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the template: {e}",
        )


@general_router.get(
    "/templates",
    response_model=List[PromptTemplateSchema],
    summary="List Prompt Templates",
)
def list_templates(db: Session = Depends(get_db)):
    """Retrieve a list of all prompt templates."""
    templates = db.query(PromptTemplate).all()
    return templates


@general_router.get(
    "/templates/{template_id}",
    response_model=PromptTemplateSchema,
    summary="Get Prompt Template by ID",
)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a specific prompt template by ID."""
    db_template = (
        db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    )
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return db_template


@general_router.put(
    "/templates/{template_id}",
    response_model=PromptTemplateSchema,
    summary="Update Prompt Template",
)
def update_template(
    template_id: uuid.UUID,
    template_update: PromptTemplateUpdate,
    db: Session = Depends(get_db),
):
    """Update a specific prompt template by ID."""
    db_template = (
        db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    )

    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    update_data = template_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@general_router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Prompt Template",
)
def delete_template(template_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a specific prompt template by ID."""
    db_template = (
        db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    )

    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    db.delete(db_template)
    db.commit()
    return  # Returns 204 No Content on successful deletion


@general_router.post("/templates/{template_id}/test", summary="Test a Prompt Template")
def test_template(
    template_id: uuid.UUID,
    input_data: Dict[str, Any],  # Expecting test input data for the template
    db: Session = Depends(get_db),
):
    """
    Tests a specific prompt template by ID using provided input data
    to generate a preview from the LLM.
    """
    db_template = (
        db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    )

    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    api_key = get_openai_api_key(db)
    client = openai.OpenAI(api_key=api_key)

    # TODO: Implement prompt construction logic
    # This is a simplified example. You'll need to interpolate input_data
    # into the template_content to form the actual prompt.
    # Consider using a templating engine like Jinja2 or Python's .format()
    prompt = db_template.template_content  # Start with the template content
    try:
        # Example simple interpolation (requires input_data keys match placeholders)
        prompt = prompt.format(**input_data)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing data for template placeholder: {e}. Ensure input_data contains all required keys.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error formatting template with input data: {e}",
        )

    # Get LLM settings from config
    llm_model = get_config_value(db, "llm_model", default="gpt-3.5-turbo")
    llm_temperature = get_config_value(db, "llm_temperature", default=0.7)
    llm_max_tokens = get_config_value(db, "llm_max_tokens", default=1024)
    llm_system_message = get_config_value(
        db, "llm_system_message", default="You are a helpful assistant."
    )  # Add a config for system message

    try:
        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {
                    "role": "system",
                    "content": llm_system_message,
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=int(llm_max_tokens),  # Ensure type is int
            temperature=float(llm_temperature),  # Ensure type is float
        )
        generated_text = response.choices[0].message.content

        return {"template_id": template_id, "test_output": generated_text}

    except openai.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LLM Authentication failed during template test. Check your API key.",
        )
    except openai.APIConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM API connection error during template test: {e}",
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="LLM API rate limit exceeded during template test.",
        )
    except openai.APIStatusError as e:
        # Catch other API errors (e.g., invalid model)
        raise HTTPException(
            status_code=e.status_code,
            detail=f"LLM API error during template test: {e.response.text}",
        )
    except Exception as e:
        # Catch any other unexpected errors during the test
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while testing template: {e}",
        )


# --- Document Generation Endpoint ---
@general_router.post("/generate", summary="Generate Document")
def generate_document(
    generation_request: DocumentHistoryCreate,  # Use the Create schema for input
    db: Session = Depends(get_db),
):
    """
    Generates a document using a specified template and input data via the LLM,
    and saves a history record.
    """
    db_template = (
        db.query(PromptTemplate)
        .filter(PromptTemplate.id == generation_request.template_id)
        .first()
    )

    if not db_template or not db_template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or is inactive",
        )

    api_key = get_openai_api_key(db)
    client = openai.OpenAI(api_key=api_key)

    # TODO: Implement prompt construction logic
    # Interpolate generation_request.input_data into db_template.template_content
    # Ensure input_data is correctly formatted (e.g., deserialized from JSON string)
    input_data_dict = {}
    if generation_request.input_data:
        try:
            input_data_dict = json.loads(
                generation_request.input_data
            )  # Assuming input_data is a JSON string
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for input_data.",
            )

    prompt = db_template.template_content  # Start with the template content
    try:
        # Example simple interpolation (requires input_data keys match placeholders)
        prompt = prompt.format(**input_data_dict)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing data for template placeholder: {e}. Ensure input_data contains all required keys.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error formatting template with input data: {e}",
        )

    # Get LLM settings from config
    llm_model = get_config_value(db, "llm_model", default="gpt-3.5-turbo")
    llm_temperature = get_config_value(db, "llm_temperature", default=0.7)
    llm_max_tokens = get_config_value(db, "llm_max_tokens", default=1024)
    llm_system_message = get_config_value(
        db, "llm_system_message", default="You are a helpful assistant."
    )  # Add a config for system message

    try:
        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {
                    "role": "system",
                    "content": llm_system_message,
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=int(llm_max_tokens),
            temperature=float(llm_temperature),
        )
        generated_text = response.choices[0].message.content

        # Save history record
        db_history = DocumentHistory(
            template_id=generation_request.template_id,
            input_data=generation_request.input_data,  # Save original input data string
            generated_content=generated_text,  # Save generated text
            document_format=generation_request.document_format,  # Save requested format
            generated_at=datetime.utcnow(),
            # user_id=... # Link to user if authentication is implemented
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)

        # TODO: Add logic here to convert generated_text to PDF/DOCX
        # and return the file or a link to it.
        # For simplicity, returning the generated text and history ID for now.

        return {
            "history_id": db_history.id,
            "generated_content_preview": generated_text[:500]
            + "...",  # Return a preview
            "document_format": db_history.document_format,  # Return the format
        }

    except openai.AuthenticationError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LLM Authentication failed during generation. Check your API key.",
        )
    except openai.APIConnectionError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM API connection error during generation: {e}",
        )
    except openai.RateLimitError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="LLM API rate limit exceeded during generation.",
        )
    except openai.APIStatusError as e:
        db.rollback()
        # Catch other API errors (e.g., invalid model)
        raise HTTPException(
            status_code=e.status_code,
            detail=f"LLM API error during generation: {e.response.text}",
        )
    except Exception as e:
        # Catch any other unexpected errors during the test
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during document generation: {e}",
        )


# --- Document History Endpoints ---
@general_router.get(
    "/history/docs",
    response_model=List[DocumentHistorySchema],
    summary="Retrieve Document History",
)
def get_document_history(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Retrieve the history of generated documents with pagination."""
    history = db.query(DocumentHistory).offset(skip).limit(limit).all()
    return history


@general_router.get(
    "/history/docs/{history_id}",
    response_model=DocumentHistorySchema,
    summary="Get Document History by ID",
)
def get_specific_document_history(history_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a specific document history record by ID."""
    db_history = (
        db.query(DocumentHistory).filter(DocumentHistory.id == history_id).first()
    )
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document history record not found",
        )
    return db_history


# Optional: Add a delete endpoint for history if needed
@general_router.delete(
    "/history/docs/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Document History",
)
def delete_document_history(history_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a specific document history record by ID."""
    db_history = (
        db.query(DocumentHistory).filter(DocumentHistory.id == history_id).first()
    )
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document history record not found",
        )
    db.delete(db_history)
    db.commit()
    return
