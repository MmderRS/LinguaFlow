from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TranslationResult:
    target: str
    used_terms: list[dict] = field(default_factory=list)


class BaseTranslationService(ABC):
    @abstractmethod
    async def translate(
        self,
        source_text: str,
        matched_terms: list[dict],
        recent_context: list[str] | None = None,
    ) -> TranslationResult:
        raise NotImplementedError
