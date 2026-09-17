from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Coding Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5433/"
        "ai_coding_assistant"
    )

    REDIS_URL: str = "redis://localhost:6379/0"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "code_chunks"

    REPOSITORY_STORAGE_PATH: str = "data/repositories"

    GITHUB_REDIRECT_URI: str = (
        "http://localhost:8000/api/github/callback"
    )

    MAX_AGENT_ITERATIONS: int = 5
    TEST_TIMEOUT_SECONDS: int = 120
    MAX_FILE_SIZE_MB: int = 5

    SANDBOX_CPU_LIMIT: int = 1
    SANDBOX_MEMORY_LIMIT: str = "512m"
    SANDBOX_PIDS_LIMIT: int = 100
    SANDBOX_NETWORK_DISABLED: bool = True

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()