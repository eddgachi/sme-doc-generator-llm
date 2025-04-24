from sqlalchemy.orm import Session

from .models import ApplicationConfig

DEFAULT_CONFIGS = [
    {
        "config_key": "openai_api_key",
        "config_value": "",
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
    """
    return db.query(ApplicationConfig.id).first() is not None


def seed_default_configs(db: Session):
    """
    Seeds the database with default configuration settings.
    """
    # Check for existing configs to avoid duplicates
    existing_configs = {
        cfg.config_key: cfg for cfg in db.query(ApplicationConfig).all()
    }

    for cfg_data in DEFAULT_CONFIGS:
        if cfg_data["config_key"] not in existing_configs:
            config = ApplicationConfig(
                config_key=cfg_data["config_key"],
                config_value=cfg_data["config_value"],
                description=cfg_data["description"],
            )
            db.add(config)
        else:
            print(f"Config '{cfg_data['config_key']}' already exists, skipping.")

    db.commit()
    print("Default configs seeded successfully.")


def get_config_by_key(db: Session, config_key: str) -> ApplicationConfig:
    """
    Retrieves a config by its key.
    """
    return (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )
