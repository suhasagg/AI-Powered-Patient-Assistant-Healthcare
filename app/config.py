from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    llm_mode: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    vector_mode: str = "memory"
    policy_version: str = "2026-01"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
