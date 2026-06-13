# 开发环境搭建

FrenchPdfReader 在 **Stirling PDF submodule** 之上开发。French Reader 引擎默认以 **sidecar** 运行在 `:5002`，不修改 Stirling `engine/` 核心。

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
git clone <this-repo-url> FrenchPdfReader
cd FrenchPdfReader
git submodule update --init --recursive
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

Stirling 全量检查（耗时，可选）：

```bash
cd stirling-upstream && task check
```

## 同步上游

```bash
./scripts/sync-upstream.sh
```

冲突时进入 `stirling-upstream/` 手动解决，再执行 `./scripts/install-extensions.sh`。

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
