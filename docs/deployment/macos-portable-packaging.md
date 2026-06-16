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
├── LICENSE
├── THIRD-PARTY-NOTICES.md
├── licenses/STIRLING-PDF-LICENSE
├── VERSION.txt
├── app/
│   └── Stirling PDF.app
├── engine/
│   └── french-reader-engine/          ← PyInstaller onedir bundle
│       ├── french-reader-engine       ← executable
│       └── _internal/                 ← Python + OpenCV deps
└── tesseract/
    ├── bin/tesseract
    ├── lib/*.dylib              ← leptonica、tiff、jpeg 等依赖（必需）
    └── share/tessdata/
```

---

## GitHub Actions（推荐）

**Actions** → **Release Portable** → **Run workflow**

- 与 Windows 在同一 workflow 中并行构建；三个 zip 合并到**同一个 GitHub Release** Assets
- 在 `macos-14` 上**并行**构建 **arm64** 与 **x64** 两个 zip
- Intel 包在 Apple Silicon Runner 上通过 Rosetta + `setup-python` x64 交叉构建
- 参数与 Windows 工作流相同：`release_tag`、`draft_release`、`skip_desktop`

工作流：`.github/workflows/release-portable.yml`

首次调试可勾选 **`skip_desktop: true`**（约 15–25 分钟/架构）。

常见失败：

| 现象 | 处理 |
|------|------|
| `spotlessJava` / `build.shibboleth.net` | 勿用 `task desktop:prepare`；`build-stirling-desktop-portable.sh` 对 Gradle 加 `-x spotless*` |
| `compileJava` / `build.shibboleth.net` | `gradle-bootjar-portable.sh` 会临时把 `mavenCentral()` 排到 Shibboleth 前面，并排除便携 core 不用的 `com.coveo:saml-client` 传递依赖 |
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

打包结束时会自动运行 `scripts/verify-portable-staging.sh`。详见 [portable-dependency-checklist.md](portable-dependency-checklist.md)。

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

### 故障排除（使用）

| 问题 | 处理 |
|------|------|
| 卡在 `Starting French Reading Assistant...` | **正常现象**：PyInstaller 引擎首次启动需 **20–60 秒**（加载 OpenCV）。请耐心等待，或单独运行 `./engine/french-reader-engine` 查看日志；`lsof -i :5002` 有输出即已就绪 |
| `Killed: 9` / 引擎秒退 | `codesign -s - --force --deep engine/french-reader-engine` 后重试；仍失败则 `xattr -cr .` 并将文件夹移出 Downloads |
| OCR 失败 / Load failed | 旧包未设置 CORS；新包启动脚本会注入 `FRENCH_READER_CORS_ORIGINS`（含 `tauri.localhost`）。须用新 zip 重打 |
| `Library not loaded` / dyld 报错 | 旧包只复制了 `bin/tesseract`，缺 `lib/*.dylib`；新打包脚本会捆绑全部 Homebrew 依赖 |
| 钥匙串反复要密码 | 见 README；启动脚本已设置 `STIRLING_PDF_TEST_FORCE_*_KEYRING_FAIL` |
| Stirling 闪退 | `xattr -cr .`；确认 zip 含完整 `.app`（非仅 exe） |

> 长期方案是 Apple 开发者签名 + 公证（notarization）；当前版本为未签名便携包，需按上述步骤首次放行。

---

## English summary

**Workflow:** Actions → *Release Portable* — builds **windows-x64**, **macos-arm64**, and **macos-x64** zips; one GitHub Release with all assets.

**Local:** `./scripts/build-portable-macos.sh --arch arm64|x64`

**Launch:** `Start French Reading Assistant.command`
