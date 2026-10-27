from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reads settings from environment variables or the .env file in the project root."""

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    demo_auth_subject: str = "demo-user"

    # Gemini API key (free at https://aistudio.google.com/apikey).
    # Leave blank and the backend uses local rule-based fallbacks instead.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"


settings = Settings()
