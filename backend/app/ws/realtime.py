import json
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import SessionLocal
from app.schemas import ASRMessage, ErrorMessage, StatusMessage, TranslationMessage
from app.services import history_service, subtitle_service, term_service
from app.services.provider_factory import get_asr_service, get_translation_service
from app.services.session_service import RealtimeSessionState
from app.ws.connection_manager import manager

router = APIRouter()


async def _send_error(websocket: WebSocket, detail: str) -> None:
    await manager.send_model(websocket, ErrorMessage(detail=detail))


async def _finalize_segment(websocket: WebSocket, state: RealtimeSessionState, db) -> None:
    if not state.session_id:
        await _send_error(websocket, "Session has not started")
        return
    if not state.has_audio():
        return

    segment_id, audio_bytes = state.consume_segment()
    asr_service = get_asr_service()
    translation_service = get_translation_service()
    source_text = await asr_service.transcribe_audio(
        audio_bytes=audio_bytes,
        mime_type=state.mime_type,
        session_id=state.session_id,
        segment_id=segment_id,
        segment_index=state.segment_index - 1,
    )
    if not source_text:
        return

    await manager.send_model(
        websocket,
        ASRMessage(segment_id=segment_id, text=source_text, is_final=True),
    )

    matched_terms = term_service.match_terms(db, source_text)
    recent_context = history_service.list_recent_source_context(db, session_id=state.session_id)
    translation = await translation_service.translate(source_text, matched_terms, recent_context)
    record = history_service.create_record(
        db,
        session_id=state.session_id,
        segment_id=segment_id,
        source_text=source_text,
        target_text=translation.target,
    )

    await manager.broadcast_session(
        state.session_id,
        TranslationMessage(
            segment_id=segment_id,
            source=source_text,
            target=translation.target,
            terms=translation.used_terms,
            record_id=record.id,
            corrected=record.corrected,
        ),
    )

    correction = await subtitle_service.maybe_autocorrect_previous(
        db,
        session_id=state.session_id,
        current_segment_id=segment_id,
        current_source=source_text,
        translator=translation_service,
    )
    if correction is not None:
        await manager.broadcast_session(state.session_id, correction)


async def _process_debug_text(websocket: WebSocket, state: RealtimeSessionState, db, text: str) -> None:
    if not state.session_id:
        state.start(f"session-{uuid4().hex[:8]}", "text/plain")
        manager.bind_session(websocket, state.session_id)

    segment_id = state.ensure_segment_id()
    asr_service = get_asr_service()
    translation_service = get_translation_service()
    source_text = await asr_service.transcribe_text(text)
    await manager.send_model(
        websocket,
        ASRMessage(segment_id=segment_id, text=source_text, is_final=True),
    )

    matched_terms = term_service.match_terms(db, source_text)
    recent_context = history_service.list_recent_source_context(db, session_id=state.session_id)
    translation = await translation_service.translate(source_text, matched_terms, recent_context)
    record = history_service.create_record(
        db,
        session_id=state.session_id,
        segment_id=segment_id,
        source_text=source_text,
        target_text=translation.target,
    )

    await manager.broadcast_session(
        state.session_id,
        TranslationMessage(
            segment_id=segment_id,
            source=source_text,
            target=translation.target,
            terms=translation.used_terms,
            record_id=record.id,
            corrected=record.corrected,
        ),
    )

    state.segment_index += 1
    state.active_segment_id = None

    correction = await subtitle_service.maybe_autocorrect_previous(
        db,
        session_id=state.session_id,
        current_segment_id=segment_id,
        current_source=source_text,
        translator=translation_service,
    )
    if correction is not None:
        await manager.broadcast_session(state.session_id, correction)


@router.websocket("/ws/realtime")
async def realtime_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    db = SessionLocal()
    state = RealtimeSessionState()

    try:
        await manager.send_model(
            websocket,
            StatusMessage(session_id="", state="connected", detail="WebSocket ready"),
        )

        while True:
            message = await websocket.receive()
            message_type = message.get("type")

            if message_type == "websocket.disconnect":
                break

            if message.get("text") is not None:
                payload = json.loads(message["text"])
                event_type = payload.get("type")

                if event_type == "start":
                    session_id = payload.get("session_id") or f"session-{uuid4().hex[:8]}"
                    mime_type = payload.get("mime_type") or "audio/webm"
                    state.start(session_id, mime_type)
                    manager.bind_session(websocket, session_id)
                    await manager.send_model(
                        websocket,
                        StatusMessage(
                            session_id=session_id,
                            state="listening",
                            detail="Audio stream started",
                        ),
                    )
                    continue

                if event_type == "stop":
                    await _finalize_segment(websocket, state, db)
                    await manager.send_model(
                        websocket,
                        StatusMessage(
                            session_id=state.session_id,
                            state="idle",
                            detail="Audio stream stopped",
                        ),
                    )
                    continue

                if event_type == "ping":
                    await manager.send_model(
                        websocket,
                        StatusMessage(
                            session_id=state.session_id,
                            state="heartbeat",
                            detail="pong",
                        ),
                    )
                    continue

                if event_type == "debug_text":
                    await _process_debug_text(websocket, state, db, payload.get("text", ""))
                    continue

                await _send_error(websocket, f"Unsupported event type: {event_type}")
                continue

            if message.get("bytes") is not None:
                if not state.session_id:
                    await _send_error(websocket, "Send a start event before audio chunks")
                    continue

                state.append_audio(message["bytes"])
                asr_service = get_asr_service()
                if asr_service.supports_partial:
                    partial_text = asr_service.partial_text(
                        state.segment_index,
                        state.chunk_count,
                    )
                    if partial_text:
                        await manager.send_model(
                            websocket,
                            ASRMessage(
                                segment_id=state.ensure_segment_id(),
                                text=partial_text,
                                is_final=False,
                            ),
                        )
                    if state.chunk_count >= 3:
                        await _finalize_segment(websocket, state, db)
                elif state.chunk_count >= 2:
                    await _finalize_segment(websocket, state, db)
                continue

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await _send_error(websocket, str(exc))
    finally:
        db.close()
        await manager.disconnect(websocket)
