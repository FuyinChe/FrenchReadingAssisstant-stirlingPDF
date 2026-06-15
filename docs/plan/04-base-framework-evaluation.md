# 04 — PDF 基座方案评估

## 决策（已更新 2026-06-13）

**优先采用 Stirling PDF**，以 **Fork + 插件式扩展** 实现法语 OCR / TTS / AI 侧栏，**不改动 Stirling 核心功能**。

详细集成方案见 **[06-stirling-integration-strategy.md](06-stirling-integration-strategy.md)**。

| 项 | 选择 |
|----|------|
| 基座 | Stirling PDF（submodule / fork） |
| 扩展方式 | `extensions/` 模块 + 工具注册 + engine router |
| 核心保护 | 命名空间隔离 + Feature Flag + 不修改现有 Controller |
| 备选 | 独立 sidecar（仅当 upstream 合并成本过高时） |

---

## 为何选择 Stirling PDF

| 维度 | 评价 |
|------|------|
| PDF 阅读体验 | ✅✅ 2.0 React SPA + PDF.js + FileContext |
| 工具生态 | ✅ 合并/拆分/OCR/转换等完整保留 |
| AI 能力 | ✅ Python Engine + Agent Chat 可复用 |
| 桌面版 | ✅ Tauri 开箱即用 |
| 区域框选 | ⚠️ 需新增 French Reader Tool（扩展模块） |
| 法语漫画 OCR | ⚠️ 默认 Tesseract 弱于 PaddleOCR，扩展 engine 解决 |
| 维护成本 | ⚠️ 需定期 sync upstream |

---

## 候选方案回顾

### 方案 A：Stirling PDF + 插件扩展 ✅ **已选**

**集成路径**（按推荐顺序）：

1. **引擎 + 前端 Tool**（MVP）：`engine/french_reader/` + 注册 `FrenchReader` Tool
2. **Java 薄代理**（M2+）：统一 8080 端口，参考 Agent Chat
3. **Sidecar 备选**：扩展独立容器，Stirling 零代码改动

**不适合**：修改 Stirling 共享 PDF Viewer 核心组件（高冲突）。

---

### 方案 B：独立 React + PDF.js + FastAPI

| 维度 | 评价 |
|------|------|
| 开发速度 | ✅ 最快 |
| Stirling 工具链 | ❌ 无法复用 |
| 状态 | **降为备选 / POC**，用于 isolated 验证 OCR 算法 |

可在 `extensions/french-reader-engine/` 内先用独立脚本验证 PaddleOCR，再接入 Stirling Tool。

---

### 方案 C：PDF.js Express / 商业 SDK

成本高，不推荐。

---

### 方案 D：参考 comic-translate

漫画气泡检测 + PaddleOCR 流水线，**作为 M5 算法参考**，UI 仍挂在 Stirling Tool 内。

---

## 决策矩阵（更新权重：复用 Stirling 体验）

| 标准 | 权重 | Stirling+插件 | 独立方案 |
|------|------|---------------|----------|
| PDF 阅读与工具体验 | 30% | 5 | 2 |
| 不破坏基座 / 可合并上游 | 25% | 4 | 5 |
| 法语 OCR+TTS 需求 | 25% | 4 | 5 |
| 桌面与部署 | 10% | 5 | 2 |
| MVP 速度 | 10% | 3 | 5 |
| **加权分** | | **4.3** | **3.7** |

---

## Stirling 集成检查清单

- [ ] 阅读上游 LICENSE
- [ ] `git submodule add` Stirling-PDF → `stirling-upstream/`
- [ ] 本地 dev：`task install && task dev`（JDK 25、Node、uv）
- [ ] 创建 `extensions/french-reader-engine/` + `french-reader-frontend/`
- [ ] `scripts/install-extensions.sh` 安装到 fork
- [ ] 注册 French Reader Tool（`useTranslatedToolRegistry.tsx`）
- [ ] engine 注册 `/french-reader/*` router
- [ ] （M2+）Java 代理 Controller
- [ ] E2E：Stirling 打开 PDF → French Reader Tool → 框选 → OCR → TTS
- [ ] `FRENCH_READER_ENABLED=false` 时核心功能回归测试

---

## 结论

| 阶段 | 基座选择 |
|------|----------|
| MVP ~ 发布 | **Stirling PDF + French Reader 插件模块** |
| OCR 算法验证 | 可在 engine 子包内独立 pytest，不必独立 App |
| 漫画自动检测 | engine + YOLO，UI 在 French Reader Tool |
| 上游同步 | 定期 `sync-upstream.sh`，冲突控制在注册/i18n |
