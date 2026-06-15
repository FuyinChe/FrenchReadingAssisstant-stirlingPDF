# Documentation / 文档中心

**French Reading Assistant for Stirling PDF** — bilingual docs for [FuyinChe/FrenchReadingAssisstant-stirlingPDF](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF).

> **Upstream base:** [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF) · [Official docs](https://docs.stirlingpdf.com/) · [DeveloperGuide](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/DeveloperGuide.md)  
> **基座应用：** [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF) · [官方文档](https://docs.stirlingpdf.com/)

| English | 中文 |
|---------|------|
| [Getting started](en/getting-started.md) | [快速开始](zh/getting-started.md) |
| [User guide](en/user-guide.md) | [用户手册](zh/user-guide.md) |
| [Architecture diagram](images/shared/architecture.md) | [架构图](images/shared/architecture.md) |
| [Screenshot assets](images/README.md) | [截图资源说明](images/README.md) |

---

## Directory layout

```
docs/
├── README.md                 # This index / 本索引
├── en/                       # English user-facing docs
│   ├── getting-started.md
│   └── user-guide.md         # + screenshot placeholders
├── zh/                       # 中文用户文档
│   ├── getting-started.md
│   └── user-guide.md
├── images/                   # Screenshots (add PNG/WebP here)
│   ├── shared/               # Architecture diagrams
│   └── user-guide/{en,zh}/
├── dev-setup.md              # Developer setup (detailed, 中文为主)
├── deployment/
│   └── sidecar-fallback.md
├── plan/                     # Architecture & milestones
└── development/              # Backlog, progress, sync log
```

---

## Onboarding (developers)

1. [Getting started EN](en/getting-started.md) / [快速开始 中文](zh/getting-started.md)
2. [Stirling integration strategy](plan/06-stirling-integration-strategy.md)
3. [Architecture](plan/02-architecture.md)
4. [Dev setup](dev-setup.md)
5. [Backlog](development/backlog.md) · [Progress](development/progress.md)

---

## User onboarding (end users)

1. Clone repo + submodule → Docker or dev script ([EN](en/getting-started.md) / [ZH](zh/getting-started.md))
2. Follow [user guide](en/user-guide.md) / [用户手册](zh/user-guide.md)
3. Add screenshots under [images/user-guide/](images/README.md) as features are documented

---

## Maintenance

| Type | When to update |
|------|----------------|
| `en/*`, `zh/*` | User-facing behavior or UI changes |
| `images/user-guide/*` | New step-by-step screenshots |
| `plan/*` | Scope or architecture changes |
| `development/*` | Sprint / sync updates |

Status markers: `[ ]` todo · `[~]` in progress · `[x]` done · `[-]` cancelled

---

## Legacy paths

| Old path | Redirect |
|----------|----------|
| [user-guide.md](user-guide.md) | Points to `en/` and `zh/` guides |
