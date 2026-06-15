# User guide — French Reading Assistant

Use the French Reading Assistant **inside [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF)**: select a region → French OCR → read aloud → AI explanation.

[用户手册（中文）](../zh/user-guide.md) · [Getting started](getting-started.md) · [Screenshot conventions](../images/README.md)

---

## Before you start

| Mode | Command |
|------|---------|
| Development | `./scripts/dev.sh` ([dev-setup.md](../dev-setup.md)) |
| Docker | `./scripts/docker-up.sh` |
| Desktop | `./scripts/build-desktop.sh`, then `./scripts/desktop-dev.sh` |

AI features need an LLM API key: Settings → LLM provider, or `FRENCH_READER_LLM_API_KEY` in `.env`.

---

## Open the tool

1. Open a PDF in Stirling (same as usual).
2. In the tool list, open **French Reading Assistant** under **Recommended tools**.
3. Layout: PDF canvas on the left, AI sidebar on the right.

<!-- Screenshot: docs/images/user-guide/en/01-open-tool.png -->

*Figure 1 — Recommended tools → French Reading Assistant. Screenshot: `docs/images/user-guide/en/01-open-tool.png` (pending).*

---

## Selection and OCR

### Manual selection (recommended)

1. Drag a rectangle on the page.
2. French OCR runs on the selection; text appears under **Recognized text**.

<!-- Screenshot: docs/images/user-guide/en/02-manual-selection.png -->

*Figure 2 — Manual selection and OCR result (screenshot pending).*

### Auto detectors

In the sidebar **AUTO DETECTORS**:

| Button | Use |
|--------|-----|
| **BUBBLES** | Comic speech bubbles |
| **PARAGRAPHS** | Picture-book / page paragraphs |

- Enable **ENHANCE** for difficult backgrounds.
- Green dashed boxes show detections; verify important text with manual selection.
- Red italic banner: auto-detect is advisory only.

<!-- Screenshot: docs/images/user-guide/en/03-auto-detectors.png -->

*Figure 3 — Bubbles / Paragraphs detectors (screenshot pending).*

---

## Text-to-speech (TTS)

1. After OCR, choose French voice and speed in **Settings**.
2. Click **Read aloud**.
3. Uses edge-tts (network required).

<!-- Screenshot: docs/images/user-guide/en/04-tts-read-aloud.png -->

*Figure 4 — TTS settings and Read aloud (screenshot pending).*

---

## AI explanation

1. **Settings → AI explanation:**
   - Modes: Translate / Vocabulary / Grammar (multi-select)
   - Output language: 中文 or English
   - **LLM provider** (default Kimi) + API key → **Save settings**
2. Click **Explain** in the sidebar.
3. Streaming output per mode; **Stop** anytime.

Yellow banner if no API key is configured.

<!-- Screenshot: docs/images/user-guide/en/05-ai-explain.png -->

*Figure 5 — LLM settings and Explain output (screenshot pending).*

---

## History and export

- Each OCR is saved to **History**.
- Export: **PDF** → **Markdown** → **TXT** (sidebar menu).
- PDF export includes recognized text and AI explanations.

<!-- Screenshot: docs/images/user-guide/en/06-history-export.png -->

*Figure 6 — History and export (screenshot pending).*

---

## Settings reference

| Section | Options |
|---------|---------|
| Pronunciation | French voice, speed |
| AI explanation | Modes, language, LLM provider, API key |
| LLM providers | Kimi, OpenAI, Gemini, Claude, Copilot (Azure), etc. |

Copilot / Custom need endpoint and model/deployment name.

---

## FAQ

| Issue | Action |
|-------|--------|
| Tool missing | `FRENCH_READER_ENABLED=true` and `./scripts/install-extensions.sh` |
| OCR fails | `./scripts/setup-ocr.sh`; check engine `:5002` |
| AI unavailable | Key in Settings or `.env` |
| Docker: no tool | Use **this repo’s** extended Stirling image, not stock Stirling-only |
| Desktop: no OCR/AI | Run sidecar (`desktop-dev.sh` starts it) |

---

## Related

- [Stirling PDF (upstream)](https://github.com/Stirling-Tools/Stirling-PDF)
- [Getting started](getting-started.md)
- [Sidecar fallback](../deployment/sidecar-fallback.md)
- [Add screenshots](../images/README.md)
