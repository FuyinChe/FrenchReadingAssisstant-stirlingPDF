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
| `failed to bundle project: No such file or directory` | 勿用 `task desktop:build`；脚本使用 `npx tauri build --target … --bundles app`，并 `unset CARGO_BUILD_TARGET` |
| Intel (x64) 找不到 `.app` | 产物在 `target/x86_64-apple-darwin/release/bundle/macos/` |
| Apple Silicon (arm64) 打包失败 | 与 x64 相同，必须显式 `--target aarch64-apple-darwin`（不要只靠 `CARGO_BUILD_TARGET`） |
| Stirling 闪退 `missing field pubkey` | 旧包误删了 updater `pubkey`；需用修复后的脚本重打 macOS zip（保留 pubkey，仅 `createUpdaterArtifacts: false`） |

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

1. 解压 zip（**不要**只预览 zip 内文件；请「解压到文件夹」）
2. **首次启动**须绕过 Gatekeeper（未签名便携包会被拦截）：

### 推荐：终端解除隔离（一次即可）

```bash
cd ~/Downloads/French-Reading-Assistant-0.5.0-macos-arm64   # 改成你的解压路径
chmod -R u+w .          # tesseract 等可能是只读副本，否则 xattr 会 Permission denied
xattr -cr .
chmod +x "Start French Reading Assistant.command"
./Start\ French\ Reading\ Assistant.command
```

`xattr -cr .` 会去掉浏览器/GitHub 下载带来的 **quarantine** 标记；对 `.command`、`engine/`、`app/*.app` 都生效。

### 备选

| 情况 | 操作 |
|------|------|
| 提示无法验证开发者 | Finder **右键** `.command` → **打开** → 再点 **打开**（不要双击） |
| 已尝试打开被拦 | **系统设置** → **隐私与安全性** → 底部 **仍要打开** |
| `Stirling PDF.app` 也被拦 | 对 `app/` 内 `.app` 右键 → 打开；或再执行 `xattr -cr .` |

3. 启动后会弹出**终端窗口**（正常现象）：先起 French Reader 引擎，再打开 Stirling  
4. **不要关闭**该终端窗口，否则 OCR 引擎会停  
5. 在 Stirling 中打开 PDF → **French Reading Assistant**

> 长期方案是 Apple 开发者签名 + 公证（notarization）；当前版本为未签名便携包，需按上述步骤首次放行。

---

## English summary

**Workflow:** Actions → *Release macOS Portable* — builds **macos-arm64** and **macos-x64** zips on `macos-14`, manual `workflow_dispatch` only.

**Local:** `./scripts/build-portable-macos.sh --arch arm64|x64`

**Launch:** `Start French Reading Assistant.command`
