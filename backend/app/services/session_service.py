from dataclasses import dataclass, field

from app.services.audio_buffer import AudioBuffer


@dataclass
class RealtimeSessionState:
    session_id: str = ""
    mime_type: str = "audio/webm"
    segment_index: int = 0
    chunk_count: int = 0
    active_segment_id: str | None = None
    audio_buffer: AudioBuffer = field(default_factory=AudioBuffer)

    def start(self, session_id: str, mime_type: str | None) -> None:
        self.session_id = session_id
        self.segment_index = 0
        self.chunk_count = 0
        self.active_segment_id = None
        self.audio_buffer.clear()
        self.audio_buffer.set_mime_type(mime_type)
        if mime_type:
            self.mime_type = mime_type

    def ensure_segment_id(self) -> str:
        if self.active_segment_id is None:
            self.active_segment_id = f"seg-{self.segment_index + 1:04d}"
        return self.active_segment_id

    def append_audio(self, chunk: bytes) -> str:
        self.audio_buffer.append(chunk)
        self.chunk_count += 1
        return self.ensure_segment_id()

    def consume_segment(self) -> tuple[str, bytes]:
        segment_id = self.ensure_segment_id()
        payload = self.audio_buffer.drain()
        self.active_segment_id = None
        self.chunk_count = 0
        self.segment_index += 1
        return segment_id, payload

    def has_audio(self) -> bool:
        return self.audio_buffer.has_data()
