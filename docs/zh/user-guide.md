# 用户手册 — French Reading Assistant

在 [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF) 中使用法语阅读增强工具：框选 → OCR → 朗读 → AI 释义。

[User guide (EN)](../en/user-guide.md) · [快速开始](getting-started.md) · [截图规范](../images/README.md)

---

## 使用前准备

| 方式 | 命令 |
|------|------|
| 开发环境 | `./scripts/dev.sh`（见 [dev-setup.md](../dev-setup.md)） |
| Docker | `./scripts/docker-up.sh` |
| 桌面版 | `./scripts/build-desktop.sh`，日常 `./scripts/desktop-dev.sh` |

AI 功能需要 LLM API Key：Settings 中选择厂商并保存，或在 `.env` 中配置 `FRENCH_READER_LLM_API_KEY`。

---

## 打开工具

1. 在 Stirling 中打开 PDF（与平时相同）。
2. 在工具列表中找到 **French Reading Assistant**（**Recommended tools / 推荐工具**）。
3. 左侧为 PDF 画布，右侧为 AI 侧栏。

<!-- 截图：docs/images/user-guide/zh/01-open-tool.png -->

*图 1 — 推荐工具 → French Reading Assistant。截图路径：`docs/images/user-guide/zh/01-open-tool.png`（待补充）。*

---

## 框选与 OCR

### 手动框选（推荐）

1. 在页面上拖拽矩形选区。
2. 系统自动对选区做法语 OCR，结果显示在 **Recognized text**。

<!-- 截图：docs/images/user-guide/zh/02-manual-selection.png -->

*图 2 — 手动框选与 OCR 结果（待补充截图）。*

### 自动检测

侧栏 **AUTO DETECTORS** 区域：

| 按钮 | 用途 |
|------|------|
| **BUBBLES** | 漫画对话气泡 |
| **PARAGRAPHS** | 绘本/页面段落文字 |

- 勾选 **ENHANCE** 可启用预处理（复杂背景页）。
- 绿色虚线框为检测结果；重要内容仍建议手动框选复核。
- 页面上方红色斜体提示：自动检测仅供参考。

<!-- 截图：docs/images/user-guide/zh/03-auto-detectors.png -->

*图 3 — 气泡 / 段落检测（待补充截图）。*

---

## 朗读（TTS）

1. OCR 完成后，在 Settings 中选择法语音色与语速。
2. 点击 **Read aloud** 播放。
3. TTS 使用 edge-tts（需网络）。

<!-- 截图：docs/images/user-guide/zh/04-tts-read-aloud.png -->

*图 4 — TTS 设置与朗读（待补充截图）。*

---

## AI 释义

1. Settings → **AI explanation**：
   - 模式：Translate / Vocabulary / Grammar（可多选）
   - 输出语言：中文或 English
   - **LLM provider**（默认 Kimi）+ API Key → **Save settings**
2. 侧栏点击 **Explain**。
3. 流式结果按模式显示；可随时 **Stop**。

未配置 Key 时侧栏显示黄色提示。

<!-- 截图：docs/images/user-guide/zh/05-ai-explain.png -->

*图 5 — LLM 设置与释义输出（待补充截图）。*

---

## 历史与导出

- 每次 OCR 写入 **History**。
- 导出顺序：**PDF** → **Markdown** → **TXT**（侧栏导出菜单）。
- PDF 导出包含识别文本与 AI 释义。

<!-- 截图：docs/images/user-guide/zh/06-history-export.png -->

*图 6 — 历史与导出（待补充截图）。*

---

## Settings 说明

| 区域 | 选项 |
|------|------|
| Pronunciation | 法语音色、语速 |
| AI explanation | 模式、语言、LLM 厂商、API Key |
| LLM 厂商 | Kimi、OpenAI、Gemini、Claude、Copilot(Azure) 等 |

Copilot / Custom 需填写 Endpoint 与 Model/Deployment 名称。

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 无 French Reader 工具 | 确认 `FRENCH_READER_ENABLED=true` 且已运行 `install-extensions.sh` |
| OCR 失败 | `./scripts/setup-ocr.sh`；检查 engine `:5002` |
| AI 不可用 | Settings 填 Key 或配置 `.env` |
| Docker 无 Tool | 须使用本仓库构建的扩展镜像，不能用未打补丁的官方 Stirling 单镜像 |
| 桌面版无响应 | 需同时运行 sidecar（`desktop-dev.sh` 会自动启动） |

---

## 相关链接

- [Stirling PDF（上游基座）](https://github.com/Stirling-Tools/Stirling-PDF)
- [快速开始](getting-started.md)
- [Sidecar 降级部署](../deployment/sidecar-fallback.md)
- [补充截图](../images/README.md)
