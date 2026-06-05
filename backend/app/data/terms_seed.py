from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Term

DEFAULT_TERMS = [
    {"domain": "Remote Sensing", "source": "Remote Sensing", "target": "遥感"},
    {"domain": "Remote Sensing", "source": "GIS", "target": "地理信息系统"},
    {"domain": "Deep Learning", "source": "Deep Learning", "target": "深度学习"},
    {"domain": "Machine Learning", "source": "Machine Learning", "target": "机器学习"},
    {"domain": "Remote Sensing", "source": "NDVI", "target": "归一化植被指数"},
    {"domain": "Deep Learning", "source": "U-Net", "target": "U-Net"},
    {"domain": "Deep Learning", "source": "Semantic Segmentation", "target": "语义分割"},
    {"domain": "Remote Sensing", "source": "Land Cover Classification", "target": "土地覆盖分类"},
    {"domain": "Remote Sensing", "source": "remote sensing imagery", "target": "遥感影像"},
]


def seed_terms(db: Session) -> None:
    existing = {item.source.lower(): item for item in db.scalars(select(Term)).all()}
    created = False

    for payload in DEFAULT_TERMS:
        key = payload["source"].lower()
        if key in existing:
            term = existing[key]
            if not term.builtin:
                term.builtin = True
                created = True
            continue

        db.add(Term(**payload, builtin=True))
        created = True

    if created:
        db.commit()
