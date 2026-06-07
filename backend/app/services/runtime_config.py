from app.config import settings

_available_asr = {"mock", "openai", "faster-whisper"}
_available_translation = {"mock", "openai", "gemini", "libretranslate", "mymemory"}

_runtime_state = {
    "asr_provider": settings.asr_provider,
    "translation_provider": settings.translation_provider,
}


def get_asr_provider() -> str:
    return _runtime_state["asr_provider"]


def set_asr_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in _available_asr:
        raise ValueError(f"Unsupported ASR provider: {provider}")
    _runtime_state["asr_provider"] = normalized
    return normalized


def get_translation_provider() -> str:
    return _runtime_state["translation_provider"]


def set_translation_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in _available_translation:
        raise ValueError(f"Unsupported translation provider: {provider}")
    _runtime_state["translation_provider"] = normalized
    return normalized


def available_asr_providers() -> list[str]:
    return ["mock", "openai", "faster-whisper"]


def available_translation_providers() -> list[str]:
    return ["mock", "mymemory", "libretranslate", "openai", "gemini"]
