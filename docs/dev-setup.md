# 开发环境搭建

> **基座：** [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF)（`stirling-upstream/` 子模块）  
> **本仓库：** [FrenchReadingAssisstant-stirlingPDF](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF)  
> **用户文档：** [快速开始（中文）](zh/getting-started.md) · [Getting started (EN)](en/getting-started.md)

French Reading Assistant 在 **Stirling PDF submodule** 之上开发。French Reader 引擎默认以 **sidecar** 运行在 `:5002`，不修改 Stirling `engine/` 核心。

## 前置条件

| 依赖 | 用途 | 安装 |
|------|------|------|
| Git | submodule | 系统自带 |
| [Task](https://taskfile.dev/installation/) | Stirling 统一命令 | `brew install go-task` |
| Docker | 可选，Stirling 容器开发 | Docker Desktop |
| JDK 25 | Stirling 后端 | `brew install openjdk` |
| Node.js 20+ | Stirling 前端 | `brew install node` |
| [uv](https://docs.astral.sh/uv/) | French Reader engine | `brew install uv` |
| Rust + Tauri CLI | 可选，桌面打包 | 见 Stirling DeveloperGuide |

Stirling 可选系统依赖（OCR 等）：Tesseract、LibreOffice、qpdf — 见 [Stirling 开发文档](https://docs.stirlingpdf.com/Installation/Development%20Setup/)。

## 首次克隆

```bash
git clone --recursive https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF.git
cd FrenchReadingAssisstant-stirlingPDF
git submodule update --init --recursive   # 若 clone 时未带 --recursive
chmod +x scripts/*.sh
./scripts/install-extensions.sh
```

## 启动开发

```bash
# Stirling (8080 + 5173 + engine 5001) + French Reader engine (5002)
./scripts/dev.sh
```

或分步：

```bash
# 1. French Reader sidecar
cd extensions/french-reader-engine
uv sync --dev
uv run uvicorn french_reader.main:app --host 0.0.0.0 --port 5002 --reload

# 2. Stirling（另一终端）
cd stirling-upstream
task install
task dev
```

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `FRENCH_READER_ENABLED` | `true` | `false` 时不打 frontend patch、不启 sidecar |
| `VITE_FRENCH_READER_ENABLED` | 同左 | 前端构建/ dev 时隐藏 Tool |
| `FRENCH_READER_PORT` | `5002` | sidecar 端口（代码中 config.py 默认 5002） |
| `FRENCH_READER_CORS_ORIGINS` | `http://localhost:5173,...` | CORS |
| `FRENCH_READER_TTS_MAX_CHARS` | `5000` | TTS 单次文本上限 |
| `FRENCH_READER_LLM_API_KEY` | — | LLM API Key（未设则用 `OPENAI_API_KEY`） |
| `FRENCH_READER_LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容端点 |
| `FRENCH_READER_LLM_MODEL` | `gpt-4o-mini` | 模型名 |
| `FRENCH_READER_AI_MAX_CHARS` | `5000` | AI 单次文本上限 |

关闭扩展：

```bash
FRENCH_READER_ENABLED=false ./scripts/install-extensions.sh
cd stirling-upstream && task dev   # 行为接近上游
```

## 验证

| 检查 | URL / 命令 |
|------|------------|
| French Reader engine | `curl http://localhost:5002/health` |
| Stirling 前端 | http://localhost:5173 |
| Stirling 后端 | http://localhost:8080 |
| 扩展单元测试 | `cd extensions/french-reader-engine && uv run pytest` |
| 安装脚本 | `./scripts/install-extensions.sh` |

### OCR 引擎（M2+）

首次使用或遇到 `No OCR engine available` 时：

```bash
./scripts/setup-ocr.sh          # 安装 Tesseract + 法语包 (macOS: brew)
cd extensions/french-reader-engine && uv sync --dev
./scripts/dev.sh                # 重启 engine
```

检查 engine 状态：

```bash
curl http://localhost:5002/french-reader/ocr/engines
```

默认识别：**Tesseract (fra)**。可选更高精度 PaddleOCR：

```bash
cd extensions/french-reader-engine && uv sync --dev --extra ocr-paddle
```

### TTS 朗读（M3+）

需要 **网络**（edge-tts 调用 Microsoft Edge 在线语音）：

```bash
curl 'http://localhost:5002/french-reader/tts/voices?lang=fr'
curl -X POST http://localhost:5002/french-reader/tts/synthesize \
  -H 'Content-Type: application/json' \
  -d '{"text":"Bonjour!","voice":"fr-FR-DeniseNeural","rate":"+0%"}' \
  --output /tmp/french-tts.mp3
```

侧栏：OCR 完成后选择法语音色 → **Read aloud**（按 OCR 分句逐句朗读）。

### AI 翻译（M4+）

在项目根目录配置 **`.env`**（已 gitignore，勿提交密钥）：

```bash
cp .env.example .env
# 编辑 .env，填入 Kimi API Key
```

`.env` 示例（Kimi / Moonshot，香港可用 `api.moonshot.ai`）：

```bash
FRENCH_READER_LLM_API_KEY=sk-...
FRENCH_READER_LLM_BASE_URL=https://api.moonshot.ai/v1
FRENCH_READER_LLM_MODEL=moonshot-v1-32k
```

`./scripts/dev.sh` 启动时会自动 `source .env`。也可手动：

```bash
export FRENCH_READER_LLM_API_KEY=sk-...
export FRENCH_READER_LLM_BASE_URL=https://api.moonshot.ai/v1
export FRENCH_READER_LLM_MODEL=moonshot-v1-32k
./scripts/dev.sh
```

检查：

```bash
curl http://localhost:5002/french-reader/ai/status
```

侧栏 **Translation & notes**：模式 Translate / Vocabulary / Grammar，流式输出；无 Key 时显示黄色降级提示。

详见 [09-llm-integration-notes.md](plan/09-llm-integration-notes.md)。

Stirling 全量检查（耗时，可选）：

```bash
cd stirling-upstream && task check
```

## Docker 部署（M6）

```bash
cp .env.docker.example .env    # 可选
./scripts/docker-up.sh         # 或 ./scripts/docker-build.sh 仅构建
```

- 三服务：`stirling`（含 French Reader UI）+ `french-reader-engine` + `gateway`
- 对外端口：`8080`（可通过 `FRENCH_READER_HTTP_PORT` 修改）
- 首次构建 Stirling 扩展镜像可能需 30–60 分钟

详见 [用户手册（中文）](zh/user-guide.md)、[User guide (EN)](en/user-guide.md)、[deployment/sidecar-fallback.md](deployment/sidecar-fallback.md)。

## 桌面版（M6）

```bash
./scripts/build-desktop.sh     # Tauri 生产包
./scripts/desktop-dev.sh       # 开发（自动启动 sidecar :5002）
```

桌面模式需设置 `VITE_FRENCH_READER_API_URL=http://127.0.0.1:5002/french-reader`（脚本已默认）。

## 同步上游

```bash
./scripts/sync-upstream.sh
```

冲突时进入 `stirling-upstream/` 手动解决，再执行 `./scripts/install-extensions.sh`。

记录见 [development/sync-log.md](development/sync-log.md)。

## 架构要点

- **Sidecar engine**：`extensions/french-reader-engine/`，API 前缀 `/french-reader/*`  
- **Frontend 扩展**：复制到 `stirling-upstream/frontend/editor/src/...` + `patches/frontend/`  
- **不修改** Stirling Java 核心与 `engine/src/stirling/`（见 [07-license-compliance.md](plan/07-license-compliance.md)）

## 故障排除

| 问题 | 处理 |
|------|------|
| submodule 为空 | `git submodule update --init --recursive` |
| patch 已应用失败 | `cd stirling-upstream && git checkout -- frontend/editor/src/core` 后重装 |
| JDK 版本 | Stirling 2.0 要求 JDK 25 |
| port 占用 | 修改 `FRENCH_READER_PORT` 或停止占用进程 |
