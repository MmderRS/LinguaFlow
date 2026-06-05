def build_translation_prompt(
    source_text: str,
    matched_terms: list[dict],
    recent_context: list[str] | None = None,
) -> str:
    terms_block = "\n".join(
        f"- {item['source']} -> {item['target']}" for item in matched_terms
    ) or "- None"
    context_block = "\n".join(f"- {item}" for item in recent_context or []) or "- None"

    return f"""You translate live English technical subtitles into concise Simplified Chinese subtitles.

Rules:
- Output only the final Chinese subtitle, without notes or quotation marks.
- Keep terminology consistent with the glossary when relevant.
- Preserve technical meaning and avoid overexplaining.
- Prefer natural subtitle phrasing over literal word-for-word translation.

Glossary:
{terms_block}

Recent context:
{context_block}

English subtitle:
{source_text}
"""
