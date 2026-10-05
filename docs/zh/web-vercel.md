# 官网落地页（Vercel）

静态介绍站：FRA 是什么、怎么用、从 [GitHub Releases](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF/releases/latest) 下载便携包。

**不包含** 浏览器内 PDF 阅读、OCR API、Stirling 全站。完整功能在解压后的桌面便携版里。

## 本地预览

```bash
chmod +x scripts/web-dev.sh
./scripts/web-dev.sh
```

打开 http://localhost:5174

或：

```bash
cd apps/web
npm install
npm run dev
```

## 部署到 Vercel

1. 仓库连到 Vercel。
2. **Settings → General → Root Directory** 设为 **`apps/web`**（或留空用仓库根的 [`vercel.json`](../../vercel.json)）。
3. **Framework Preset** 选 **Vite**。不要选 FastAPI / Python。
4. 不要把 Root Directory 设成 `extensions/french-reader-engine`，否则会报 `No FastAPI entrypoint found`。

站点会请求 GitHub API `releases/latest`；尚无发行包时按钮退化为 Releases 页面。无需引擎环境变量。

## 下载资源命名

便携包流水线产出（见 [发行策略](../plan/10-distribution-strategy.md)）：

- `French-Reading-Assistant-*-windows-x64.zip`
- `French-Reading-Assistant-*-macos-arm64.zip`
- `French-Reading-Assistant-*-macos-x64.zip`
