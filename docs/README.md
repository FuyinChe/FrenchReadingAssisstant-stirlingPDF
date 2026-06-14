# FrenchPdfReader 文档中心

法语 PDF 阅读器（侧重漫画/BD）的项目文档索引。所有计划与开发进度均在此目录维护。

## 目录结构

```
docs/
├── README.md                 # 本文件：文档导航
├── plan/                     # 计划类文档（相对稳定，变更需评审）
│   ├── 01-project-overview.md
│   ├── 02-architecture.md
│   ├── 03-tech-stack.md
│   ├── 04-base-framework-evaluation.md
│   ├── 05-milestones.md
│   ├── 06-stirling-integration-strategy.md
│   └── 07-license-compliance.md
├── dev-setup.md              # 开发环境搭建
├── user-guide.md             # 用户使用手册（M6）
├── deployment/
│   └── sidecar-fallback.md   # Sidecar 降级部署
└── development/
    ├── README.md
    ├── backlog.md            # 可执行任务清单（主 backlog）
    ├── progress.md           # 进度追踪与周报
    └── sync-log.md           # 上游同步记录（M603）
```

## 阅读顺序（新成员 onboarding）

1. [项目概述](plan/01-project-overview.md) — 目标、用户场景、核心功能
2. [架构设计](plan/02-architecture.md) — 模块划分与数据流
3. [技术选型](plan/03-tech-stack.md) — 语言、库、服务
4. [基座方案评估](plan/04-base-framework-evaluation.md) — 为何优先 Stirling
5. **[Stirling 集成策略](plan/06-stirling-integration-strategy.md)** — 插件挂载、目录、触点
6. [里程碑](plan/05-milestones.md) — 阶段目标与验收标准
7. [开发环境](dev-setup.md) — Stirling + 扩展安装启动
8. [用户手册](user-guide.md) — 框选、OCR、TTS、AI、导出
9. [任务 Backlog](development/backlog.md) — 可执行工作项
10. [进度追踪](development/progress.md) — 当前状态
11. [Docker / 桌面部署](dev-setup.md#docker-部署m6) — M6 打包

## 文档维护约定

| 类型 | 更新时机 | 负责人 |
|------|----------|--------|
| `plan/*` | 架构/范围变更时 | 项目负责人 |
| `development/backlog.md` | 任务新增/拆分/关闭时 | 当前开发者 |
| `development/progress.md` | 每周或每个 Sprint 结束时 | 当前开发者 |

**状态标记**：`[ ]` 未开始 · `[~]` 进行中 · `[x]` 已完成 · `[-]` 已取消
