# 05 — 里程碑与阶段验收

## 总览

基座：**Stirling PDF Fork + French Reader 插件模块**

| 阶段 | 名称 | 周期（估） | 交付物 |
|------|------|------------|--------|
| M0 | Stirling 基座与扩展骨架 | 1–2 周 | submodule、dev 环境、extensions 目录 |
| M1 | French Reader Tool 壳 | 1 周 | 注册 Tool + FileContext 读 PDF |
| M2 | 区域 OCR + 侧栏 | 2 周 | 框选 + engine OCR + AiSidePanel |
| M3 | TTS | 1 周 | 法语朗读 |
| M4 | AI 增强 | 1–2 周 | 释义/翻译（复用 engine LLM） |
| M5 | 漫画气泡 | 2 周 | YOLO 检测 + 点选 OCR |
| M6 | 打包与上游同步 | 1 周 | Docker/Tauri、sync 文档 |

**MVP = M0 + M1 + M2 + M3**（约 5–7 周）

---

## M0 — Stirling 基座与扩展骨架

**目标**：Fork/submodule 就绪，扩展可安装，Stirling 核心可正常运行。

**验收标准**：

- [ ] `stirling-upstream/` submodule 指向 Stirling-PDF
- [ ] `task install && task dev` 可启动 Stirling（8080 + 5173 + engine 5001）
- [ ] `extensions/french-reader-engine/`、`french-reader-frontend/` 骨架存在
- [ ] `scripts/install-extensions.sh` 可执行（即使尚未注册 Tool）
- [ ] 阅读 LICENSE，记录合规说明
- [ ] `FRENCH_READER_ENABLED=false` 时与上游行为一致

---

## M1 — French Reader Tool 壳

**目标**：在 Stirling 工具列表中出现「French Reader」，能打开当前 PDF。

**验收标准**：

- [ ] Tool 已注册（`useTranslatedToolRegistry.tsx` + i18n）
- [ ] 从 FileContext 加载已打开 PDF，无需重新上传
- [ ] 页面布局：左侧 PDF 视图 + 右侧空白侧栏占位
- [ ] 翻页、缩放可用（复用或嵌入 Stirling PDF  viewer 能力）
- [ ] Stirling 其他 Tool 不受影响（冒烟测试 3 个常用工具）

---

## M2 — 区域 OCR + 侧栏

**目标**：核心差异化功能。

**验收标准**：

- [ ] RegionSelector 拖拽框选，坐标归一化
- [ ] engine `POST /french-reader/ocr/region` 返回法语文本
- [ ] PaddleOCR `lang=fr` 集成
- [ ] AiSidePanel 展示 text、confidence、复制
- [ ] 选区完成自动 OCR、面板展开
- [ ] 10 页漫画/BD 抽样可用

---

## M3 — TTS

**验收标准**：

- [ ] engine `POST /french-reader/tts/synthesize`
- [ ] 侧栏朗读/停止，法语音色可选
- [ ] 首字延迟 < 2s

---

## M4 — AI 增强

**验收标准**：

- [ ] 复用 engine LLM 配置
- [ ] 翻译/释义至少 2 种 mode
- [ ] SSE 流式展示；无 Key 时降级

---

## M5 — 漫画气泡

**验收标准**：

- [ ] YOLO 气泡检测 API + 前端可点击 bbox
- [ ] 点击 → OCR → 侧栏

---

## M6 — 打包与上游同步

**验收标准**：

- [ ] Docker 镜像含 French Reader 扩展
- [ ] Tauri 桌面包可打开 French Reader Tool
- [ ] `sync-upstream.sh` 文档 + 一次成功 sync 记录
- [ ] `task check` 通过

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| upstream 合并冲突 | 扩展隔离 + patches/ + 定期 sync |
| Stirling 无官方插件 API | 遵循 ADDING_TOOLS.md，触点最小化 |
| JDK 25 / 环境重 | 文档化 `task dev`，Docker 备选 |
| Tesseract vs Paddle 重复 | French Reader 专用 Paddle，不动 Stirling OCR 工具 |

---

## 下一步

执行 [backlog.md](../development/backlog.md) **M0（Stirling 版）** 任务组。

## 参考

- [06-stirling-integration-strategy.md](06-stirling-integration-strategy.md)
