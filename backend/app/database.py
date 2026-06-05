"""数据库连接与会话管理（SQLite + SQLAlchemy）。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite 在多线程下需要 check_same_thread=False
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url, connect_args=connect_args, future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖：每个请求一个 DB 会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """建表 + 写入术语种子数据。"""
    from app import models  # noqa: F401  确保模型被注册
    from app.data.terms_seed import seed_terms

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_terms(db)
