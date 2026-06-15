# Getting started

**French Reading Assistant for Stirling PDF** extends [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF). You need this repo **and** the Stirling submodule (`stirling-upstream/`). Stirling is not bundled as a separate download — it is pulled via `git submodule`.

| | |
|---|---|
| **This repo** | [FuyinChe/FrenchReadingAssisstant-stirlingPDF](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF) |
| **Base app (upstream)** | [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) |
| **Stirling documentation** | [docs.stirlingpdf.com](https://docs.stirlingpdf.com/) |

[中文快速开始](../zh/getting-started.md)

---

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| Git + submodule | Pull Stirling upstream |
| Docker Desktop / Engine | Docker deployment (recommended for end users) |
| JDK 25, Node 20+, Task, uv | Local development only |

---

## Clone

```bash
git clone --recursive https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF.git
cd FrenchReadingAssisstant-stirlingPDF
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

The submodule points to [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF.git) (see `.gitmodules`).

---

## Run with Docker (recommended)

Builds images **on your machine** — does **not** upload to Docker Hub.

```bash
chmod +x scripts/*.sh
cp .env.docker.example .env    # optional: FRENCH_READER_LLM_API_KEY
./scripts/docker-up.sh
# equivalent: docker compose up --build
```

- First build can take **30–60 minutes** (Stirling + frontend + JDK).
- Open http://localhost:8080
- Go to **Recommended tools** → **French Reading Assistant**

Optional `.env` keys: see [.env.docker.example](../../.env.docker.example).

---

## Run for development

```bash
chmod +x scripts/*.sh
./scripts/install-extensions.sh
./scripts/dev.sh
```

| Service | URL |
|---------|-----|
| Stirling UI | http://localhost:5173 |
| Stirling API | http://localhost:8080 |
| French Reader engine | http://localhost:5002 |

Full developer setup: [dev-setup.md](../dev-setup.md).

---

## Desktop (Tauri)

Uses Stirling’s Tauri desktop build with French Reader enabled:

```bash
./scripts/build-desktop.sh
./scripts/desktop-dev.sh
```

See [Stirling DeveloperGuide](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/DeveloperGuide.md) for Rust/JDK requirements.

---

## AI configuration

Either:

1. **In-app:** Settings (gear) → LLM provider + API key → Save, or  
2. **Environment:** `FRENCH_READER_LLM_API_KEY` in `.env` (dev) or `.env` for Docker sidecar.

---

## Next steps

- [User guide (with screenshot placeholders)](user-guide.md)
- [Documentation index](../README.md)
- [Sidecar fallback deployment](../deployment/sidecar-fallback.md)
