# services.py
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import ApplicationConfig

# Define the default configuration settings for Google AI
DEFAULT_CONFIGS = [
    {
        "config_key": "google_api_key",
        "config_value": "",  # Keep this empty by default for security
        "description": "Your Google AI API Key (required for Gemini models)",
    },
    {
        "config_key": "llm_model",
        "config_value": "gemini-1.5-flash-latest",  # Using a recent, fast model as default
        "description": "Which LLM model to call (e.g., gemini-1.5-flash-latest, gemini-1.5-pro-latest)",
    },
    {
        "config_key": "llm_api_base_url",
        "config_value": "",  # Google AI client typically doesn't need a custom base URL unless using a proxy
        "description": "Base URL for your LLM provider (usually not needed for Google AI)",
    },
    {
        "config_key": "llm_temperature",
        "config_value": "0.7",
        "description": "Controls creativity of the responses (0.0 to 1.0)",
    },
    {
        "config_key": "llm_max_tokens",  # Note: Google AI uses max_output_tokens
        "config_value": "1024",
        "description": "Limits response length (max_output_tokens for Google AI)",
    },
    {
        "config_key": "llm_system_message",  # Note: Google AI models have limited system instruction support via API
        "config_value": "You are a helpful assistant.",
        "description": "Default system message for LLM calls (support varies by model).",
    },
    {
        "config_key": "llm_model_test",
        "config_value": "gemini-1.5-flash-latest",  # Use a small, cheap model for testing
        "description": "Specific LLM model to use for the connection test endpoint.",
    },
    {
        "config_key": "default_doc_format",
        "config_value": "pdf",
        "description": "pdf or docx – controls your download endpoint",
    },
    {
        "config_key": "enable_history",
        "config_value": "true",  # Stored as string, remember to convert to bool when reading
        "description": "Toggle whether you persist users’ previous queries",
    },
    {
        "config_key": "history_retention_days",
        "config_value": "30",  # Stored as string, remember to convert to int when reading
        "description": "How long to keep query history around",
    },
    {
        "config_key": "response_timeout_seconds",
        "config_value": "60",  # Increased timeout as Gemini can sometimes take longer
        "description": "How long your backend will wait for the LLM to respond",
    },
    {
        "config_key": "cors_allowed_origins",
        "config_value": "*",  # Stored as string, remember to parse into a list
        "description": "Comma-separated list of allowed front-ends/hosts",
    },
    {
        "config_key": "retry_on_failure_count",
        "config_value": "2",  # Stored as string, remember to convert to int when reading
        "description": "How many times to auto-retry an LLM call if it times out",
    },
]


def check_configs_exist(db: Session) -> bool:
    """
    Checks if any config records exist in the database.
    Useful to determine if initial seeding is needed.
    """
    # Check if the application_config table has any rows
    return db.query(ApplicationConfig.id).limit(1).first() is not None


def seed_default_configs(db: Session):
    """
    Seeds the database with default configuration settings.
    If a config key already exists, it updates the value and description
    to match the defaults. If it doesn't exist, it creates it.
    """
    print("Starting default config seeding...")
    for cfg_data in DEFAULT_CONFIGS:
        config_key = cfg_data["config_key"]
        default_value = cfg_data["config_value"]
        default_description = cfg_data["description"]

        # Try to find the existing config
        existing_config = (
            db.query(ApplicationConfig)
            .filter(ApplicationConfig.config_key == config_key)
            .first()
        )

        if existing_config:
            # Config exists, check if update is needed
            needs_update = False
            if existing_config.config_value != default_value:
                existing_config.config_value = default_value
                needs_update = True
                print(f"Updating config '{config_key}': value changed.")

            # Only update description if the default description is not None and different
            if (
                default_description is not None
                and existing_config.description != default_description
            ):
                existing_config.description = default_description
                needs_update = True
                print(f"Updating config '{config_key}': description changed.")

            if needs_update:
                db.add(existing_config)  # Stage the update
                print(f"Config '{config_key}' updated.")
            else:
                print(f"Config '{config_key}' already exists and is up-to-date.")

        else:
            # Config does not exist, create it
            new_config = ApplicationConfig(
                config_key=config_key,
                config_value=default_value,
                description=default_description,
            )
            db.add(new_config)  # Stage the creation
            print(f"Creating new config '{config_key}'.")

    try:
        db.commit()  # Commit all staged changes (updates and creations)
        print("Default configs seeding completed successfully.")
    except Exception as e:
        db.rollback()  # Rollback in case of any error during commit
        print(f"Error during default config seeding: {e}")
        raise  # Re-raise the exception after rollback


def get_config_value(
    db: Session, config_key: str, default: Optional[Any] = None
) -> Optional[Any]:
    """
    Retrieves a configuration value from the application_config table.

    Args:
        db: The SQLAlchemy database session.
        config_key: The key of the configuration setting to retrieve.
        default: The default value to return if the config_key is not found.

    Returns:
        The config_value (as a string) if found, otherwise the default value.
        Note: You may need to cast the string value to the appropriate type (int, bool, float, list)
              when using it in your application logic.
    """
    config_item = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )

    if config_item:
        return config_item.config_value
    else:
        # Consider adding logging here if a key is not found and no default is provided
        # import logging
        # if default is None:
        #     logging.warning(f"Configuration key '{config_key}' not found in database and no default provided.")
        # else:
        #      logging.info(f"Configuration key '{config_key}' not found in database. Using provided default: {default}")
        return default


def get_config_by_key(db: Session, config_key: str) -> Optional[ApplicationConfig]:
    """
    Retrieves an ApplicationConfig object by its key.
    Returns the object or None if not found.
    """
    return (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )


# Helper function to get the Google API Key
def get_google_api_key(db: Session) -> str:
    """Retrieves the Google API key from the database."""
    api_key = get_config_value(db, "google_api_key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google API key is not configured. Please set it in the application settings.",
        )
    return api_key
