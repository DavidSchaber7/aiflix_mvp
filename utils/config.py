import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s: %(message)s")


def get_env(name: str, default: str | None = None) -> str | None:
    """Return the value of an environment variable."""
    return os.getenv(name, default)


def require_env(name: str) -> str:
    """Get an environment variable or raise an error if missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is required. Please set it in the .env file."
        )
    return value


def get_openai_client() -> OpenAI:
    """Create an OpenAI client, ensuring the API key exists."""
    api_key = require_env("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)

