# French Reading Assistant — 用户手册

在 Stirling PDF 中使用法语阅读增强工具：框选 → OCR → 朗读 → AI 释义。

## 使用前准备

| 方式 | 需要 |
|------|------|
| 开发环境 | `./scripts/dev.sh`（见 [dev-setup.md](dev-setup.md)） |
| Docker | `./scripts/docker-up.sh` |
| 桌面版 | 先 `./scripts/build-desktop.sh`，日常开发用 `./scripts/desktop-dev.sh` |

AI 功能需要 LLM API Key：在 Settings（齿轮）中选择厂商并保存，或在 `.env` 中配置 `FRENCH_READER_LLM_API_KEY`。

---

## 打开工具

1. 在 Stirling 中打开 PDF（与平时相同）。
2. 在工具列表中找到 **French Reading Assistant**（推荐工具分类）。
3. 进入后左侧为 PDF 画布，右侧为 AI 侧栏。

---

## 框选与 OCR

### 手动框选（推荐）

1. 在页面上拖拽矩形选区。
2. 系统自动对选区做法语 OCR，结果显示在右侧 **Recognized text**。

### 自动检测

侧栏 **AUTO DETECTORS** 区域：

| 按钮 | 用途 |
|------|------|
| **BUBBLES** | 漫画对话气泡 |
| **PARAGRAPHS** | 绘本/页面段落文字 |

- 勾选 **ENHANCE** 可启用预处理（复杂背景页）。
- 绿色虚线框为检测结果；仍建议重要内容用手动框选复核。
- 页面上方红色斜体提示：自动检测仅供参考，精确场景请手动框选。

---

## 朗读（TTS）

1. OCR 完成后，在 Settings 中选择法语音色与语速。
2. 点击 **Read aloud** 播放。
3. TTS 使用 edge-tts（需网络）。

---

## AI 释义

1. 在 Settings → **AI explanation** 中：
   - 选择模式：Translate / Vocabulary / Grammar（可多选）
   - 选择输出语言：中文或 English
   - 选择 **LLM provider**（默认 Kimi）并粘贴 API Key → **Save settings**
2. 回到侧栏，点击 **Explain**。
3. 流式结果按模式显示；可随时 **Stop**。

未配置 Key 时侧栏会显示黄色提示。

---

## 历史与导出

- 每次 OCR 会写入 **History**。
- 导出顺序：**PDF** → **Markdown** → **TXT**（侧栏导出菜单）。
- PDF 导出包含识别文本与已生成的 AI 释义。

---

## Settings 说明

| 区域 | 选项 |
|------|------|
| Pronunciation | 法语音色、语速 |
| AI explanation | 模式、语言、LLM 厂商下拉、API Key |
| LLM 厂商 | Kimi、OpenAI、Gemini、Claude、Copilot(Azure)、等 |

Copilot / Custom 需额外填写 Endpoint 与 Model/Deployment 名称。

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 无 French Reader 工具 | 确认 `FRENCH_READER_ENABLED=true` 且已运行 `install-extensions.sh` |
| OCR 失败 | 运行 `./scripts/setup-ocr.sh`；检查 engine `:5002` |
| AI 不可用 | Settings 填 Key 或配置 `.env` |
| Docker 打不开 Tool | 需使用本仓库构建的扩展镜像，不能用未打补丁的官方 Stirling 单镜像 |
| 桌面版 AI/OCR 无响应 | 需同时运行 sidecar（`desktop-dev.sh` 会自动启动） |

---

## 相关文档

- [开发环境](dev-setup.md)
- [Sidecar 降级部署](deployment/sidecar-fallback.md)
- [Docker 快速启动](../README.md#docker-部署)
