from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GOOGLE_PROJECT_NAME: str
    GOOGLE_LOCATION_NAME: str
    SERVICE_ACCOUNT_SCOPE: str
    SERVICE_ACCOUNT_FILE: str
    
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    model_config = SettingsConfigDict(env_file=".env")

env = Settings()
