# LinguaFlow 部署方案

## 本地开发部署

### 后端

```bash
"D:/ProgramData/miniconda3/envs/py310/python.exe" -m pip install -r "E:/LinguaFlow/backend/requirements.txt"
PYTHONPATH="E:/LinguaFlow/backend" "D:/ProgramData/miniconda3/envs/py310/python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
npm --prefix "E:/LinguaFlow/frontend" install
npm --prefix "E:/LinguaFlow/frontend" run dev
```

## 生产部署建议

### 推荐拓扑

- 前端：静态托管
  - Vercel
  - Netlify
  - Nginx 静态站点
- 后端：长期在线容器或虚拟机
  - Docker 容器
  - 云主机
  - 内网服务器
- 数据库：SQLite 适合 MVP
  - 生产建议至少将数据库文件映射到持久卷

原因：
- WebSocket 长连接不适合多数无状态 serverless 场景
- OpenAI Whisper / 翻译调用需要稳定出站网络
- 若后续接入 `faster-whisper`，更需要固定计算资源

## 环境变量

复制 `backend/.env.example` 为 `.env`，至少配置：

```env
ASR_PROVIDER=mock
TRANSLATION_PROVIDER=mock
DATABASE_URL=sqlite:///./linguaflow.db
OPENAI_API_KEY=
GEMINI_API_KEY=
```

如果使用真实 provider：

```env
ASR_PROVIDER=openai
TRANSLATION_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_TRANSLATION_MODEL=gpt-4o-mini
OPENAI_WHISPER_MODEL=whisper-1
```

或：

```env
TRANSLATION_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-1.5-flash
```

## 前端环境变量

前端通过 `VITE_API_BASE_URL` 指向后端地址，例如：

```env
VITE_API_BASE_URL=https://your-api.example.com
```

## 反向代理建议

如果使用 Nginx：
- `/` 代理到前端静态资源
- `/api/` 代理到 FastAPI
- `/ws/realtime` 开启 WebSocket upgrade

关键点：
- `proxy_http_version 1.1`
- `Upgrade` / `Connection` 头必须透传

## 数据持久化

SQLite 文件默认位于后端工作目录。

建议：
- 将 `linguaflow.db` 放在持久磁盘目录
- 定期备份数据库文件
- 导出 JSON 作为额外归档

## 容器化建议

当前仓库未强制加入 Docker 配置，但推荐后续补充：
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`

推荐 compose 结构：
- `frontend` 服务暴露 5173 或构建后交给 Nginx
- `backend` 服务暴露 8000
- `backend` 挂载 SQLite 持久卷

## 上线前检查清单

1. 后端健康检查 `/api/health` 返回正常
2. 前端能够连接 `/ws/realtime`
3. mock 模式可以完整跑通一轮字幕链路
4. 若使用 OpenAI/Gemini，确认密钥和网络可用
5. 检查浏览器麦克风权限
6. 检查历史记录写入与导出 JSON
7. 检查自动修正与人工修正都可回写历史

## 当前已验证

- 后端测试通过
- 前端生产构建通过
- WebSocket 调试文本路径通过自动化测试

## 后续上线优化建议

- 使用 PostgreSQL 替代 SQLite
- 引入日志与请求追踪
- 为 provider 调用增加限流和重试策略
- 为前端做 chunk 拆分与资源压缩优化
- 为实时音频链路增加更稳定的分段与断句策略
