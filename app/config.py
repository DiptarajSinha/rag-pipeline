from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_GEMINI_API_KEY: str
    DB_URL: str
    OPENAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignore extra env vars

settings = Settings()

# Usage example:
#print(settings.OPENAI_API_KEY)
