from app.services.asr.base import BaseASRService
from app.services.asr.mock_asr import MockASRService
from app.services.asr.openai_asr import OpenAIASRService
from app.services.runtime_config import get_asr_provider, get_translation_provider
from app.services.translation.base import BaseTranslationService
from app.services.translation.gemini_translation import GeminiTranslationService
from app.services.translation.libretranslate_translation import LibreTranslateService
from app.services.translation.mock_translation import MockTranslationService
from app.services.translation.mymemory_translation import MyMemoryTranslationService
from app.services.translation.openai_translation import OpenAITranslationService


_asr_instances: dict[str, BaseASRService] = {}
_translation_instances: dict[str, BaseTranslationService] = {}


def get_asr_service() -> BaseASRService:
    provider = get_asr_provider().lower()
    if provider not in _asr_instances:
        if provider == "openai":
            _asr_instances[provider] = OpenAIASRService()
        elif provider == "faster-whisper":
            from app.services.asr.faster_whisper_asr import FasterWhisperASRService

            _asr_instances[provider] = FasterWhisperASRService()
        else:
            _asr_instances[provider] = MockASRService()
    return _asr_instances[provider]


def get_translation_service() -> BaseTranslationService:
    provider = get_translation_provider().lower()
    if provider not in _translation_instances:
        if provider == "openai":
            _translation_instances[provider] = OpenAITranslationService()
        elif provider == "gemini":
            _translation_instances[provider] = GeminiTranslationService()
        elif provider == "libretranslate":
            _translation_instances[provider] = LibreTranslateService()
        elif provider == "mymemory":
            _translation_instances[provider] = MyMemoryTranslationService()
        else:
            _translation_instances[provider] = MockTranslationService()
    return _translation_instances[provider]
