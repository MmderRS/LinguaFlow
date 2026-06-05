from dataclasses import dataclass, field


@dataclass
class AudioBuffer:
    mime_type: str = "audio/webm"
    chunks: list[bytes] = field(default_factory=list)

    def set_mime_type(self, mime_type: str | None) -> None:
        if mime_type:
            self.mime_type = mime_type

    def append(self, chunk: bytes) -> None:
        if chunk:
            self.chunks.append(chunk)

    def has_data(self) -> bool:
        return bool(self.chunks)

    def drain(self) -> bytes:
        payload = b"".join(self.chunks)
        self.chunks.clear()
        return payload

    def clear(self) -> None:
        self.chunks.clear()
