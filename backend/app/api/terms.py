from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DeleteResult, TermCreate, TermOut, TermUpdate
from app.services import term_service

router = APIRouter()


@router.get("/terms", response_model=list[TermOut])
def list_terms(
    query: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[TermOut]:
    return term_service.list_terms(db, query=query, domain=domain)


@router.post("/terms", response_model=TermOut, status_code=status.HTTP_201_CREATED)
def create_term(payload: TermCreate, db: Session = Depends(get_db)) -> TermOut:
    try:
        return term_service.create_term(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/terms/{term_id}", response_model=TermOut)
def update_term(term_id: int, payload: TermUpdate, db: Session = Depends(get_db)) -> TermOut:
    try:
        term = term_service.update_term(db, term_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return term


@router.delete("/terms/{term_id}", response_model=DeleteResult)
def delete_term(term_id: int, db: Session = Depends(get_db)) -> DeleteResult:
    try:
        deleted = term_service.delete_term(db, term_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return DeleteResult(deleted=deleted)
