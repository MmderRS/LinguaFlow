from abc import ABC, abstractmethod


class BaseASRService(ABC):
    supports_partial: bool = False
    supports_stream_chunks: bool = False

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        mime_type: str,
        session_id: str,
        segment_id: str,
        segment_index: int,
    ) -> str:
        raise NotImplementedError

    async def transcribe_text(self, text: str) -> str:
        return text.strip()

    def partial_text(self, segment_index: int, chunk_count: int) -> str:
        return ""
