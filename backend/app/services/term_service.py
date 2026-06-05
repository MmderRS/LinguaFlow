from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Term
from app.schemas import TermCreate, TermUpdate


def count_terms(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Term)) or 0


def list_terms(db: Session, query: str | None = None, domain: str | None = None) -> list[Term]:
    stmt = select(Term)
    if query:
        normalized = query.strip().lower()
        stmt = stmt.where(
            or_(
                func.lower(Term.source).contains(normalized),
                func.lower(Term.target).contains(normalized),
            )
        )
    if domain:
        stmt = stmt.where(Term.domain == domain)
    stmt = stmt.order_by(Term.builtin.desc(), Term.domain.asc(), Term.source.asc())
    return list(db.scalars(stmt).all())


def create_term(db: Session, payload: TermCreate) -> Term:
    source = payload.source.strip()
    target = payload.target.strip()
    existing = db.scalar(select(Term).where(func.lower(Term.source) == source.lower()))
    if existing is not None:
        raise ValueError("Term already exists")

    term = Term(
        domain=payload.domain.strip() or "General",
        source=source,
        target=target,
        builtin=False,
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


def update_term(db: Session, term_id: int, payload: TermUpdate) -> Term | None:
    term = db.get(Term, term_id)
    if term is None:
        return None
    if term.builtin:
        raise ValueError("Built-in terms are read-only")
    if payload.domain is not None:
        term.domain = payload.domain.strip() or "General"
    if payload.target is not None:
        term.target = payload.target.strip()
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


def delete_term(db: Session, term_id: int) -> int:
    term = db.get(Term, term_id)
    if term is None:
        return 0
    if term.builtin:
        raise ValueError("Built-in terms cannot be deleted")
    db.delete(term)
    db.commit()
    return 1


def match_terms(db: Session, text: str) -> list[dict]:
    normalized = text.lower().strip()
    if not normalized:
        return []

    matches: list[dict] = []
    seen: set[str] = set()
    for term in sorted(list_terms(db), key=lambda item: len(item.source), reverse=True):
        key = term.source.lower()
        if key in normalized and key not in seen:
            matches.append(
                {
                    "source": term.source,
                    "target": term.target,
                    "domain": term.domain,
                    "builtin": term.builtin,
                }
            )
            seen.add(key)
    return matches
