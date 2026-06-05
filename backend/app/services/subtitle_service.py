import re

from app.schemas import CorrectionMessage
from app.services import history_service, term_service
from app.services.translation.base import BaseTranslationService

CORRECTION_RULES = [
    (
        re.compile(r"\bremote sensing image\b", flags=re.IGNORECASE),
        {"analysis", "classification", "segmentation", "imagery"},
        "remote sensing imagery",
    ),
]


async def maybe_autocorrect_previous(
    db,
    session_id: str,
    current_segment_id: str,
    current_source: str,
    translator: BaseTranslationService,
) -> CorrectionMessage | None:
    previous = history_service.get_latest_record(
        db,
        session_id=session_id,
        exclude_segment_id=current_segment_id,
    )
    if previous is None:
        return None

    original_source = previous.source_text
    updated_source = original_source
    lowered_current = current_source.lower()

    for pattern, triggers, replacement in CORRECTION_RULES:
        if pattern.search(original_source) and any(trigger in lowered_current for trigger in triggers):
            updated_source = pattern.sub(replacement, original_source)
            break

    if updated_source == original_source:
        return None

    matched_terms = term_service.match_terms(db, updated_source)
    recent_context = history_service.list_recent_source_context(
        db,
        session_id=session_id,
        exclude_segment_id=previous.segment_id,
    )
    translation = await translator.translate(updated_source, matched_terms, recent_context)
    updated_record = history_service.update_record(
        db,
        previous,
        source_text=updated_source,
        target_text=translation.target,
        corrected=True,
    )
    return CorrectionMessage(
        segment_id=updated_record.segment_id,
        source=updated_record.source_text,
        target=updated_record.target_text,
        record_id=updated_record.id,
    )
