from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Threshold default dari .env — bisa di-override per request
    THRESHOLD_WARNING: float = 8.0
    THRESHOLD_DANGER: float = 10.0
    MAX_CAPACITY: float = 12.0

    # MySQL
    DB_HOST: str = "10.57.237.215"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123"
    DB_NAME: str = "water_levels"
    DB_TABLE: str = "water_levels"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
