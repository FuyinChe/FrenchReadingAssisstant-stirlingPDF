# 用户手册 — French Reading Assistant

在 [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF) 中使用法语阅读增强工具：框选 → OCR → 朗读 → AI 释义。

[User guide (EN)](../en/user-guide.md) · [快速开始](getting-started.md) · [截图规范](../images/README.md)

---

## 使用前准备

| 方式 | 命令 |
|------|------|
| 开发环境 | `./scripts/dev.sh`（见 [dev-setup.md](../dev-setup.md)） |
| Docker | `./scripts/docker-up.sh` |
| 桌面 / 便携版 | 运行 `Start French Reading Assistant` 启动脚本（见 [发行策略](../plan/10-distribution-strategy.md)） |

AI 功能需要 LLM API Key：Settings 中选择厂商并保存，或在 `.env` 中配置 `FRENCH_READER_LLM_API_KEY`。TTS 使用 edge-tts（需联网）。

---

## 打开工具

1. 在 Stirling 中打开 PDF（与平时相同）。
2. 在工具列表中找到 **French Reading Assistant**（**Recommended tools / 推荐工具**）。
3. 左侧为 PDF 画布，右侧为 AI 侧栏。

![法语阅读助手侧栏](../../screenshots/preview/002.png)

*图 1 — 阅读助手面板：自动检测、设置与历史。*

---

## 框选与 OCR

### 手动框选（推荐）

1. 在页面上拖拽矩形选区。
2. 系统自动对选区做法语 OCR，结果显示在 **Recognized text**。

![识别结果与 Explain / Stop](../../screenshots/preview/008.png)

*图 2 — OCR 结果、置信度与操作按钮。*

![完整界面 — OCR 后点击 Explain](../../screenshots/preview/009.png)

*图 3 — 对当前选区运行 AI 释义。*

### 自动检测

侧栏 **AUTO DETECTORS** 区域：

| 按钮 | 用途 |
|------|------|
| **BUBBLES** | 漫画对话气泡 |
| **PARAGRAPHS** | 绘本/页面段落文字 |

- 勾选 **Enhance page contrast before detection (OpenCV)** 可预处理复杂背景。
- 绿色虚线框为检测结果；重要内容仍建议手动框选复核。
- 页面上方红色斜体提示：自动检测仅供参考。

**漫画（气泡）**

![打开漫画 PDF，使用 BUBBLES](../../screenshots/preview/021.png)

*图 4 — 漫画页面：对对话气泡使用 BUBBLES。*

![气泡检测与 OCR 结果](../../screenshots/preview/022.png)

*图 5 — 检测气泡 → 逐气泡 OCR。*

**绘本（段落）**

![PARAGRAPHS + OpenCV 增强](../../screenshots/preview/004.png)

*图 6 — 段落检测（与 README 预览相同）。*

![段落页手动框选](../../screenshots/preview/025.png)

*图 7 — 段落式页面的手动框选。*

---

## 朗读（TTS）

1. OCR 完成后，打开 **Settings** → **Pronunciation** 中选择法语音色与语速。
2. 点击识别结果旁的扬声器图标（或 **Read aloud**）。
3. TTS 使用 edge-tts（需网络）。

![Settings 中的音色与语速](../../screenshots/preview/003.png)

*图 8 — 发音设置。*

---

## AI 释义

1. Settings → **AI explanation**：
   - 模式：Translate / Vocabulary / Grammar（可多选）
   - 输出语言：中文或 English
   - **LLM provider**（默认 Kimi）+ API Key → **Save settings**
2. 侧栏点击 **Explain**。
3. 流式结果按模式显示；可随时 **Stop**。

![选择 LLM 厂商](../../screenshots/preview/006.png)

*图 9 — LLM 厂商列表。*

![保存 API Key](../../screenshots/preview/007.png)

*图 10 — 填写 Key 并保存。*

![释义输出语言](../../screenshots/preview/010.png)

*图 11 — 选择释义显示语言。*

![翻译与词汇释义](../../screenshots/preview/011.png)

*图 12 — Translate + Vocabulary 面板。*

![词汇面板](../../screenshots/preview/012.png)

*图 13 — 词汇与音标。*

![语法面板](../../screenshots/preview/013.png)

*图 14 — 语法说明。*

**中文输出**

![中文释义（翻译 + 词汇）](../../screenshots/preview/017.png)

*图 15 — 输出语言设为中文。*

![中文语法说明](../../screenshots/preview/018.png)

*图 16 — 语法部分中文显示。*

**漫画工作流**

![漫画 — 中文翻译与词汇](../../screenshots/preview/023.png)

*图 17 — 漫画气泡的中文 AI 输出。*

![漫画 — 中文语法笔记](../../screenshots/preview/024.png)

*图 18 — 漫画对话的语法说明。*

未配置 Key 时侧栏显示黄色提示。

---

## 历史与导出

- 每次 OCR 写入 **History**。
- 导出顺序：**PDF** → **Markdown** → **TXT**（侧栏导出菜单）。
- PDF 导出包含识别文本与 AI 释义。

![识别历史](../../screenshots/preview/014.png)

*图 19 — 历史记录（亦见 README 预览）。*

![导出菜单](../../screenshots/preview/015.png)

*图 20 — PDF / Markdown / TXT 导出。*

![导出的 PDF（英文笔记）](../../screenshots/preview/016.png)

*图 21 — PDF 导出样例（亦见 README 预览）。*

![导出的 PDF（中文笔记）](../../screenshots/preview/020.png)

*图 22 — 含中文释义的 PDF。*

![历史中的中文翻译](../../screenshots/preview/019.png)

*图 23 — 历史面板中文翻译。*

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
| TTS 失败 | 确认联网；macOS 便携版请使用含 Web Audio 修复的最新构建 |
| Docker 无 Tool | 须使用本仓库构建的扩展镜像 |
| 桌面版无响应 | 需同时运行 sidecar / 便携启动脚本；macOS 请保持终端窗口打开 |

---

## 相关链接

- [Stirling PDF（上游基座）](https://github.com/Stirling-Tools/Stirling-PDF)
- [快速开始](getting-started.md)
- [Sidecar 降级部署](../deployment/sidecar-fallback.md)
- [截图索引](../../screenshots/README.md)
