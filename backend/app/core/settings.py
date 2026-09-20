import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )
    gemini_max_retries: int = int(
        os.getenv("GEMINI_MAX_RETRIES", "3")
    )
    gemini_retry_delay_seconds: float = float(
        os.getenv("GEMINI_RETRY_DELAY_SECONDS", "2")
    )


settings = Settings()