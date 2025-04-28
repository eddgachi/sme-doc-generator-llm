# utils.py

from sqlalchemy.orm import Session

from .models import ApplicationConfig

# Define the default configuration settings
DEFAULT_CONFIGS = [
    {
        "config_key": "openai_api_key",
        "config_value": "",  # Keeping this empty by default for security
        "description": "OpenAI API Key",
    },
    {
        "config_key": "llm_model",
        "config_value": "gpt-3.5-turbo",
        "description": "Which model to call (so you can switch between free-tier options)",
    },
    {
        "config_key": "llm_api_base_url",
        "config_value": "https://api.openai.com/v1",
        "description": "Base URL for your LLM provider (makes it swap-able)",
    },
    {
        "config_key": "llm_temperature",
        "config_value": "0.7",
        "description": "Controls creativity of the responses",
    },
    {
        "config_key": "llm_max_tokens",
        "config_value": "1024",
        "description": "Limits response length",
    },
    {
        "config_key": "llm_system_message",
        "config_value": "You are a helpful assistant.",
        "description": "Default system message for LLM calls.",
    },
    {
        "config_key": "llm_model_test",
        "config_value": "gpt-3.5-turbo",
        "description": "Specific LLM model to use for the connection test endpoint.",
    },
    {
        "config_key": "default_doc_format",
        "config_value": "pdf",
        "description": "pdf or docx – controls your download endpoint",
    },
    {
        "config_key": "enable_history",
        "config_value": "true",
        "description": "Toggle whether you persist users’ previous queries",
    },
    {
        "config_key": "history_retention_days",
        "config_value": "30",
        "description": "How long to keep query history around",
    },
    {
        "config_key": "response_timeout_seconds",
        "config_value": "30",
        "description": "How long your backend will wait for the LLM to respond",
    },
    {
        "config_key": "cors_allowed_origins",
        "config_value": "*",
        "description": "Comma-separated list of allowed front-ends/hosts",
    },
    {
        "config_key": "retry_on_failure_count",
        "config_value": "2",
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
        db.commit()
        print("Default configs seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during default config seeding: {e}")
        raise
