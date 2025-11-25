from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_account_file: str
    google_api_key: str
    gemini_model: str
    gemini_pro_model: str
    project_name: str
    location_name: str
    
    aws_access_key_id: str
    aws_secret_access_key: str
    claude_sonnet_model: str
    mistral_pixtral_model: str
    claude_region: str

    gpt_4o_mini: str
    azure_api_key_gpt4o_mini: str
    azure_endpoint_gpt4o_mini: str
    azure_api_version: str

    model_config = SettingsConfigDict(env_file=".env")

env = Settings()
