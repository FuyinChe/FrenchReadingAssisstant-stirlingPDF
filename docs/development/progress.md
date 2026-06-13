# 开发进度追踪

> 每周或每个 Sprint 结束时更新。

## 当前状态

| 项 | 值 |
|----|-----|
| 当前阶段 | **M1 完成 → M2 区域 OCR 待开始** |
| 基座策略 | **Stirling PDF Fork + 插件扩展** |
| 当前 Sprint | Sprint 2 准备 |
| 最后更新 | 2026-06-13 |
| 阻塞项 | 无 |

## 里程碑进度

| 里程碑 | 状态 | 完成日期 | 备注 |
|--------|------|----------|------|
| M0 Stirling 基座与扩展骨架 | ✅ 完成 | 2026-06-13 | |
| M1 French Reader Tool 壳 | ✅ 完成 | 2026-06-13 | Viewer + 侧栏助手 |
| M2 区域 OCR + 侧栏 | ⬜ 未开始 | — | 下一步 |
| M3 TTS | ⬜ 未开始 | — | MVP 截止 |
| M4 AI 增强 | ⬜ 未开始 | — | |
| M5 漫画气泡 | ⬜ 未开始 | — | |
| M6 打包与 upstream sync | ⬜ 未开始 | — | |

---

## 进行中任务

| ID | 负责人 | 开始日期 | 备注 |
|----|--------|----------|------|
| TASK-M108 | — | — | 可选：Merge/Split/OCR 冒烟回归 |

---

## 已完成任务（最近 10 条）

| ID | 完成日期 | 备注 |
|----|----------|------|
| TASK-M107 | 2026-06-13 | ViewerControls：页码 + 缩放 |
| TASK-M106 | 2026-06-13 | FileContext + auto viewer |
| TASK-M102–M105 | 2026-06-13 | FrenchReader + registry + i18n defaults |
| TASK-M101 | 2026-06-13 | docs/plan/08-viewer-integration-notes.md |
| TASK-M002 | 2026-06-13 | 用户确认 dev 启动成功 |
| TASK-M001 | 2026-06-13 | submodule |
| TASK-M003–M010 | 2026-06-13 | M0 骨架 |

---

## Sprint 日志

### Sprint 1（M0 + M1）— 2026-06-13

**完成**：

- [x] M0：submodule、extensions、scripts、CI
- [x] M1：EmbedPDF viewer 集成、AiSidePanel、页码/缩放控制
- [x] 用户验证：`./scripts/dev.sh` 可启动 French Reader

**下步（M2）**：

- [ ] RegionSelector overlay
- [ ] engine `POST /french-reader/ocr/region`
- [ ] 侧栏展示 OCR 文本

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-13 | M1：viewer 模式 + Reading assistant 侧栏 |
| 2026-06-13 | M0 骨架；engine sidecar |
