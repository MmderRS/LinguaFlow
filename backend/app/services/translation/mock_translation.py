import re

from app.services.translation.base import BaseTranslationService, TranslationResult

PHRASE_MAP = [
    ("Welcome to today's", "欢迎来到今天的"),
    ("remote sensing conference", "遥感会议"),
    ("remote sensing imagery", "遥感影像"),
    ("remote sensing image", "遥感影像"),
    ("remote sensing", "遥感"),
    ("land cover classification", "土地覆盖分类"),
    ("semantic segmentation", "语义分割"),
    ("deep learning", "深度学习"),
    ("machine learning", "机器学习"),
    ("u-net", "U-Net"),
    ("ndvi", "NDVI"),
    ("gis", "GIS"),
    ("image analysis", "影像分析"),
    ("analysis", "分析"),
    ("conference", "会议"),
    ("lecture", "讲座"),
    ("course", "课程"),
    ("model", "模型"),
    ("models", "模型"),
    ("with", "结合"),
    ("using", "使用"),
    ("based on", "基于"),
    ("focus on", "重点讨论"),
    ("we will", "我们将"),
    ("we are going to", "我们将"),
    ("supports", "支持"),
    ("today", "今天"),
]

WORD_MAP = {
    "welcome": "欢迎",
    "today": "今天",
    "remote": "遥感",
    "sensing": "感知",
    "image": "影像",
    "imagery": "影像",
    "analysis": "分析",
    "classification": "分类",
    "semantic": "语义",
    "segmentation": "分割",
    "learning": "学习",
    "deep": "深度",
    "machine": "机器",
    "land": "土地",
    "cover": "覆盖",
    "conference": "会议",
    "model": "模型",
    "models": "模型",
    "data": "数据",
    "dataset": "数据集",
    "training": "训练",
    "accuracy": "精度",
    "algorithm": "算法",
    "network": "网络",
    "method": "方法",
    "result": "结果",
    "results": "结果",
    "research": "研究",
    "system": "系统",
    "supports": "支持",
    "support": "支持",
    "using": "使用",
    "use": "使用",
    "with": "结合",
    "for": "用于",
    "and": "和",
    "or": "或",
    "the": "",
    "a": "",
    "an": "",
    "to": "",
    "of": "的",
    "in": "在",
    "on": "关于",
    "we": "我们",
    "will": "将",
    "can": "可以",
    "is": "是",
    "are": "是",
}


def _replace_case_insensitive(text: str, source: str, target: str) -> str:
    return re.sub(re.escape(source), target, text, flags=re.IGNORECASE)


def _contains_chinese(text: str) -> bool:
    return bool(re.search(r"[一-鿿]", text))


def _rough_word_translation(text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9\-]+|[^A-Za-z0-9\-\s]+", text)
    translated: list[str] = []
    for token in tokens:
        normalized = token.lower()
        if normalized in WORD_MAP:
            value = WORD_MAP[normalized]
            if value:
                translated.append(value)
        elif re.fullmatch(r"[^A-Za-z0-9\-\s]+", token):
            translated.append(token)
        else:
            translated.append(token)
    result = "".join(translated)
    result = re.sub(r"\s+", "", result).strip()
    return result


class MockTranslationService(BaseTranslationService):
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        translated = source_text.strip()

        for term in sorted(matched_terms, key=lambda item: len(item["source"]), reverse=True):
            translated = _replace_case_insensitive(translated, term["source"], term["target"])

        for source, target in PHRASE_MAP:
            translated = _replace_case_insensitive(translated, source, target)

        translated = re.sub(r"\s+", " ", translated).strip()
        if not _contains_chinese(translated) or re.search(r"[A-Za-z]{4,}", translated):
            rough = _rough_word_translation(translated)
            if _contains_chinese(rough):
                translated = rough

        if not _contains_chinese(translated):
            translated = f"本地翻译暂缺精确译文：{source_text}"
        elif re.search(r"[A-Za-z]{4,}", translated):
            translated = f"本地翻译：{translated}"

        return TranslationResult(target=translated, used_terms=matched_terms)
