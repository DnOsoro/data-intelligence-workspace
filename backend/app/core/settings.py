import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_env: str = os.getenv(
        "APP_ENV",
        "development",
    )

    backend_host: str = os.getenv(
        "BACKEND_HOST",
        "127.0.0.1",
    )

    backend_port: int = int(
        os.getenv(
            "BACKEND_PORT",
            "8000",
        )
    )

    duckdb_database: str = os.getenv(
        "DUCKDB_DATABASE",
        ":memory:",
    )

    openrouter_api_key: str = os.getenv(
        "OPENROUTER_API_KEY",
        "",
    )

    openrouter_model: str = os.getenv(
        "OPENROUTER_MODEL",
        "openai/gpt-4o",
    )

    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    openrouter_http_referer: str = os.getenv(
        "OPENROUTER_HTTP_REFERER",
        "",
    )

    openrouter_x_title: str = os.getenv(
        "OPENROUTER_X_TITLE",
        "Data Intelligence Workspace",
    )

    openrouter_max_retries: int = int(
        os.getenv(
            "OPENROUTER_MAX_RETRIES",
            "3",
        )
    )

    openrouter_retry_delay_seconds: float = float(
        os.getenv(
            "OPENROUTER_RETRY_DELAY_SECONDS",
            "2",
        )
    )

    openrouter_max_tokens: int = int(
        os.getenv(
            "OPENROUTER_MAX_TOKENS",
            "1000",
        )
    )


settings = Settings()