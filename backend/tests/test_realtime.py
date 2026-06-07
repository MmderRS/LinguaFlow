import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_linguaflow.db")

from fastapi.testclient import TestClient

from app.main import app
from app.services.runtime_config import set_translation_provider


def test_realtime_debug_flow() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/ws/realtime") as websocket:
            connected = websocket.receive_json()
            assert connected["type"] == "status"

            websocket.send_json(
                {
                    "type": "start",
                    "session_id": "session-test",
                    "mime_type": "text/plain",
                }
            )
            websocket.receive_json()

            websocket.send_json(
                {
                    "type": "debug_text",
                    "text": "Remote sensing imagery supports land cover classification",
                }
            )

            asr = websocket.receive_json()
            translation = websocket.receive_json()

            assert asr["type"] == "asr"
            assert translation["type"] == "translation"
            assert translation["record_id"] is not None


def test_translation_falls_back_when_provider_is_not_configured() -> None:
    set_translation_provider("openai")
    try:
        with TestClient(app) as client:
            with client.websocket_connect("/ws/realtime") as websocket:
                websocket.receive_json()
                websocket.send_json(
                    {
                        "type": "start",
                        "session_id": "session-fallback",
                        "mime_type": "text/plain",
                    }
                )
                websocket.receive_json()

                websocket.send_json(
                    {
                        "type": "debug_text",
                        "text": "Remote sensing image analysis",
                    }
                )

                asr = websocket.receive_json()
                error = websocket.receive_json()
                translation = websocket.receive_json()

                assert asr["type"] == "asr"
                assert error["type"] == "error"
                assert "回退到本地翻译" in error["detail"]
                assert translation["type"] == "translation"
                assert translation["target"]
    finally:
        set_translation_provider("mock")


def test_finalize_audio_event_keeps_connection_alive_without_audio() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/ws/realtime") as websocket:
            websocket.receive_json()
            websocket.send_json(
                {
                    "type": "start",
                    "session_id": "session-audio-finalize",
                    "mime_type": "audio/webm",
                }
            )
            websocket.receive_json()

            websocket.send_json({"type": "finalize_audio"})
            processing = websocket.receive_json()
            resumed = websocket.receive_json()

            assert processing["type"] == "status"
            assert processing["state"] == "processing"
            assert resumed["type"] == "status"
            assert resumed["state"] == "listening"
