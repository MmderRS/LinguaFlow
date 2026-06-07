import re
from urllib.parse import quote

import httpx

from app.config import settings
from app.services.translation.base import BaseTranslationService, TranslationResult

LANGUAGE_MAP = {
    "english": "en",
    "chinese": "zh-CN",
    "simplified chinese": "zh-CN",
    "traditional chinese": "zh-TW",
}


class MyMemoryTranslationService(BaseTranslationService):
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
            placeholder = f"TERMTOKEN{index}"
            placeholders[placeholder] = term["target"]
            protected_text = re.sub(re.escape(term["source"]), placeholder, protected_text, flags=re.IGNORECASE)

        params = {
            "q": protected_text,
            "langpair": f"{_language_code(settings.translation_source_lang)}|{_language_code(settings.translation_target_lang)}",
        }
        if settings.mymemory_email:
            params["de"] = settings.mymemory_email

        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(settings.mymemory_url, params=params)
            response.raise_for_status()

        data = response.json()
        translated = (data.get("responseData") or {}).get("translatedText", "").strip()
        if not translated:
            translated = _best_match(data)
        if not translated:
            raise RuntimeError("MyMemory returned empty translation")

        for placeholder, term_target in placeholders.items():
            translated = translated.replace(placeholder, term_target)
            translated = translated.replace(quote(placeholder), term_target)

        translated = _cleanup(translated)
        if _looks_untranslated(source_text, translated):
            raise RuntimeError("MyMemory returned untranslated English text")

        return TranslationResult(target=translated, used_terms=matched_terms)


def _best_match(data: dict) -> str:
    matches = data.get("matches") or []
    best = ""
    best_score = -1.0
    for item in matches:
        text = str(item.get("translation") or "").strip()
        try:
            score = float(item.get("quality") or item.get("match") or 0)
        except (TypeError, ValueError):
            score = 0.0
        if text and score > best_score:
            best = text
            best_score = score
    return best


def _language_code(language_name: str) -> str:
    normalized = language_name.strip().lower()
    return LANGUAGE_MAP.get(normalized, normalized)


def _cleanup(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _contains_chinese(text: str) -> bool:
    return bool(re.search(r"[一-鿿]", text))


def _looks_untranslated(source_text: str, translated: str) -> bool:
    if _contains_chinese(translated):
        return False
    source_words = set(re.findall(r"[a-zA-Z]{4,}", source_text.lower()))
    translated_words = set(re.findall(r"[a-zA-Z]{4,}", translated.lower()))
    if not translated_words:
        return False
    overlap = source_words & translated_words
    return len(overlap) >= max(1, len(translated_words) // 2)
