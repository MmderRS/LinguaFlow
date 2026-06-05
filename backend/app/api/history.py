from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CorrectionMessage, DeleteResult, HistoryOut, HistoryPage, ManualCorrectionIn
from app.services import history_service
from app.ws.connection_manager import manager

router = APIRouter()


@router.get("/history", response_model=HistoryPage)
def list_history(
    query: str | None = Query(default=None),
    session_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> HistoryPage:
    total, items = history_service.list_history(
        db,
        query=query,
        session_id=session_id,
        page=page,
        page_size=page_size,
    )
    return HistoryPage(total=total, page=page, page_size=page_size, items=items)


@router.get("/history/export")
def export_history(
    query: str | None = Query(default=None),
    session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    items = history_service.export_history(db, query=query, session_id=session_id)
    return JSONResponse(content=[item.to_dict() for item in items])


@router.delete("/history/{record_id}", response_model=DeleteResult)
def delete_record(record_id: int, db: Session = Depends(get_db)) -> DeleteResult:
    deleted = history_service.delete_record(db, record_id)
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return DeleteResult(deleted=deleted)


@router.delete("/history/session/{session_id}", response_model=DeleteResult)
def delete_session_history(session_id: str, db: Session = Depends(get_db)) -> DeleteResult:
    return DeleteResult(deleted=history_service.delete_session(db, session_id))


@router.post(
    "/history/session/{session_id}/segment/{segment_id}/correction",
    response_model=HistoryOut,
)
async def apply_manual_correction(
    session_id: str,
    segment_id: str,
    payload: ManualCorrectionIn,
    db: Session = Depends(get_db),
) -> HistoryOut:
    if payload.source_text is None and payload.target_text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide source_text or target_text",
        )

    record = history_service.apply_manual_correction(
        db,
        session_id=session_id,
        segment_id=segment_id,
        source_text=payload.source_text,
        target_text=payload.target_text,
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    await manager.broadcast_session(
        session_id,
        CorrectionMessage(
            segment_id=segment_id,
            source=record.source_text,
            target=record.target_text,
            record_id=record.id,
        ),
    )
    return record
