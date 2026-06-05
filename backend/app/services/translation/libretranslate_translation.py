import httpx

from app.config import settings
from app.services.translation.base import BaseTranslationService, TranslationResult

LANGUAGE_MAP = {
    "english": "en",
    "chinese": "zh",
    "simplified chinese": "zh",
    "traditional chinese": "zt",
}


class LibreTranslateService(BaseTranslationService):
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        if not source_text.strip():
            return TranslationResult(target="", used_terms=[])

        protected_text = source_text
        placeholders: dict[str, str] = {}
        for index, term in enumerate(sorted(matched_terms, key=lambda item: len(item["source"]), reverse=True)):
            placeholder = f"__TERM_{index}__"
            placeholders[placeholder] = term["target"]
            protected_text = protected_text.replace(term["source"], placeholder)

        payload = {
            "q": protected_text,
            "source": _language_code(settings.translation_source_lang),
            "target": _language_code(settings.translation_target_lang),
            "format": "text",
        }
        if settings.libretranslate_api_key:
            payload["api_key"] = settings.libretranslate_api_key

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(settings.libretranslate_url, data=payload)
            response.raise_for_status()

        translated = response.json().get("translatedText", "").strip()
        for placeholder, term_target in placeholders.items():
            translated = translated.replace(placeholder, term_target)

        return TranslationResult(target=translated, used_terms=matched_terms)


def _language_code(language_name: str) -> str:
    normalized = language_name.strip().lower()
    return LANGUAGE_MAP.get(normalized, normalized)
