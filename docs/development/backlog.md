# 任务 Backlog

> 可执行工作项清单。基座：**Stirling PDF + 插件扩展**  
> 状态：`[ ]` 未开始 · `[~]` 进行中 · `[x]` 已完成 · `[-]` 已取消

最后更新：2026-06-13（策略调整为 Stirling 优先）

---

## M0 — Stirling 基座与扩展骨架（1–2 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M001 | 添加 `stirling-upstream` git submodule（Stirling-Tools/Stirling-PDF） | `.gitmodules` | 1h | [x] |
| TASK-M002 | 验证 Stirling dev：`task install && task dev` | 环境文档 `docs/dev-setup.md` | 4h | [x] |
| TASK-M003 | 阅读 LICENSE，编写 `docs/plan/07-license-compliance.md` | 合规说明 | 2h | [x] |
| TASK-M004 | 创建 `extensions/french-reader-engine/`（uv + 空 router） | Python 骨架 | 2h | [x] |
| TASK-M005 | 创建 `extensions/french-reader-frontend/`（空 FrenchReader.tsx） | React 骨架 | 2h | [x] |
| TASK-M006 | 编写 `scripts/install-extensions.sh`（复制/链接到 stirling-upstream） | 安装脚本 | 3h | [x] |
| TASK-M007 | 编写 `scripts/sync-upstream.sh` + `scripts/dev.sh` | 同步与启动 | 2h | [x] |
| TASK-M008 | engine 侧car :5002（不修改 Stirling engine 核心） | french_reader/main.py | 2h | [x] |
| TASK-M009 | 环境变量 `FRENCH_READER_ENABLED` 与 Tool 显示开关 | 功能开关 | 2h | [x] |
| TASK-M010 | CI：extensions 单元测试 + install 验证 | `.github/workflows/ci.yml` | 3h | [x] |

**M0 完成定义**：Stirling 正常运行；extensions 可安装；关闭 French Reader 时与上游一致。

---

## M1 — French Reader Tool 壳（1 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M101 | 调研 Stirling PDF viewer 组件 / hook 复用点 | 调研笔记 | 3h | [x] |
| TASK-M102 | 实现 `FrenchReader.tsx` 双栏布局（PDF + 侧栏占位） | Tool 主组件 | 4h | [x] |
| TASK-M103 | `useFrenchReaderOperation.ts`（ToolType.custom） | operation hook | 3h | [x] |
| TASK-M104 | 注册 Tool：`useTranslatedToolRegistry.tsx` + 分类/图标 | 工具可见 | 2h | [x] |
| TASK-M105 | i18n：`en` / `zh` 工具名与描述 | translation.json | 2h | [x] |
| TASK-M106 | FileContext 集成：读取当前 PDF，展示首页 | 无需重传 | 4h | [x] |
| TASK-M107 | 翻页、页码、缩放（复用或包装现有 viewer） | 阅读交互 | 6h | [x] |
| TASK-M108 | 冒烟：Merge/Split/OCR 三个 Stirling 原生 Tool 仍正常 | 回归清单 | 2h | [ ] |

**M1 完成定义**：Stirling 内打开 French Reader，能阅读已加载 PDF。

---

## M2 — 区域 OCR + 侧栏（2 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M201 | `RegionSelector` overlay（拖拽矩形） | 前端组件 | 6h | [x] |
| TASK-M202 | canvas 裁剪 → base64，坐标归一化 | 裁剪逻辑 | 4h | [x] |
| TASK-M203 | engine：PaddleOCR 封装 `ocr_service.py` | OCR 服务 | 4h | [x] |
| TASK-M204 | `POST /french-reader/ocr/region` + Pydantic schema | API | 3h | [x] |
| TASK-M205 | Vite proxy `/french-reader` → engine:5002 | 开发联调 | 2h | [x] |
| TASK-M206 | `AiSidePanel`：text、confidence、loading、复制 | 侧栏 UI | 4h | [x] |
| TASK-M207 | 选区完成 → 自动 OCR → 面板展开 | 联动 | 3h | [x] |
| TASK-M208 | OCR 后处理（法语断行、标点） | postprocess | 3h | [x] |
| TASK-M209 | `tests/test_ocr.py` 固定样例 snapshot | 测试 | 3h | [x] |
| TASK-M210 | （可选）Java `FrenchReaderProxyController` 转发 OCR | 统一 8080 | 4h | [ ] |
| TASK-M211 | 准备法语漫画测试页（版权合规） | 测试素材说明 | 2h | [ ] |

**M2 完成定义**：框选 → 侧栏法语 OCR 文本。

---

## M3 — TTS（1 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M301 | engine：`tts_service.py` + edge-tts | TTS 服务 | 3h | [x] |
| TASK-M302 | `POST /french-reader/tts/synthesize` | API | 2h | [x] |
| TASK-M303 | `GET /french-reader/tts/voices?lang=fr` | 音色列表 | 2h | [x] |
| TASK-M304 | 侧栏 `TtsPlayer`：播放/停止/音色 | UI | 4h | [x] |
| TASK-M305 | Java 代理 TTS 端点（若 M210 已做则复用模式） | 生产端口 | 2h | [ ] |
| TASK-M306 | 错误处理与文本长度限制 | 健壮性 | 2h | [x] |

**M3 完成定义**：OCR 文本一键法语朗读（**MVP 发布**）。

---

## M4 — AI 增强（1–2 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M401 | 调研 Stirling engine 现有 LLM 配置方式 | 笔记 | 2h | [x] |
| TASK-M402 | `POST /french-reader/ai/explain` + SSE | API | 4h | [x] |
| TASK-M403 | 翻译 / 词汇释义 prompt 模板 | prompts/ | 3h | [x] |
| TASK-M404 | 侧栏 AI 区块流式渲染 | UI | 4h | [x] |
| TASK-M405 | 无 LLM 配置时的降级 UI | 降级 | 2h | [x] |

---

## M5 — 漫画气泡（2 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M501 | YOLO 权重 + `bubble_detector.py` | 检测服务 | 6h | [ ] |
| TASK-M502 | `POST /french-reader/ocr/auto-bubbles` | API | 4h | [ ] |
| TASK-M503 | 前端「检测气泡」+ 可点击 bbox | UI | 6h | [ ] |
| TASK-M504 | 点击气泡 → OCR 链路 | 联动 | 3h | [ ] |
| TASK-M505 | OpenCV 预处理可选开关 | OCR 提升 | 4h | [ ] |

---

## M6 — 打包与上游同步（1 周）

| ID | 任务 | 产出 | 估时 | 状态 |
|----|------|------|------|------|
| TASK-M601 | Dockerfile 扩展层（基于 Stirling 镜像） | 部署 | 4h | [ ] |
| TASK-M602 | Tauri 桌面包含 French Reader Tool | 桌面 | 6h | [ ] |
| TASK-M603 | 执行一次 `sync-upstream.sh` 并记录冲突解决 | sync 日志 | 4h | [ ] |
| TASK-M604 | 用户手册：在 Stirling 中使用 French Reader | user-guide | 3h | [ ] |
| TASK-M605 | Sidecar 降级方案文档（零改 Stirling） | 备选 doc | 2h | [ ] |

---

## 技术债

| ID | 任务 | 优先级 | 状态 |
|----|------|--------|------|
| TASK-T001 | engine 服务端 PDF 页渲染（替代 client crop） | P2 | [ ] |
| TASK-T002 | Piper 离线 TTS | P2 | [ ] |
| TASK-T003 | 选区历史持久化 | P2 | [ ] |
| TASK-T004 | 向上游 Stirling 提交 Tool 贡献（可选） | P3 | [ ] |

---

## Sprint 建议

| Sprint | 范围 | 目标 |
|--------|------|------|
| Sprint 1 | M0 + M1 | Stirling + French Reader Tool 能读 PDF |
| Sprint 2 | M2 | 框选 OCR + 侧栏 |
| Sprint 3 | M3 | TTS（**MVP**） |
| Sprint 4 | M4 | AI 增强 |
| Sprint 5 | M5 + M6 | 漫画 + 打包/sync |

---

## 已废弃任务（独立 App 方案）

以下任务随策略调整 **取消**，改由 Stirling Tool 路径实现：

| 原 ID | 原任务 | 替代 |
|-------|--------|------|
| 旧 M001–M008 | 独立 frontend/backend/docker | M0 Stirling 基座任务 |
| 旧 M105–M107 | 独立文档上传/页渲染 API | FileContext + Stirling viewer |
| 旧 M603 | Stirling PoC | 已是主方案，见 M6 sync |
