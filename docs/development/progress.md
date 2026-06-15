# 开发进度追踪

> 每周或每个 Sprint 结束时更新。

## 当前状态

| 项 | 值 |
|----|-----|
| 当前阶段 | **M4 AI 翻译完成 → M5 气泡检测待开始** |
| 基座策略 | **Stirling PDF Fork + 插件扩展** |
| 最后更新 | 2026-06-13 |
| 阻塞项 | AI 需 `OPENAI_API_KEY`；TTS 需联网 |

## 里程碑进度

| 里程碑 | 状态 | 完成日期 | 备注 |
|--------|------|----------|------|
| M0 Stirling 基座与扩展骨架 | ✅ 完成 | 2026-06-13 | |
| M1 French Reader Tool 壳 | ✅ 完成 | 2026-06-13 | |
| M2 区域 OCR + 侧栏 | ✅ 完成 | 2026-06-13 | 框选 + sidecar OCR |
| M4 AI 增强 | ✅ 完成 | 2026-06-13 | 翻译 SSE + 侧栏 |
| M3 TTS | ✅ 完成 | 2026-06-13 | edge-tts + 侧栏播放 |
| M4 AI 增强 | ⬜ 未开始 | — | |
| M5 漫画气泡 | ⬜ 未开始 | — | |
| M6 打包与 upstream sync | ⬜ 未开始 | — | |

---

## 进行中任务

| ID | 负责人 | 开始日期 | 备注 |
|----|--------|----------|------|
| — | — | — | — |

---

## 已完成任务（最近）

| ID | 完成日期 | 备注 |
|----|----------|------|
| TASK-M401–M405 | 2026-06-13 | AI explain SSE + 翻译侧栏 |
| TASK-M301–M304, M306 | 2026-06-13 | edge-tts API + TtsPlayer 侧栏 |
| TASK-M201–M209 | 2026-06-13 | RegionSelector + OCR API + 侧栏结果 |
| TASK-M101–M107 | 2026-06-13 | M1 viewer 集成 |
| TASK-M001–M010 | 2026-06-13 | M0 骨架 |

---

## Sprint 日志

### Sprint 2（M2）— 2026-06-13

**完成**：

- [x] `POST /french-reader/ocr/region`（PaddleOCR → Tesseract 回退）
- [x] 当前页 `RegionSelector` + pdf.js 裁剪
- [x] 侧栏 OCR 结果、置信度、复制
- [x] Vite proxy `/french-reader` → `:5002`
- [x] engine 测试 6 passed

**下步（M3）**：edge-tts + 侧栏播放

### Sprint 3（M3）— 2026-06-13

**完成**：

- [x] `POST /french-reader/tts/synthesize`（edge-tts → audio/mpeg）
- [x] `GET /french-reader/tts/voices?lang=fr`
- [x] 侧栏 `TtsPlayer`：音色、语速、播放/停止
- [x] 按 OCR 分句逐句朗读（衔接 M2 标点分句）
- [x] 文本长度上限 5000 字符

**下步（M4）**：AI 释义 / 翻译侧栏

### Sprint 4（M4）— 2026-06-13

**完成**：

- [x] `POST /french-reader/ai/explain`（OpenAI 兼容 SSE）
- [x] `GET /french-reader/ai/status`
- [x] prompt 模板：translate / vocabulary / grammar
- [x] 侧栏 `AiTranslationPanel` 流式展示 + 无 Key 降级
- [x] 笔记 [09-llm-integration-notes.md](../plan/09-llm-integration-notes.md)

**下步（M5）**：漫画气泡自动检测

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-13 | M4：AI 翻译 / 释义 SSE |
| 2026-06-13 | M3：edge-tts 法语朗读 |
| 2026-06-13 | M2：区域框选 OCR 全链路 |
| 2026-06-13 | M1 / M0 |
