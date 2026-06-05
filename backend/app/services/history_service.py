from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import HistoryRecord


def count_history(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(HistoryRecord)) or 0


def _apply_filters(query_stmt, query: str | None = None, session_id: str | None = None):
    if query:
        like_query = f"%{query.strip()}%"
        query_stmt = query_stmt.where(
            or_(
                HistoryRecord.source_text.ilike(like_query),
                HistoryRecord.target_text.ilike(like_query),
            )
        )
    if session_id:
        query_stmt = query_stmt.where(HistoryRecord.session_id == session_id)
    return query_stmt


def list_history(
    db: Session,
    query: str | None = None,
    session_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, list[HistoryRecord]]:
    base_stmt = _apply_filters(select(HistoryRecord), query=query, session_id=session_id)
    total = db.scalar(select(func.count()).select_from(base_stmt.subquery())) or 0
    items = list(
        db.scalars(
            base_stmt
            .order_by(HistoryRecord.created_at.desc(), HistoryRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return total, items


def export_history(
    db: Session,
    query: str | None = None,
    session_id: str | None = None,
) -> list[HistoryRecord]:
    stmt = _apply_filters(select(HistoryRecord), query=query, session_id=session_id)
    return list(
        db.scalars(stmt.order_by(HistoryRecord.created_at.asc(), HistoryRecord.id.asc())).all()
    )


def list_recent_source_context(
    db: Session,
    session_id: str,
    limit: int = 3,
    exclude_segment_id: str | None = None,
) -> list[str]:
    stmt = select(HistoryRecord).where(HistoryRecord.session_id == session_id)
    if exclude_segment_id:
        stmt = stmt.where(HistoryRecord.segment_id != exclude_segment_id)
    items = list(db.scalars(stmt.order_by(HistoryRecord.created_at.desc()).limit(limit)).all())
    return [item.source_text for item in reversed(items)]


def create_record(
    db: Session,
    session_id: str,
    segment_id: str,
    source_text: str,
    target_text: str,
    corrected: bool = False,
) -> HistoryRecord:
    record = HistoryRecord(
        session_id=session_id,
        segment_id=segment_id,
        source_text=source_text,
        target_text=target_text,
        corrected=corrected,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record_by_segment(db: Session, session_id: str, segment_id: str) -> HistoryRecord | None:
    return db.scalar(
        select(HistoryRecord).where(
            HistoryRecord.session_id == session_id,
            HistoryRecord.segment_id == segment_id,
        )
    )


def get_latest_record(
    db: Session,
    session_id: str,
    exclude_segment_id: str | None = None,
) -> HistoryRecord | None:
    stmt = select(HistoryRecord).where(HistoryRecord.session_id == session_id)
    if exclude_segment_id:
        stmt = stmt.where(HistoryRecord.segment_id != exclude_segment_id)
    return db.scalar(stmt.order_by(HistoryRecord.created_at.desc(), HistoryRecord.id.desc()).limit(1))


def update_record(
    db: Session,
    record: HistoryRecord,
    source_text: str | None = None,
    target_text: str | None = None,
    corrected: bool | None = None,
) -> HistoryRecord:
    if source_text is not None:
        record.source_text = source_text.strip()
    if target_text is not None:
        record.target_text = target_text.strip()
    if corrected is not None:
        record.corrected = corrected
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def apply_manual_correction(
    db: Session,
    session_id: str,
    segment_id: str,
    source_text: str | None = None,
    target_text: str | None = None,
) -> HistoryRecord | None:
    record = get_record_by_segment(db, session_id=session_id, segment_id=segment_id)
    if record is None:
        return None
    return update_record(db, record, source_text=source_text, target_text=target_text, corrected=True)


def delete_record(db: Session, record_id: int) -> int:
    record = db.get(HistoryRecord, record_id)
    if record is None:
        return 0
    db.delete(record)
    db.commit()
    return 1


def delete_session(db: Session, session_id: str) -> int:
    records = list(
        db.scalars(select(HistoryRecord).where(HistoryRecord.session_id == session_id)).all()
    )
    if not records:
        return 0
    deleted = len(records)
    for record in records:
        db.delete(record)
    db.commit()
    return deleted
