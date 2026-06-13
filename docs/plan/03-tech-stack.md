# 03 — 技术选型

## 语言与运行时

| 层级 | 选择 | 理由 |
|------|------|------|
| **基座** | **Stirling PDF**（Spring Boot + React + Engine） | 完整 PDF 工具链 + 阅读体验 + Tauri |
| 扩展主开发 | **Python 3.11+**（`extensions/french-reader-engine/`） | OCR/TTS/AI |
| 扩展前端 | **TypeScript + React**（Stirling Tool 组件） | 复用 Mantine、FileContext、PDF.js |
| Java | 仅薄代理（可选） | 统一 8080，参考 Agent Chat |
| 桌面 | **Stirling Tauri** | 扩展随 Fork 打包 |

## 后端依赖（Python）

### 核心框架

```toml
# pyproject.toml 建议依赖
fastapi >= 0.110
uvicorn[standard] >= 0.27
python-multipart          # PDF 上传
pydantic >= 2.0
```

### PDF 处理

| 库 | 用途 |
|----|------|
| **PyMuPDF (fitz)** | 页渲染为 PNG、裁剪、高性能 |
| pdf2image + poppler | 备选渲染方案 |
| pypdf | 轻量元数据读取 |

### OCR（法语 + 漫画）

| 库 | 场景 | 备注 |
|----|------|------|
| **PaddleOCR** | 默认法语 OCR | `lang=fr`，漫画清晰页效果好 |
| Tesseract 5 + `fra` | 备选 / Stirling 已有 | 集成简单，漫画弱于 Paddle |
| ocrmypdf + paddleocr 插件 | 整页 OCR 预处理 | 可选，生成 searchable PDF |

**漫画气泡（P1）**：

| 库 | 用途 |
|----|------|
| ultralytics (YOLOv8) | 气泡检测 |
| ogkalu/comic-speech-bubble-detector-yolov8m | 预训练权重 |

### TTS（法语）

| 库 | 离线 | 质量 |
|----|------|------|
| **edge-tts** | 否 | 高（MVP 默认） |
| piper-tts | 是 | 中高 |
| gTTS | 否 | 中 |

### AI 增强（P1）

| 库 | 用途 |
|----|------|
| openai / anthropic SDK | 可选云端 LLM |
| ollama | 本地 LLM |
| spaCy `fr_core_news_sm` | 分词、词性 |

### 测试与质量

```toml
pytest >= 8.0
pytest-asyncio
httpx                    # FastAPI 测试客户端
ruff                     # lint + format
mypy                     # 可选类型检查
```

## 前端依赖

```json
{
  "react": "^18",
  "pdfjs-dist": "^4",
  "axios": "^1",
  "@tanstack/react-query": "^5",
  "zustand": "^4",
  "tailwindcss": "^3"
}
```

- **pdfjs-dist**：Mozilla PDF.js，canvas 渲染
- **react-query**：OCR/TTS 请求缓存与 loading 状态
- **zustand**：侧栏开关、当前选区、播放状态

## 基础设施

| 工具 | 用途 |
|------|------|
| Docker Compose | 一键启动 frontend + backend |
| Taskfile / Makefile | 统一 dev 命令 |
| GitHub Actions | CI：lint、pytest、前端 build |

## 开发环境要求

- Python 3.11+，推荐 [uv](https://docs.astral.sh/uv/) 管理依赖
- Node.js 20+
- Poppler（pdf2image 备选）
- 可选：CUDA（PaddleOCR GPU 加速）

## 许可证注意事项

| 组件 | 许可证 | 影响 |
|------|--------|------|
| Stirling PDF | 见上游仓库 | Fork 需遵守其许可证 |
| PaddleOCR | Apache 2.0 | 商用友好 |
| PDF.js | Apache 2.0 | 商用友好 |
| YOLOv8 | AGPL-3.0（ultralytics） | 分发需注意 |

## 推荐 MVP 技术栈摘要

```
基座:      Stirling PDF (task dev: Java 8080 + Vite 5173 + engine 5001)
扩展 FE:   French Reader Tool @ extensions/french-reader-frontend/
扩展 BE:   french_reader router @ extensions/french-reader-engine/
OCR/TTS:   PaddleOCR (fr) + edge-tts
Deploy:    Stirling Docker + 扩展层 / Tauri 桌面
```

详见 [06-stirling-integration-strategy.md](06-stirling-integration-strategy.md)。
