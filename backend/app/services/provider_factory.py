from functools import lru_cache

from app.config import settings
from app.services.asr.base import BaseASRService
from app.services.asr.mock_asr import MockASRService
from app.services.asr.openai_asr import OpenAIASRService
from app.services.translation.base import BaseTranslationService
from app.services.translation.gemini_translation import GeminiTranslationService
from app.services.translation.mock_translation import MockTranslationService
from app.services.translation.openai_translation import OpenAITranslationService


@lru_cache
def get_asr_service() -> BaseASRService:
    provider = settings.asr_provider.lower()
    if provider == "openai":
        return OpenAIASRService()
    if provider == "faster-whisper":
        return MockASRService()
    return MockASRService()


@lru_cache
def get_translation_service() -> BaseTranslationService:
    provider = settings.translation_provider.lower()
    if provider == "openai":
        return OpenAITranslationService()
    if provider == "gemini":
        return GeminiTranslationService()
    return MockTranslationService()
