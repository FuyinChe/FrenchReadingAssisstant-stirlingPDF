# 开发进度追踪

> 每周或每个 Sprint 结束时更新。

## 当前状态

| 项 | 值 |
|----|-----|
| 当前阶段 | **M0 — 基本完成，待 Stirling dev 验证** |
| 基座策略 | **Stirling PDF Fork + 插件扩展** |
| 当前 Sprint | Sprint 1 准备 |
| 最后更新 | 2026-06-13 |
| 阻塞项 | 本地需 JDK 25 + Task + uv 以跑满 Stirling `task dev` |

## 里程碑进度

| 里程碑 | 状态 | 完成日期 | 备注 |
|--------|------|----------|------|
| M0 Stirling 基座与扩展骨架 | 🟡 进行中 | — | submodule + extensions + scripts + CI |
| M1 French Reader Tool 壳 | ⬜ 未开始 | — | |
| M2 区域 OCR + 侧栏 | ⬜ 未开始 | — | |
| M3 TTS | ⬜ 未开始 | — | MVP 截止 |
| M4 AI 增强 | ⬜ 未开始 | — | |
| M5 漫画气泡 | ⬜ 未开始 | — | |
| M6 打包与 upstream sync | ⬜ 未开始 | — | |

---

## 进行中任务

| ID | 负责人 | 开始日期 | 备注 |
|----|--------|----------|------|
| TASK-M002 | — | 2026-06-13 | 需本机 `task install && task dev` 验证 |

---

## 已完成任务（最近 10 条）

| ID | 完成日期 | 备注 |
|----|----------|------|
| TASK-M001 | 2026-06-13 | stirling-upstream submodule |
| TASK-M003 | 2026-06-13 | docs/plan/07-license-compliance.md |
| TASK-M004 | 2026-06-13 | extensions/french-reader-engine |
| TASK-M005 | 2026-06-13 | extensions/french-reader-frontend |
| TASK-M006 | 2026-06-13 | scripts/install-extensions.sh |
| TASK-M007 | 2026-06-13 | scripts/sync-upstream.sh + dev.sh |
| TASK-M008 | 2026-06-13 | sidecar engine :5002（不修改 Stirling engine 核心） |
| TASK-M009 | 2026-06-13 | FRENCH_READER_ENABLED / VITE_FRENCH_READER_ENABLED |
| TASK-M010 | 2026-06-13 | .github/workflows/ci.yml |
| — | 2026-06-13 | docs/dev-setup.md |

---

## Sprint 日志

### Sprint 0（M0 骨架）— 2026-06-13

**完成**：

- [x] Stirling submodule
- [x] extensions 引擎 + 前端骨架
- [x] install / sync / dev 脚本
- [x] 前端 Tool 注册 patch（prototypeToolId + usePrototypeToolRegistry）
- [x] engine 侧car + pytest 2 passed
- [x] CI workflow
- [x] 许可证合规文档

**待办**：

- [ ] TASK-M002：本机验证 Stirling `task dev` + French Reader Tool 出现在 UI

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-13 | M0 骨架落地；engine 采用 sidecar 避免修改 Stirling engine 专有代码 |
