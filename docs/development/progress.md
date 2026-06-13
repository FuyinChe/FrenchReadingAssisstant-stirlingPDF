# 开发进度追踪

> 每周或每个 Sprint 结束时更新。

## 当前状态

| 项 | 值 |
|----|-----|
| 当前阶段 | **M2 完成 → M3 TTS 待开始** |
| 基座策略 | **Stirling PDF Fork + 插件扩展** |
| 最后更新 | 2026-06-13 |
| 阻塞项 | 本地 OCR 需安装 `uv sync --extra ocr`（PaddleOCR 或 Tesseract） |

## 里程碑进度

| 里程碑 | 状态 | 完成日期 | 备注 |
|--------|------|----------|------|
| M0 Stirling 基座与扩展骨架 | ✅ 完成 | 2026-06-13 | |
| M1 French Reader Tool 壳 | ✅ 完成 | 2026-06-13 | |
| M2 区域 OCR + 侧栏 | ✅ 完成 | 2026-06-13 | 框选 + sidecar OCR |
| M3 TTS | ⬜ 未开始 | — | MVP 截止 |
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

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-13 | M2：区域框选 OCR 全链路 |
| 2026-06-13 | M1 / M0 |
