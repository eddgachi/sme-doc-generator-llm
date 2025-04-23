from sqlalchemy.orm import Session

from .models import ApplicationConfig

DEFAULT_CONFIGS = [
    {
        "config_key": "openai_api_key",
        "config_value": "",
        "description": "OpenAI Api Key",
    },
    {
        "config_key": "notification_emails",
        "config_value": "admin@example.com,support@example.com",
        "description": "Emails for notifications",
    },
    {
        "config_key": "notify_on_failure",
        "config_value": "true",
        "description": "Send notifications on sync failure",
    },
    {
        "config_key": "notify_on_success_with_errors",
        "config_value": "false",
        "description": "Notify on success with errors",
    },
    {
        "config_key": "notify_on_config_change",
        "config_value": "false",
        "description": "Notify on configuration changes",
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
