"""
preprocessing/common/config.py
================================
Centralised, validated settings loaded from .env via pydantic-settings.

All pipeline modules import `settings` from here. No module reads os.environ
directly so credentials cannot accidentally leak into logs.
"""

from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Database ----
    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "coursera_platform"
    db_user: str = "coursera_user"
    db_password: str = "changeme"

    # ---- Dataset paths ----
    source_zip: str = "IBM Data Science Professional Certificate.zip"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    inventory_dir: str = "data/inventory"

    # ---- Pipeline tuning ----
    video_segment_seconds: int = 300
    txt_chunk_target_tokens: int = 500
    txt_chunk_overlap_tokens: int = 50
    srt_align_confidence_threshold: float = 0.8

    # ---- Logging ----
    log_level: str = "INFO"
    log_file: str = "logs/pipeline.log"

    # ---- Feature flags ----
    skip_video_metadata: bool = False
    extract_frames: bool = False

    # ---- Derived paths (computed, not from env) ----
    @property
    def source_zip_path(self) -> Path:
        return Path(self.source_zip)

    @property
    def raw_dir(self) -> Path:
        return Path(self.raw_data_dir)

    @property
    def processed_dir(self) -> Path:
        return Path(self.processed_data_dir)

    @property
    def images_dir(self) -> Path:
        return self.processed_dir / "images"

    @property
    def inventory_path(self) -> Path:
        return Path(self.inventory_dir) / "course_inventory.json"

    @property
    def db_dsn(self) -> str:
        """psycopg3 DSN string or connection URL (password NOT logged)."""
        if self.database_url:
            return self.database_url
        return (
            f"host={self.db_host} port={self.db_port} "
            f"dbname={self.db_name} user={self.db_user} "
            f"password={self.db_password}"
        )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return v.upper()


# Singleton — import this everywhere
settings = Settings()
