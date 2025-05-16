# routes.py
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

import google.generativeai as genai  # Import the Google Generative AI library
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

# Import config utility functions from services
from app.services import (
    DEFAULT_CONFIGS,
    get_config_by_key,
    get_config_value,
    get_google_api_key,
)
from app.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from google.api_core import (
    exceptions as google_exceptions,
)  # Import Google API exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# General Router for shared endpoints
general_router = APIRouter(prefix="/api", tags=["General"])


@general_router.get("/")
def read_root():
    """Basic root endpoint."""
    return {"message": "SME Document Generator API"}


# --- ApplicationConfig Endpoints (General & LLM Settings) ---
@general_router.get(
    "/settings",
    response_model=List[ApplicationConfigSchema],
    summary="Fetch All Application Settings",
)
def get_all_settings(db: Session = Depends(get_db)):
    """Retrieve all application configuration settings."""
    settings = db.query(ApplicationConfig).all()
    # Mask the API key for security
    for setting in settings:
        if setting.config_key == "google_api_key" and setting.config_value:
            setting.config_value = "********"
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
    # Mask the API key for security
    if db_setting.config_key == "google_api_key" and db_setting.config_value:
        db_setting.config_value = "********"
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
        # Do not update masked API key if received
        if (
            key == "config_value"
            and config_key == "google_api_key"
            and value == "********"
        ):
            continue
        setattr(db_setting, key, value)

    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    # Mask the API key in the response
    if db_setting.config_key == "google_api_key" and db_setting.config_value:
        db_setting.config_value = "********"

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


# --- LLM Settings Endpoints (Specific) ---
@general_router.get("/settings/llm", summary="Fetch LLM Settings")
def get_llm_settings(db: Session = Depends(get_db)):
    """
    Fetches the current LLM configuration settings.
    """
    settings_keys = [
        "google_api_key",
        "llm_model",
        "llm_api_base_url",
        "llm_temperature",
        "llm_max_tokens",
        "llm_system_message",
        "llm_model_test",
        "default_doc_format",
        "enable_history",
        "history_retention_days",
        "response_timeout_seconds",
        "cors_allowed_origins",
        "retry_on_failure_count",
    ]
    settings = {}
    for key in settings_keys:
        value = get_config_value(db, key)
        # Mask the API key value for security
        if key == "google_api_key" and value:
            settings[key] = "********"
        else:
            settings[key] = value

    # Add description for each setting from DEFAULT_CONFIGS for frontend display
    config_descriptions = {
        cfg["config_key"]: cfg["description"] for cfg in DEFAULT_CONFIGS
    }
    settings_with_descriptions = []
    for key, value in settings.items():
        settings_with_descriptions.append(
            {
                "config_key": key,
                "config_value": value,
                "description": config_descriptions.get(key, "No description available"),
            }
        )

    return settings_with_descriptions


@general_router.put("/settings/llm", summary="Update LLM Settings")
def update_llm_settings(
    settings_update: ApplicationConfigUpdate, db: Session = Depends(get_db)
):
    """
    Updates the LLM configuration settings.
    """
    updated_count = 0
    # ApplicationConfigUpdate schema should contain the keys you want to allow updating
    update_data = settings_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        config_item = get_config_by_key(db, key)
        if config_item:
            # Handle the masked API key input: if it's the masked string, don't update
            if key == "google_api_key" and value == "********":
                continue  # Skip updating the masked key

            # Convert boolean/integer/float values from schema to string for storage
            if (
                isinstance(value, bool)
                or isinstance(value, int)
                or isinstance(value, float)
            ):
                config_item.config_value = str(value)
            elif isinstance(value, list):  # Handle list for cors_allowed_origins
                config_item.config_value = ",".join(value)
            else:
                config_item.config_value = str(
                    value
                )  # Ensure value is stored as string

            db.add(config_item)
            updated_count += 1
        # Optional: Log a warning if a key in update_data doesn't exist in the database configs

    db.commit()
    # Note: Refreshing a single item might not reflect all changes if multiple were updated.
    # For simplicity here, we rely on the next fetch to get updated values.

    return {"message": f"Updated {updated_count} LLM settings."}


@general_router.get("/settings/llm/test-connection", summary="Test LLM Connection")
def test_llm_connection(db: Session = Depends(get_db)):
    """
    Tests the connection to the configured LLM provider (Google Gemini)
    using the API key stored in the application config.
    """
    # 1. Load credentials & config
    api_key = get_google_api_key(db)  # Use the helper function
    test_model = get_config_value(
        db, "llm_model_test", default="gemini-1.5-flash-latest"
    )  # Use a Gemini test model
    response_timeout_seconds = float(
        get_config_value(db, "response_timeout_seconds", default="60")
    )

    # 2. Configure the Google Generative AI client
    genai.configure(api_key=api_key)

    try:
        # 3. Get the model and send a minimal chat completion
        model = genai.GenerativeModel(test_model)

        # Use generate_content for a simple prompt
        response = model.generate_content(
            "Hello, world!",
            request_options={
                "timeout": response_timeout_seconds
            },  # Use response_timeout_seconds
        )

        # Check if the response has content
        # Gemini responses can be structured differently, check for parts
        sample_reply = "No content received in response."
        if response and response.candidates:
            # Find the first text part in the content
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    sample_reply = part.text
                    break  # Found text, take the first part

        return {
            "status": "ok",
            "message": "LLM connection successful!",
            "model": test_model,
            "sample_reply": sample_reply,
        }

    except google_exceptions.PermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google AI authentication failed. Check your API key or project permissions. Details: {e}",
        )
    except google_exceptions.DeadlineExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Google AI API request timed out. Details: {e}",
        )
    except google_exceptions.ResourceExhausted as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Google AI API rate limit or quota exceeded. Details: {e}",
        )
    except google_exceptions.GoogleAPIError as e:
        # Catches other general Google API errors
        # Attempt to get a relevant status code, default to 500
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if hasattr(e, "code"):
            # Google API errors might have a 'code' attribute corresponding to HTTP status
            status_code = e.code
        raise HTTPException(
            status_code=status_code,
            detail=f"Google AI API error: {e}",
        )
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while testing LLM connection: {e}",
        )


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

    # 1. Load credentials & config
    api_key = get_google_api_key(db)
    llm_model = get_config_value(
        db, "llm_model_test", default="gemini-1.5-flash-latest"
    )
    llm_temperature = float(get_config_value(db, "llm_temperature", default="0.7"))
    llm_max_tokens = int(get_config_value(db, "llm_max_tokens", default="1024"))
    # llm_system_message = get_config_value(
    #     db, "llm_system_message", default="You are a helpful assistant."
    # )
    response_timeout_seconds = float(
        get_config_value(db, "response_timeout_seconds", default="60")
    )

    # 2. Configure the Google Generative AI client
    genai.configure(api_key=api_key)

    # 3. Construct the prompt
    prompt = db_template.template_content  # Start with the template content
    try:
        # Interpolate input_data into the template content
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

    # Add instruction for Kenyan context
    kenyan_context_instruction = " Ensure the document is formatted and relevant for the Kenyan market, including using KES for currency where applicable."
    final_prompt = prompt + kenyan_context_instruction

    try:
        # 4. Get the model and send a chat completion
        model = genai.GenerativeModel(llm_model)

        response = model.generate_content(
            final_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=llm_max_tokens, temperature=llm_temperature
            ),
            request_options={"timeout": response_timeout_seconds},
        )

        # Extract generated text
        generated_text = "No content received from LLM."
        if response and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    generated_text = part.text
                    break

        return {"template_id": template_id, "test_output": generated_text}

    except google_exceptions.PermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM Authentication failed during template test. Check your API key or project permissions. Details: {e}",
        )
    except google_exceptions.DeadlineExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM API request timed out during template test. Details: {e}",
        )
    except google_exceptions.ResourceExhausted as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"LLM API rate limit or quota exceeded during template test. Details: {e}",
        )
    except google_exceptions.GoogleAPIError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if hasattr(e, "code"):
            status_code = e.code
        raise HTTPException(
            status_code=status_code,
            detail=f"LLM API error during template test: {e}",
        )
    except Exception as e:
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

    # 1. Load credentials & config
    api_key = get_google_api_key(db)
    llm_model = get_config_value(db, "llm_model", default="gemini-1.5-flash-latest")
    llm_temperature = float(get_config_value(db, "llm_temperature", default="0.7"))
    llm_max_tokens = int(get_config_value(db, "llm_max_tokens", default="1024"))
    # llm_system_message = get_config_value(
    #     db, "llm_system_message", default="You are a helpful assistant."
    # )
    response_timeout_seconds = float(
        get_config_value(db, "response_timeout_seconds", default="60")
    )
    enable_history = (
        get_config_value(db, "enable_history", default="true").lower() == "true"
    )  # Read as bool

    # 2. Configure the Google Generative AI client
    genai.configure(api_key=api_key)

    # 3. Construct the prompt
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
        # Interpolate input_data into the template content
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

    # Add instruction for Kenyan context
    kenyan_context_instruction = " Ensure the document is formatted and relevant for the Kenyan market, including using KES for currency where applicable. Provide the output in plain text or Markdown format suitable for a document."
    final_prompt = prompt + kenyan_context_instruction

    generated_text = "Error: Could not generate document."
    try:
        # 4. Get the model and send a chat completion
        model = genai.GenerativeModel(llm_model)

        response = model.generate_content(
            final_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=llm_max_tokens, temperature=llm_temperature
            ),
            request_options={"timeout": response_timeout_seconds},
        )

        # Extract generated text
        if response and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    generated_text = part.text
                    break

    except google_exceptions.PermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM Authentication failed during generation. Check your API key or project permissions. Details: {e}",
        )
    except google_exceptions.DeadlineExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM API request timed out during generation. Details: {e}",
        )
    except google_exceptions.ResourceExhausted as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"LLM API rate limit or quota exceeded during generation. Details: {e}",
        )
    except google_exceptions.GoogleAPIError as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if hasattr(e, "code"):
            status_code = e.code
        raise HTTPException(
            status_code=status_code,
            detail=f"LLM API error during generation: {e}",
        )
    except Exception as e:
        # Catch any other unexpected errors during the test
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during document generation: {e}",
        )

    # 5. Save history record if enabled
    history_id = None
    if enable_history:
        try:
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
            history_id = db_history.id
        except Exception as e:
            db.rollback()
            # Log the error but don't necessarily fail the generation request
            print(f"Error saving document history: {e}")
            # Optionally, raise a less severe error or return a warning in the response

    # TODO: Add logic here to convert generated_text to PDF/DOCX
    # and return the file or a link to it.
    # For simplicity, returning the generated text and history ID for now.

    return {
        "history_id": history_id,  # Will be None if history is disabled or save failed
        "generated_content": generated_text,  # Return the full generated text
        "document_format": generation_request.document_format,  # Return the requested format
    }


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
    # Check if history is enabled
    enable_history = (
        get_config_value(db, "enable_history", default="true").lower() == "true"
    )
    if not enable_history:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document history is disabled in application settings.",
        )

    history = db.query(DocumentHistory).offset(skip).limit(limit).all()
    return history


@general_router.get(
    "/history/docs/{history_id}",
    response_model=DocumentHistorySchema,
    summary="Get Document History by ID",
)
def get_specific_document_history(history_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieve a specific document history record by ID."""
    # Check if history is enabled
    enable_history = (
        get_config_value(db, "enable_history", default="true").lower() == "true"
    )
    if not enable_history:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document history is disabled in application settings.",
        )

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
    # Check if history is enabled
    enable_history = (
        get_config_value(db, "enable_history", default="true").lower() == "true"
    )
    if not enable_history:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document history is disabled in application settings.",
        )

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
