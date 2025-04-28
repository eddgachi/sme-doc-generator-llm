# utils.py
from typing import Any, Optional

from app.models import ApplicationConfig
from sqlalchemy.orm import Session


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
        The config_value if found, otherwise the default value.
    """
    config_item = (
        db.query(ApplicationConfig)
        .filter(ApplicationConfig.config_key == config_key)
        .first()
    )

    if config_item:
        return config_item.config_value
    else:
        print(
            f"Configuration key '{config_key}' not found in database. Using default: {default}"
        )
        return default
