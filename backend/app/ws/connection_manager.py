from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, set[WebSocket]] = {}
        self._socket_to_session: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    def bind_session(self, websocket: WebSocket, session_id: str) -> None:
        previous = self._socket_to_session.get(websocket)
        if previous and previous in self._sessions:
            self._sessions[previous].discard(websocket)
        self._socket_to_session[websocket] = session_id
        self._sessions.setdefault(session_id, set()).add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        session_id = self._socket_to_session.pop(websocket, None)
        if session_id and session_id in self._sessions:
            self._sessions[session_id].discard(websocket)
            if not self._sessions[session_id]:
                self._sessions.pop(session_id, None)

    async def send_model(self, websocket: WebSocket, payload) -> None:
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        await websocket.send_json(payload.model_dump(mode="json"))

    async def broadcast_session(self, session_id: str, payload) -> None:
        for websocket in list(self._sessions.get(session_id, set())):
            await self.send_model(websocket, payload)


manager = ConnectionManager()
