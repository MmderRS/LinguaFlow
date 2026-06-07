import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_linguaflow.db")

from app.config import settings
from app.services.provider_factory import get_translation_service
from app.services.runtime_config import (
    available_translation_providers,
    set_translation_provider,
)
from app.services.translation.mymemory_translation import MyMemoryTranslationService


def test_default_translation_provider_is_mymemory() -> None:
    assert settings.translation_provider == "mymemory"


def test_available_translation_providers_include_mymemory() -> None:
    assert "mymemory" in available_translation_providers()


def test_can_select_mymemory_translation_provider() -> None:
    set_translation_provider("mymemory")
    try:
        service = get_translation_service()
        assert isinstance(service, MyMemoryTranslationService)
    finally:
        set_translation_provider("mock")
