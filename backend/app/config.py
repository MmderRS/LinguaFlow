"""应用配置：从环境变量 / .env 读取，集中管理。"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    # ---- Server ----
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---- Database ----
    database_url: str = "sqlite:///./linguaflow.db"

    # ---- ASR ----
    asr_provider: str = "mock"  # faster-whisper | openai | mock
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_language: str = "en"
    whisper_vad_filter: bool = True

    # ---- Translation ----
    translation_provider: str = "mymemory"  # mymemory | libretranslate | openai | gemini | mock
    translation_source_lang: str = "English"
    translation_target_lang: str = "Chinese"
    libretranslate_url: str = "https://libretranslate.com/translate"
    libretranslate_api_key: str = ""
    mymemory_url: str = "https://api.mymemory.translated.net/get"
    mymemory_email: str = ""

    # ---- OpenAI ----
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_translation_model: str = "gpt-4o-mini"
    openai_whisper_model: str = "whisper-1"

    # ---- Gemini ----
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # ---- Audio pipeline ----
    audio_sample_rate: int = 16000
    partial_interval_ms: int = 900
    silence_timeout_ms: int = 800
    max_utterance_ms: int = 12000

    @field_validator("cors_origins")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
