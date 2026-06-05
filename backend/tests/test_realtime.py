import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_linguaflow.db")

from fastapi.testclient import TestClient

from app.main import app


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
