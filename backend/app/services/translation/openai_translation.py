import httpx

from app.config import settings
from app.services.translation.base import BaseTranslationService, TranslationResult
from app.services.translation_prompt import build_translation_prompt


def _normalize_chat_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts).strip()
    return ""


class OpenAITranslationService(BaseTranslationService):
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        payload = {
            "model": settings.openai_translation_model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional simultaneous interpretation engine.",
                },
                {
                    "role": "user",
                    "content": build_translation_prompt(source_text, matched_terms, recent_context),
                },
            ],
        }
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        base_url = settings.openai_base_url.rstrip("/")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        target = _normalize_chat_content(content)
        if not target:
            raise RuntimeError("OpenAI translation returned empty content")
        return TranslationResult(target=target, used_terms=matched_terms)
