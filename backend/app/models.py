from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
PostgresBase = declarative_base()


class ApplicationConfig(PostgresBase):
    """Stores global configuration settings for the application."""

    __tablename__ = "application_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
