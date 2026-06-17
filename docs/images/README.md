# Documentation images / 文档截图

Screenshots for user guides live under `docs/images/user-guide/`. README preview images live under [`screenshots/preview/`](../../screenshots/preview/). Add PNG or WebP files; keep filenames stable so links in `docs/en/` and `docs/zh/` do not break.

用户手册截图放在 `docs/images/user-guide/`；根目录 README 预览图放在 [`screenshots/preview/`](../../screenshots/preview/)。请使用 PNG 或 WebP，并保持文件名稳定，以便中英文文档链接一致。

## Directory layout

```
screenshots/preview/             # 2–4 images for root README only
docs/images/user-guide/
├── en/                          # English UI screenshots
│   ├── 01-open-tool.png         # (pending) Open French Reading Assistant
│   ├── 02-manual-selection.png  # (pending) Drag selection + OCR
│   ├── 03-auto-detectors.png    # (pending) Bubbles / Paragraphs
│   ├── 04-tts-read-aloud.png    # (pending) TTS settings + Read aloud
│   ├── 05-ai-explain.png        # (pending) LLM settings + Explain
│   ├── 06-history-export.png    # (pending) History + export menu
│   └── 07-docker-home.png       # (pending) Gateway home / tool entry
└── zh/                          # Same steps; Chinese UI labels if different
    └── (mirror filenames under en/)
```

Shared assets (logos, architecture diagrams) may go in `docs/images/shared/` — see [architecture.md](shared/architecture.md).

## Conventions

| Rule | EN | 中文 |
|------|----|------|
| Format | PNG or WebP, ≤ 1920px wide | 同上 |
| Naming | `NN-topic-kebab-case.ext` | 与英文同名（便于双语共用或对照） |
| Alt text | Describe the UI action | 在对应语言的 md 里写清楚 alt |
| Privacy | Redact API keys and personal PDFs | 打码 API Key 与私人 PDF |
| Stirling UI | Credit [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) in captions when showing base UI | 展示基座界面时在说明中注明 Stirling PDF |

## Referencing in markdown

```markdown
![Open French Reading Assistant](../images/user-guide/en/01-open-tool.png)
*Figure 1 — Recommended tools → French Reading Assistant (screenshot pending).*
```

Until a file exists, guides show an italic *screenshot pending* note instead of a broken image.

## Related docs

- [User guide (EN)](../en/user-guide.md)
- [用户手册（中文）](../zh/user-guide.md)
