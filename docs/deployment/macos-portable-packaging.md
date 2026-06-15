# macOS 便携 ZIP 打包指南

> **基座：** [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF)  
> [Windows 打包](windows-portable-packaging.md) · [English summary](#english-summary)

面向 **macOS** 的解压即用方案：双击 **`Start French Reading Assistant.command`**。

| 架构 | 产物文件名 |
|------|------------|
| Apple Silicon (M1/M2/M3) | `French-Reading-Assistant-{version}-macos-arm64.zip` |
| Intel Mac | `French-Reading-Assistant-{version}-macos-x64.zip` |

---

## 目录结构（zip 内）

```text
French-Reading-Assistant-0.5.0-macos-arm64/
├── Start French Reading Assistant.command   ← 双击启动
├── README.txt
├── VERSION.txt
├── app/
│   └── Stirling PDF.app
├── engine/
│   └── french-reader-engine
└── tesseract/
    ├── bin/tesseract
    └── share/tessdata/
```

---

## GitHub Actions（推荐）

**Actions** → **Release macOS Portable** → **Run workflow**

- 在 `macos-14` 上**并行**构建 **arm64** 与 **x64** 两个 zip
- Intel 包在 Apple Silicon Runner 上通过 Rosetta + `setup-python` x64 交叉构建
- 参数与 Windows 工作流相同：`release_tag`、`draft_release`、`skip_desktop`

工作流：`.github/workflows/release-macos-portable.yml`

首次调试可勾选 **`skip_desktop: true`**（约 15–25 分钟/架构）。

常见失败：

| 现象 | 处理 |
|------|------|
| `failed to bundle project: No such file or directory` | 勿用完整 `desktop:build`（会尝试 dmg/deb/msi 等）；便携脚本已改为仅 `--bundles app` |
| `TAURI_SIGNING_PRIVATE_KEY` | 便携包设置 `createUpdaterArtifacts: false`，无需 Stirling 更新签名私钥 |
| Intel (x64) 找不到 `.app` | x64 在 M 系列 Runner 上交叉编译，产物在 `target/x86_64-apple-darwin/release/bundle/macos/` |

---

## 本地打包

```bash
# Apple Silicon
./scripts/build-portable-macos.sh --arch arm64

# Intel（在 Intel Mac 上；或在 M 系列上用 Rosetta 终端）
./scripts/build-portable-macos.sh --arch x64
```

依赖：`brew install go-task tesseract tesseract-lang`、JDK 25、Node 22+、Rust、uv（与 Stirling 开发环境相同）。

产物：`dist/portable-macos/*.zip`

---

## 用户使用

1. 解压 zip  
2. 双击 **`Start French Reading Assistant.command`**  
3. 若提示无法打开：系统设置 → 隐私与安全性 → 仍要打开  
4. Stirling 中打开 PDF → **French Reading Assistant**

---

## English summary

**Workflow:** Actions → *Release macOS Portable* — builds **macos-arm64** and **macos-x64** zips on `macos-14`, manual `workflow_dispatch` only.

**Local:** `./scripts/build-portable-macos.sh --arch arm64|x64`

**Launch:** `Start French Reading Assistant.command`
