from app.services.asr.base import BaseASRService

SCRIPTED_SEGMENTS = [
    "[MOCK ASR] Welcome to today's remote sensing conference",
    "[MOCK ASR] We will focus on remote sensing image",
    "[MOCK ASR] analysis and land cover classification with U-Net models",
]


class MockASRService(BaseASRService):
    supports_partial = True
    supports_stream_chunks = True

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        mime_type: str,
        session_id: str,
        segment_id: str,
        segment_index: int,
    ) -> str:
        return SCRIPTED_SEGMENTS[segment_index % len(SCRIPTED_SEGMENTS)]

    async def transcribe_text(self, text: str) -> str:
        return text.strip() or SCRIPTED_SEGMENTS[0]

    def partial_text(self, segment_index: int, chunk_count: int) -> str:
        text = SCRIPTED_SEGMENTS[segment_index % len(SCRIPTED_SEGMENTS)]
        words = text.split()
        partial_size = min(len(words), max(1, chunk_count * 2))
        return " ".join(words[:partial_size])
