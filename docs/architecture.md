# LinguaFlow 架构说明

## 总体架构

LinguaFlow 采用前后端分离架构：
- 前端：Vue 3 + Vite + TypeScript + Element Plus + Pinia
- 后端：FastAPI + SQLAlchemy + SQLite
- 实时层：WebSocket
- AI 能力层：ASR provider + Translation provider

## 数据流

1. 前端通过 WebSocket 建立实时会话。
2. 浏览器发送 `start`，随后发送音频 chunk 或 `debug_text`。
3. 后端通过 ASR provider 输出英文识别结果。
4. 后端根据术语库和上下文调用翻译 provider 输出中文字幕。
5. 已确认字幕写入 `history_records`。
6. 若后续上下文触发修正规则，后端广播 `correction` 并更新历史记录。
7. 前端字幕面板和历史页都消费同一批数据模型。

## 后端模块

- `app/main.py`：FastAPI 应用入口
- `app/api/`：REST API
- `app/ws/`：WebSocket 管理与实时入口
- `app/services/asr/`：ASR provider 抽象与实现
- `app/services/translation/`：翻译 provider 抽象与实现
- `app/services/history_service.py`：历史记录增删查改
- `app/services/term_service.py`：术语匹配与 CRUD
- `app/services/subtitle_service.py`：自动修正规则
- `app/data/terms_seed.py`：内置术语种子

## 前端模块

- `src/pages/`：四个主页面
- `src/components/subtitle/`：字幕展示与人工修正
- `src/components/history/`：历史记录与导出组件
- `src/stores/realtime.ts`：实时会话、录音、字幕状态
- `src/stores/history.ts`：历史记录列表状态
- `src/stores/settings.ts`：运行时设置状态
- `src/services/api.ts`：REST API 客户端
- `src/services/ws.ts`：WebSocket 客户端

## 数据模型

### 历史记录 `HistoryRecord`
- `session_id`
- `segment_id`
- `source_text`
- `target_text`
- `corrected`
- `created_at`
- `updated_at`

### 术语 `Term`
- `domain`
- `source`
- `target`
- `builtin`
- `created_at`

## Provider 策略

### ASR
- `mock`：用于端到端调试
- `openai`：当前真实识别优先路径
- `faster-whisper`：当前保留接口，后续接入本地推理

### Translation
- `mock`
- `openai`
- `gemini`

三种翻译实现遵循统一接口，输入包含：
- `source_text`
- `matched_terms`
- `recent_context`

## 修正机制

当前修正规则基于后续上下文自动触发。例如：
- 旧字幕：`remote sensing image`
- 新上下文出现 `analysis` / `classification` / `segmentation`
- 后端将旧字幕修正为 `remote sensing imagery`
- 前端显示 `[已修正]`

同时支持人工修正：
- 前端弹窗编辑中英文
- 调用历史修正 API
- 后端广播 `correction`

## 当前可扩展点

- 更细粒度的音频分段与静音检测
- `faster-whisper` 本地实时识别
- 多会话房间隔离和权限控制
- 更强的上下文翻译缓存与术语冲突解决
- 前端路由级拆包和更细的性能优化
