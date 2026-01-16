"""
Configuration management for the Mechanistic Interpretability Research Assistant
Loads settings from environment variables with sensible defaults
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Search API Configuration
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ID")

    # Application Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    CACHE_DIR: Path = DATA_DIR / "cache"
    RESEARCH_PAPERS_DIR: Path = DATA_DIR / "research_papers"
    RESULTS_DIR: Path = PROJECT_ROOT / "results"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # AutoGen Configuration
    AUTOGEN_MAX_ROUNDS: int = int(os.getenv("AUTOGEN_MAX_ROUNDS", "10"))
    AUTOGEN_TIMEOUT: int = int(os.getenv("AUTOGEN_TIMEOUT", "120"))

    # Agent-specific settings
    AGENT_FEATURE_EXTRACTION_ENABLED: bool = True
    AGENT_CIRCUITS_ANALYSIS_ENABLED: bool = True
    AGENT_RESEARCH_SYNTHESIZER_ENABLED: bool = True

    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")

        # Check if at least one search API is configured
        if not any([cls.SERPAPI_KEY, cls.GOOGLE_API_KEY]):
            errors.append("No search API key configured (SERPAPI_KEY or GOOGLE_API_KEY)")

        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESEARCH_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_llm_config(cls) -> dict:
        """Get AutoGen LLM configuration"""
        return {
            "model": cls.OPENAI_MODEL,
            "api_key": cls.OPENAI_API_KEY,
            "temperature": cls.OPENAI_TEMPERATURE,
        }


# Create settings instance
settings = Settings()

# Validate and create directories on import
if __name__ != "__main__":
    settings.create_directories()
