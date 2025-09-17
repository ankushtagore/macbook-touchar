import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )

    # Touch Bar Configuration
    TOUCH_BAR_WIDTH: int = 1080  # Standard Touch Bar width
    TOUCH_BAR_HEIGHT: int = 60  # Standard Touch Bar height
    MAX_ANSWER_LENGTH: int = 200  # Maximum characters to display on Touch Bar

    # UI Configuration
    FONT_SIZE: int = 12
    BACKGROUND_COLOR: str = "#1e1e1e"
    TEXT_COLOR: str = "#ffffff"
    ACCENT_COLOR: str = "#007AFF"

    # Search Configuration
    SEARCH_TIMEOUT: int = 30  # seconds
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
