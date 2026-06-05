import httpx

from app.config import settings
from app.services.asr.base import BaseASRService


def _filename_for_mime_type(mime_type: str) -> str:
    normalized = mime_type.lower()
    if "ogg" in normalized:
        return "segment.ogg"
    if "wav" in normalized:
        return "segment.wav"
    if "mp3" in normalized:
        return "segment.mp3"
    return "segment.webm"


class OpenAIASRService(BaseASRService):
    supports_stream_chunks = False

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        mime_type: str,
        session_id: str,
        segment_id: str,
        segment_index: int,
    ) -> str:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        if not audio_bytes:
            return ""

        base_url = settings.openai_base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        data = {
            "model": settings.openai_whisper_model,
            "language": settings.whisper_language,
            "response_format": "json",
        }
        files = {
            "file": (
                _filename_for_mime_type(mime_type),
                audio_bytes,
                mime_type or "audio/webm",
            )
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/audio/transcriptions",
                headers=headers,
                data=data,
                files=files,
            )
            response.raise_for_status()

        text = response.json().get("text", "").strip()
        return text
