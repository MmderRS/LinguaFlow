import asyncio
import os
import tempfile
from pathlib import Path

from app.config import settings
from app.services.asr.base import BaseASRService

try:
    from faster_whisper import WhisperModel
except ImportError as exc:  # pragma: no cover - exercised when optional dependency is missing
    WhisperModel = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


class FasterWhisperASRService(BaseASRService):
    supports_stream_chunks = False

    def __init__(self) -> None:
        if WhisperModel is None:
            raise RuntimeError(
                "faster-whisper is not installed. Run: python -m pip install faster-whisper"
            ) from IMPORT_ERROR

        self._model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        mime_type: str,
        session_id: str,
        segment_id: str,
        segment_index: int,
    ) -> str:
        if not audio_bytes:
            return ""

        suffix = _suffix_from_mime_type(mime_type)
        temp_path = await asyncio.to_thread(_write_temp_audio, audio_bytes, suffix)
        try:
            return await asyncio.to_thread(self._transcribe_file, temp_path)
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _transcribe_file(self, audio_path: Path) -> str:
        segments, _ = self._model.transcribe(
            str(audio_path),
            language=settings.whisper_language,
            vad_filter=settings.whisper_vad_filter,
        )
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        return text.strip()


def _suffix_from_mime_type(mime_type: str) -> str:
    normalized = mime_type.lower()
    if "wav" in normalized:
        return ".wav"
    if "ogg" in normalized:
        return ".ogg"
    if "mp3" in normalized:
        return ".mp3"
    return ".webm"


def _write_temp_audio(audio_bytes: bytes, suffix: str) -> Path:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp_file.write(audio_bytes)
        temp_file.flush()
    finally:
        temp_file.close()
    return Path(os.path.abspath(temp_file.name))
