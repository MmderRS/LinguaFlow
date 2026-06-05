# LinguaFlow

面向技术会议、在线课程、学术讲座、国际会议场景的 AI 实时同声传译助手。

当前版本提供一个可运行的 MVP：
- Vue 3 + Vite + TypeScript + Element Plus + Pinia 前端
- FastAPI + SQLite 后端
- WebSocket 实时双向通信
- mock / OpenAI Whisper ASR provider 抽象
- mock / OpenAI / Gemini 翻译 provider 抽象
- 双语字幕、自动修正、人工修正
- 术语库管理、历史记录查询/删除/导出 JSON

## 目录结构

```text
LinguaFlow/
├─ frontend/
│  ├─ index.html
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  └─ src/
│     ├─ App.vue
│     ├─ main.ts
│     ├─ components/
│     ├─ composables/
│     ├─ pages/
│     ├─ router/
│     ├─ services/
│     ├─ stores/
│     ├─ styles/
│     └─ types/
├─ backend/
│  ├─ requirements.txt
│  ├─ app/
│  │  ├─ api/
│  │  ├─ data/
│  │  ├─ services/
│  │  │  ├─ asr/
│  │  │  └─ translation/
│  │  ├─ ws/
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ main.py
│  │  ├─ models.py
│  │  └─ schemas.py
│  └─ tests/
├─ docs/
│  ├─ architecture.md
│  └─ deployment.md
└─ README.md
```

## 快速开始

### 1. 后端

推荐使用你当前指定的 Python 环境：`D:/ProgramData/miniconda3/envs/py310/python.exe`

安装依赖：

```bash
"D:/ProgramData/miniconda3/envs/py310/python.exe" -m pip install -r "E:/LinguaFlow/backend/requirements.txt"
```

启动服务：

```bash
PYTHONPATH="E:/LinguaFlow/backend" "D:/ProgramData/miniconda3/envs/py310/python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端

安装依赖：

```bash
npm --prefix "E:/LinguaFlow/frontend" install
```

启动开发服务器：

```bash
npm --prefix "E:/LinguaFlow/frontend" run dev
```

前端默认访问 `http://127.0.0.1:8000`。
如需修改，可设置 `VITE_API_BASE_URL`。

## 环境变量

后端支持从 `.env` 读取配置。可参考 [backend/.env.example](backend/.env.example)。

关键项：
- `ASR_PROVIDER=mock|openai|faster-whisper`
- `TRANSLATION_PROVIDER=mock|openai|gemini`
- `OPENAI_API_KEY=`
- `OPENAI_TRANSLATION_MODEL=gpt-4o-mini`
- `OPENAI_WHISPER_MODEL=whisper-1`
- `GEMINI_API_KEY=`
- `DATABASE_URL=sqlite:///./linguaflow.db`

## 页面说明

- 首页：项目概览与能力说明
- 实时翻译页：麦克风录音、调试文本注入、双语字幕、自动修正、人工修正
- 历史记录页：查询、删除、导出 JSON、继续修正
- 设置页：查看 provider 配置、管理用户术语

## 实时协议

WebSocket 地址：`/ws/realtime`

客户端事件：
- `start`
- `stop`
- `ping`
- `debug_text`
- 二进制音频 chunk

服务端事件：
- `status`
- `asr`
- `translation`
- `correction`
- `error`

## 测试与验证

后端测试：

```bash
PYTHONPATH="E:/LinguaFlow/backend" "D:/ProgramData/miniconda3/envs/py310/python.exe" -m pytest "E:/LinguaFlow/backend/tests"
```

前端构建：

```bash
npm --prefix "E:/LinguaFlow/frontend" run build
```

当前验证结果：
- 后端测试：4/4 通过
- 前端构建：通过

## 分阶段交付说明

### Phase 1: 搭建项目结构
- 已完成前后端目录骨架、FastAPI 入口、Vue 脚手架、术语种子和 README 初版。
- 运行命令：见“快速开始”。
- 测试方法：启动前后端并访问 `/api/health` 与前端首页。
- Git Commit Message:

```text
bootstrap runnable LinguaFlow project structure
```

### Phase 2: 实现前端页面
- 已完成首页、实时翻译页、历史记录页、设置页。
- 测试方法：运行前端，逐页检查路由和组件渲染。
- Git Commit Message:

```text
build frontend pages for realtime translation workflow
```

### Phase 3: 实现 FastAPI 服务
- 已完成健康检查、设置、术语、历史记录 REST API。
- 测试方法：运行后端并请求 `/api/settings`、`/api/terms`、`/api/history`。
- Git Commit Message:

```text
add FastAPI REST APIs for settings terms and history
```

### Phase 4: 实现 WebSocket
- 已完成 `/ws/realtime` 实时链路、连接管理与消息协议。
- 测试方法：使用实时翻译页调试文本注入，观察 `status -> asr -> translation -> correction`。
- Git Commit Message:

```text
implement realtime websocket subtitle pipeline
```

### Phase 5: 实现 Whisper 识别
- 已完成 provider 抽象和 OpenAI Whisper 接口接入；默认仍可用 mock 路径演示。
- 测试方法：配置 `ASR_PROVIDER=openai` 和 `OPENAI_API_KEY` 后用麦克风录音验证。
- Git Commit Message:

```text
add configurable ASR providers with OpenAI Whisper support
```

### Phase 6: 实现 AI 翻译
- 已完成 mock / OpenAI / Gemini 统一翻译接口。
- 测试方法：切换 `TRANSLATION_PROVIDER` 并验证术语优先翻译。
- Git Commit Message:

```text
add translation providers with terminology-aware prompts
```

### Phase 7: 实现字幕系统
- 已完成双语字幕面板、自动修正标记和人工修正弹窗。
- 测试方法：在实时翻译页连续输入上下文相关句子，观察旧字幕自动更新为 `[已修正]`。
- Git Commit Message:

```text
deliver bilingual subtitle UI with correction workflow
```

### Phase 8: 实现历史记录
- 已完成分页查询、删除、按会话删除、JSON 导出和历史片段人工修正。
- 测试方法：在历史页执行检索、删除、导出和修正操作。
- Git Commit Message:

```text
complete subtitle history management and export flow
```

### Phase 9: 生成部署方案
- 已补充部署文档与架构文档。
- 测试方法：按 [docs/deployment.md](docs/deployment.md) 执行本地或容器化部署。
- Git Commit Message:

```text
document deployment and architecture for MVP handoff
```

## 当前限制

- 浏览器实时音频链路已具备，但更稳定的流式断句与低延迟控制还需要进一步迭代。
- `faster-whisper` 目前仍保留为接口占位，尚未接入真实本地推理实现。
- 前端生产构建存在 chunk size 警告，但不影响运行；后续可做路由级拆包优化。
