from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    COHERE_API_KEY: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

# Usage example:
#print(settings.OPENAI_API_KEY)
