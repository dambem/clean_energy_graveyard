from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Data
    repd_csv_path: Path = Path("data/repd-q3-oct-2025.csv")
    csv_encoding: str = "cp1252"
    output_dir: Path = Path("outputs")

    # API Keys
    gemini_api_key: str = ""
    google_search_api_key: str = ""
    google_cse_id: str = ""

    # Scraping
    scrape_max_chars: int = 10_000
    scrape_timeout: int = 10
    request_delay: float = 5.0

    # Gemini
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 1.0

    # NIMBY
    nimby_scores_path: Path = Path("outputs/nimby_scores.json")
    nimby_batch_size: int = 15

    model_config = {"env_file": ".env", "env_prefix": "REPD_"}


settings = Settings()
