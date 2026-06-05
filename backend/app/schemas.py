"""Pydantic 模式（请求 / 响应 / WebSocket 消息）。"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HistoryOut(BaseModel):
    id: int
    session_id: str
    segment_id: str
    source_text: str
    target_text: str
    corrected: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class HistoryPage(BaseModel):
    total: int
    page: int = 1
    page_size: int = 20
    items: list[HistoryOut]


class DeleteResult(BaseModel):
    deleted: int


class TermBase(BaseModel):
    domain: str = Field(default="General", max_length=64)
    source: str = Field(min_length=1, max_length=255)
    target: str = Field(min_length=1, max_length=255)


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    domain: str | None = Field(default=None, max_length=64)
    target: str | None = Field(default=None, min_length=1, max_length=255)


class TermOut(TermBase):
    id: int
    builtin: bool = False
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ManualCorrectionIn(BaseModel):
    source_text: str | None = Field(default=None, min_length=1)
    target_text: str | None = Field(default=None, min_length=1)


class PublicSettingsOut(BaseModel):
    asr_provider: str
    translation_provider: str
    available_asr_providers: list[str]
    available_translation_providers: list[str]
    websocket_path: str = "/ws/realtime"
    supports_manual_correction: bool = True
    supports_mock_input: bool = True


class ProviderUpdateIn(BaseModel):
    provider: str = Field(min_length=1, max_length=64)


class ASRMessage(BaseModel):
    type: Literal["asr"] = "asr"
    segment_id: str
    text: str
    is_final: bool = False


class TranslationMessage(BaseModel):
    type: Literal["translation"] = "translation"
    segment_id: str
    source: str
    target: str
    is_final: bool = True
    terms: list[dict] = Field(default_factory=list)
    record_id: int | None = None
    corrected: bool = False


class CorrectionMessage(BaseModel):
    type: Literal["correction"] = "correction"
    segment_id: str
    source: str
    target: str
    record_id: int | None = None
    corrected: bool = True


class StatusMessage(BaseModel):
    type: Literal["status"] = "status"
    session_id: str
    state: str
    detail: str = ""
    asr_provider: str | None = None
    translation_provider: str | None = None
    is_mock_asr: bool = False


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    detail: str
