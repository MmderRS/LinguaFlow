from fastapi import APIRouter, HTTPException, status

from app.schemas import ProviderUpdateIn, PublicSettingsOut
from app.services.runtime_config import (
    available_asr_providers,
    available_translation_providers,
    get_asr_provider,
    get_translation_provider,
    set_asr_provider,
    set_translation_provider,
)

router = APIRouter()


@router.get("/settings", response_model=PublicSettingsOut)
def get_public_settings() -> PublicSettingsOut:
    return PublicSettingsOut(
        asr_provider=get_asr_provider(),
        translation_provider=get_translation_provider(),
        available_asr_providers=available_asr_providers(),
        available_translation_providers=available_translation_providers(),
    )


@router.post("/settings/asr-provider", response_model=PublicSettingsOut)
def update_asr_provider(payload: ProviderUpdateIn) -> PublicSettingsOut:
    try:
        set_asr_provider(payload.provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return get_public_settings()


@router.post("/settings/translation-provider", response_model=PublicSettingsOut)
def update_translation_provider(payload: ProviderUpdateIn) -> PublicSettingsOut:
    try:
        set_translation_provider(payload.provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return get_public_settings()
