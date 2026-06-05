from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import history_service, term_service

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    return {
        "status": "ok",
        "history_records": history_service.count_history(db),
        "terms": term_service.count_terms(db),
    }
