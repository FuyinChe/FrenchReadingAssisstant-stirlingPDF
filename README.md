# FrenchPdfReader

面向法语 PDF（尤其是漫画 / BD）的智能阅读增强模块，**以 [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) 为基座**，以插件形式挂载：区域框选 → 法语 OCR → 右侧 AI 面板 → TTS 朗读。

**不改动 Stirling 核心功能**；扩展代码隔离在 `extensions/`，通过新 Tool + sidecar engine（:5002）接入。

## 功能概览

- **Stirling PDF 全功能保留**：合并、拆分、转换、原生 OCR、AI Agent、Tauri 桌面等
- **French Reader Tool**（新增）：框选法语区域、侧栏展示 OCR、TTS、AI 释义
- **漫画增强**（规划）：YOLO 气泡自动检测

## 文档

| 文档 | 说明 |
|------|------|
| [文档中心](docs/README.md) | 导航 |
| [Stirling 集成策略](docs/plan/06-stirling-integration-strategy.md) | **核心**：插件/Fork 方案 |
| [架构设计](docs/plan/02-architecture.md) | 模块与 API |
| [基座评估](docs/plan/04-base-framework-evaluation.md) | 为何选 Stirling |
| [任务 Backlog](docs/development/backlog.md) | 可执行工作项 |
| [进度追踪](docs/development/progress.md) | 当前状态 |

## 技术方向

```
基座:      Stirling PDF (submodule → stirling-upstream/)
扩展:      extensions/french-reader-frontend/  (React Tool)
           extensions/french-reader-engine/    (FastAPI: OCR/TTS/AI)
Python:    PaddleOCR (fr) + edge-tts
集成原则:  命名空间隔离 + FRENCH_READER_ENABLED 开关 + 最小 patch
```

## 快速开始

```bash
git submodule update --init --recursive
chmod +x scripts/*.sh
./scripts/install-extensions.sh
./scripts/dev.sh
```

详见 [docs/dev-setup.md](docs/dev-setup.md)。

## 状态

**M0 基本完成** — submodule、extensions、安装脚本、CI 已就绪；待本机验证 Stirling `task dev`。
