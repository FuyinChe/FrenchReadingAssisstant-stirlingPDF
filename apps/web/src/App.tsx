import { useEffect, useState } from "react";
import {
  fetchLatestRelease,
  GITHUB_REPO,
  RELEASES_LATEST_PAGE,
  type PlatformId,
  type ReleaseInfo,
} from "./releases";

const HOME = "https://learnlanguage.net";
const FVA = "https://fva.learnlanguage.net";
const FRA = "https://fra.learnlanguage.net";
const CA = "https://cantonese.learnlanguage.net";
const HUB_GITHUB = "https://github.com/FuyinChe/learnlanguage.net";
const STIRLING = "https://github.com/Stirling-Tools/Stirling-PDF";
const REPO = `https://github.com/${GITHUB_REPO}`;

function GitHubIcon() {
  return (
    <svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true">
      <path
        fill="currentColor"
        d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82A7.7 7.7 0 0 1 8 3.47c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"
      />
    </svg>
  );
}

type Lang = "zh" | "en";

const copy = {
  zh: {
    brand: "法语阅读助手",
    enName: "French Reading Assistant",
    tagline: "用来读法语材料。在页面上框选一段，识别文字、听朗读，并查看语法和词汇说明。",
    download: "下载",
    usage: "用法",
    about: "介绍",
    heroCta: "下载便携版",
    allReleases: "所有发行版",
    noRelease: "尚无公开发行包。请打开 GitHub Releases，或按仓库文档自行打包。",
    fetchError: "暂时读不到发行版列表，请直接打开 GitHub Releases。",
    version: "最新版本",
    win: "Windows x64",
    macArm: "macOS Apple 芯片",
    macIntel: "macOS Intel",
    unzip: "下载 zip → 解压 → 运行 Start French Reading Assistant。PDF 留在本机。",
    aboutBody:
      "本项目在开源 Stirling PDF 上增加 French Reading Assistant 工具，不改动 Stirling 核心。合并、拆分等能力仍然可用。",
    stepsTitle: "在 Stirling 里怎么用",
    steps: [
      "解压便携包并启动应用，像平时一样打开 PDF。",
      "在 Recommended tools / 推荐工具 中打开 French Reading Assistant。",
      "左侧是 PDF 画布，右侧是识别、朗读与 AI 侧栏。",
      "在页面上拖矩形即可做法语 OCR；也可用 BUBBLES / PARAGRAPHS 自动检测。",
      "AI 释义需在设置里填写 LLM API Key；朗读使用 edge-tts（需联网）。",
    ],
    fig1: "图 1 — 推荐工具中打开 French Reading Assistant。",
    fig2: "图 2 — 阅读助手侧栏：检测、设置与历史。",
    fig3: "图 3 — 框选后的 OCR 结果与 Explain。",
    guide: "完整用户手册",
    baseApp: "Base application",
    thisRepo: "本项目地址",
    home: "主站",
    fva: "法语动词助手",
    fra: "法语阅读助手",
    ca: "粤语助手",
  },
  en: {
    brand: "French Reading Assistant",
    enName: "French Reading Assistant",
    tagline:
      "Read French materials: select a region, run OCR, listen with TTS, and see grammar and vocabulary notes.",
    download: "Download",
    usage: "How to use",
    about: "About",
    heroCta: "Download portable build",
    allReleases: "All releases",
    noRelease:
      "No published release yet. Open GitHub Releases, or build from the repo docs.",
    fetchError: "Could not load releases. Open GitHub Releases instead.",
    version: "Latest",
    win: "Windows x64",
    macArm: "macOS Apple silicon",
    macIntel: "macOS Intel",
    unzip:
      "Download the zip → extract → run Start French Reading Assistant. PDFs stay on your machine.",
    aboutBody:
      "This project adds a French Reading Assistant tool on top of open-source Stirling PDF without changing Stirling’s core. Merge, split, and other tools still work.",
    stepsTitle: "Using it inside Stirling",
    steps: [
      "Unzip the portable pack and start the app, then open a PDF as usual.",
      "Open French Reading Assistant from Recommended tools.",
      "The PDF canvas is on the left; OCR, TTS, and AI sit in the right panel.",
      "Drag a rectangle on the page for French OCR, or run BUBBLES / PARAGRAPHS.",
      "AI explain needs an LLM API key in Settings. TTS uses edge-tts (needs network).",
    ],
    fig1: "Figure 1 — Open French Reading Assistant from Recommended tools.",
    fig2: "Figure 2 — Assistant sidebar: detectors, settings, history.",
    fig3: "Figure 3 — OCR result and Explain after a selection.",
    guide: "Full user guide",
    baseApp: "Base application",
    thisRepo: "This project",
    home: "Main site",
    fva: "French Verb Assistant",
    fra: "French Reading Assistant",
    ca: "Cantonese Assistant",
  },
} as const;

const platforms: { id: PlatformId; labelKey: "win" | "macArm" | "macIntel" }[] = [
  { id: "windows-x64", labelKey: "win" },
  { id: "macos-arm64", labelKey: "macArm" },
  { id: "macos-x64", labelKey: "macIntel" },
];

export function App() {
  const [lang, setLang] = useState<Lang>("zh");
  const [release, setRelease] = useState<ReleaseInfo | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ok" | "empty" | "error">(
    "loading",
  );
  const t = copy[lang];

  useEffect(() => {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  }, [lang]);

  useEffect(() => {
    let cancelled = false;
    fetchLatestRelease()
      .then((info) => {
        if (cancelled) {
          return;
        }
        if (!info) {
          setLoadState("empty");
          return;
        }
        setRelease(info);
        setLoadState("ok");
      })
      .catch(() => {
        if (!cancelled) {
          setLoadState("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="page">
      <header className="top">
        <a className="brand" href={HOME}>
          <span className="brand-mark">LearnLanguage</span>
          <span className="brand-host">.net</span>
        </a>
        <div className="top-right">
          <nav className="page-nav">
            <a href="#download">{t.download}</a>
            <a href="#usage">{t.usage}</a>
            <a href="#about">{t.about}</a>
          </nav>
          <div className="lang" role="group" aria-label="语言">
            <button
              type="button"
              aria-pressed={lang === "zh"}
              onClick={() => setLang("zh")}
            >
              中文
            </button>
            <button
              type="button"
              aria-pressed={lang === "en"}
              onClick={() => setLang("en")}
            >
              EN
            </button>
          </div>
        </div>
      </header>

      <main>
        <section className="hero" id="top">
          <div className="hero-head">
            <span className="code-badge" aria-hidden="true">
              FRA
            </span>
            <p className="eyebrow">fra.learnlanguage.net</p>
          </div>
          <h1>{t.brand}</h1>
          {lang === "zh" ? <p className="en-name">{t.enName}</p> : null}
          <p className="lede">{t.tagline}</p>
          <div className="hero-actions">
            <a className="primary" href="#download">
              {t.heroCta}
            </a>
            <a className="github-text" href={REPO} aria-label="GitHub">
              <GitHubIcon />
              GitHub
            </a>
          </div>
        </section>

        <section id="download" className="block">
          <h2>{t.download}</h2>
          <p className="lede-inline">{t.unzip}</p>
          {loadState === "ok" && release ? (
            <p className="meta">
              {t.version}{" "}
              <a href={release.htmlUrl}>{release.tag}</a>
            </p>
          ) : null}
          {loadState === "empty" ? <p className="note">{t.noRelease}</p> : null}
          {loadState === "error" ? <p className="note">{t.fetchError}</p> : null}
          <div className="downloads">
            {platforms.map((platform) => {
              const href = release?.urls[platform.id] ?? RELEASES_LATEST_PAGE;
              return (
                <a key={platform.id} className="primary" href={href}>
                  {t[platform.labelKey]}
                </a>
              );
            })}
          </div>
          <p>
            <a href={RELEASES_LATEST_PAGE}>{t.allReleases}</a>
          </p>
        </section>

        <section id="usage" className="block">
          <h2>{t.stepsTitle}</h2>
          <ol>
            {t.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
          <figure>
            <img src="/preview/001.png" alt={t.fig1} />
            <figcaption>{t.fig1}</figcaption>
          </figure>
          <figure>
            <img src="/preview/002.png" alt={t.fig2} />
            <figcaption>{t.fig2}</figcaption>
          </figure>
          <figure>
            <img src="/preview/008.png" alt={t.fig3} />
            <figcaption>{t.fig3}</figcaption>
          </figure>
          <p>
            <a href={`${REPO}/blob/main/docs/${lang === "zh" ? "zh" : "en"}/user-guide.md`}>
              {t.guide}
            </a>
          </p>
        </section>

        <section id="about" className="block">
          <h2>{t.about}</h2>
          <p>{t.aboutBody}</p>
          <p className="about-row">
            <span className="about-label">{t.baseApp}:</span>
            <a href={STIRLING}>Stirling PDF</a>
          </p>
          <p className="about-row">
            <span className="about-label">{t.thisRepo}:</span>
            <a href={REPO} className="github-link" aria-label="GitHub">
              <GitHubIcon />
            </a>
          </p>
        </section>
      </main>

      <footer>
        <nav className="footer-links" aria-label={lang === "zh" ? "页面" : "Pages"}>
          <a href={HOME}>{t.home}</a>
          <a href={FVA}>{t.fva}</a>
          <a href={FRA}>{t.fra}</a>
          <a href={CA}>{t.ca}</a>
          <a className="footer-github" href={HUB_GITHUB} aria-label="GitHub">
            <GitHubIcon />
          </a>
        </nav>
        <span className="copyright">© 2026 LearnLanguage</span>
      </footer>
    </div>
  );
}
