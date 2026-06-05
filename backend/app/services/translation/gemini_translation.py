import httpx

from app.config import settings
from app.services.translation.base import BaseTranslationService, TranslationResult
from app.services.translation_prompt import build_translation_prompt


class GeminiTranslationService(BaseTranslationService):
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": build_translation_prompt(source_text, matched_terms, recent_context)
                        }
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.2},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini translation returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        target = "".join(part.get("text", "") for part in parts).strip()
        if not target:
            raise RuntimeError("Gemini translation returned empty content")
        return TranslationResult(target=target, used_terms=matched_terms)
