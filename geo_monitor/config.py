from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str
    GEMINI_API_KEY: str

    model_config = {
        "env_file": ".env"
    }


settings = Settings()