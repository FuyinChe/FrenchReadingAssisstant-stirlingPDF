# 08 — Stirling Viewer 集成调研（M1）

## 结论

French Reader **复用 Stirling 原生 EmbedPDF Viewer**，扩展内容放在 **右侧 Tool 面板**（`RightSidebar` → `ToolRenderer`），与 Annotate / Read 工具一致。

| 能力 | Stirling 来源 | French Reader 用法 |
|------|---------------|-------------------|
| PDF 渲染 | `Workbench` → `Viewer` → `EmbedPdfViewer` | `workbench: "viewer"` 自动切换 |
| 当前文件 | `FileContext` + `useViewScopedFiles` | 单 PDF，`maxFiles: 1` |
| 页码 / 缩放 | `ViewerContext` scroll/zoom actions | `useFrenchReaderPageState` |
| 工具 UI | `createToolFlow` + 侧栏 steps | `AiSidePanel` |
| 区域框选 | EmbedPDF overlay（待 M2） | 暂不改动 Viewer 核心 |

## 参考实现

- **Read 工具**：`workbench: "viewer"`, `component: null` — 仅切视图  
- **Annotate 工具**：`workbench: "viewer"` + `createToolFlow` + `AnnotationPanel`  
- **French Reader**：Annotate 模式 — viewer 居中，助手面板在侧栏  

## 数据流（M1）

```
用户选择 French Reader
  → FrenchReader.tsx 检测 FileContext 有文件
  → setWorkbench("viewer")
  → 中央 EmbedPDF 显示 PDF
  → 侧栏 AiSidePanel 显示文件名、页码、缩放
```

## M2 预留

- 在 Viewer 上叠加 `RegionSelector`（需调研 EmbedPDF 页面坐标 API 或 canvas overlay）
- OCR 请求发往 sidecar `:5002/french-reader/ocr/region`

## 文件映射（extensions → stirling-upstream）

| 扩展源 | 安装目标 |
|--------|----------|
| `src/tools/FrenchReader.tsx` | `src/tools/frenchReader/` |
| `src/components/frenchReader/*` | `src/components/frenchReader/` |
| `src/hooks/tools/frenchReader/*` | `src/hooks/tools/frenchReader/` |
| `src/extensions/french-reader/*` | `src/extensions/french-reader/` |
