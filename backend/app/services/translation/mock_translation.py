import re

from app.services.translation.base import BaseTranslationService, TranslationResult

PHRASE_MAP = [
    ("Welcome to today's", "欢迎来到今天的"),
    ("remote sensing conference", "遥感会议"),
    ("remote sensing imagery", "遥感影像"),
    ("remote sensing image", "遥感影像"),
    ("land cover classification", "土地覆盖分类"),
    ("semantic segmentation", "语义分割"),
    ("deep learning", "深度学习"),
    ("machine learning", "机器学习"),
    ("analysis", "分析"),
    ("conference", "会议"),
    ("model", "模型"),
    ("models", "模型"),
    ("with", "结合"),
    ("focus on", "重点讨论"),
    ("we will", "我们将"),
    ("today", "今天"),
]


def _replace_case_insensitive(text: str, source: str, target: str) -> str:
    return re.sub(re.escape(source), target, text, flags=re.IGNORECASE)


class MockTranslationService(BaseTranslationService):
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        translated = source_text

        for term in sorted(matched_terms, key=lambda item: len(item["source"]), reverse=True):
            translated = _replace_case_insensitive(translated, term["source"], term["target"])

        for source, target in PHRASE_MAP:
            translated = _replace_case_insensitive(translated, source, target)

        translated = re.sub(r"\s+", " ", translated).strip()
        if translated == source_text:
            translated = f"实时翻译：{source_text}"

        return TranslationResult(target=translated, used_terms=matched_terms)
