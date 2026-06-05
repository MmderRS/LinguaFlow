from fastapi import APIRouter

from app.config import settings
from app.schemas import PublicSettingsOut

router = APIRouter()


@router.get("/settings", response_model=PublicSettingsOut)
def get_public_settings() -> PublicSettingsOut:
    return PublicSettingsOut(
        asr_provider=settings.asr_provider,
        translation_provider=settings.translation_provider,
        available_asr_providers=["mock", "openai", "faster-whisper"],
        available_translation_providers=["mock", "openai", "gemini"],
    )
