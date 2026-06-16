# Windows 便携 ZIP 打包指南

> **基座：** [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF)  
> **本仓库：** [FrenchReadingAssisstant-stirlingPDF](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF)  
> [English summary](#english-summary)

面向 **Windows 10/11 x64** 的「解压即用」方案：用户双击 **`Start French Reading Assistant.bat`** 即可启动。

---

## 一、产物说明

构建完成后得到：

```text
dist/portable-windows/
└── French-Reading-Assistant-{version}-windows-x64.zip
    ├── Start French Reading Assistant.bat   ← 用户双击这个
    ├── README.txt
    ├── LICENSE                              ← MIT（本扩展原创部分）
    ├── THIRD-PARTY-NOTICES.md               ← Stirling + 第三方组件
    ├── licenses\STIRLING-PDF-LICENSE        ← Stirling 上游许可全文
    ├── VERSION.txt                          ← 插件版本与 build id
    ├── app\                                 ← Stirling 桌面（exe + JRE + JAR）
    │   ├── stirling-pdf.exe
    │   ├── runtime\jre\                   ← 内置 Java（必需）
    │   └── libs\stirling-pdf-*.jar        ← Stirling 后端（必需）
    ├── engine\
    │   └── french-reader-engine.exe         ← OCR / TTS / AI
    └── tesseract\                           ← OCR（含 fra 法语包）
        ├── tesseract.exe
        ├── *.dll                            ← 全部依赖（libtesseract、libleptonica、libtiff…）
        └── tessdata\
```

| 文件 | 作用 |
|------|------|
| `Start French Reading Assistant.bat` | 启动 engine → 等待健康检查 → 打开 Stirling |
| `VERSION.txt` | 可追踪的插件版本（与 Settings 中显示一致） |
| `extensions/french-reader-version.json` | **版本源文件**（发版前改这里） |

---

## 二、构建机环境（仅打包时需要）

在 **Windows x64** 电脑上安装：

| 依赖 | 用途 | 安装示例 |
|------|------|----------|
| Git for Windows | 子模块 + bash 脚本 | [git-scm.com](https://git-scm.com/download/win) |
| Python 3.11+ | 打包 engine | python.org / `winget install Python.Python.3.12` |
| Node.js 20+ | Stirling 前端 | `winget install OpenJS.NodeJS.LTS` |
| JDK 25 | Stirling 后端 | Stirling 文档要求 |
| Rust | Tauri 桌面 | [rustup.rs](https://rustup.rs/) |
| Go Task | Stirling 构建命令 | `winget install Task.Task` 或 `scoop install task` |
| Tesseract + fra | OCR（打包进 zip） | `winget install UB-Mannheim.TesseractOCR` |

验证：

```powershell
git --version
python --version
node --version
java -version
cargo --version
task --version
tesseract --list-langs   # 需包含 fra
```

---

## 三、获取源码

```powershell
git clone --recursive https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF.git
cd FrenchReadingAssisstant-stirlingPDF
```

若已克隆但未拉子模块：

```powershell
git submodule update --init --recursive
```

---

## 四、版本号（发版前必做）

编辑 **`extensions/french-reader-version.json`**：

```json
{
  "name": "french-reading-assistant",
  "displayName": "French Reading Assistant",
  "version": "0.5.0",
  "apiVersion": 1,
  "minStirlingVersion": "2.0.0",
  "channel": "portable"
}
```

同步到 engine / 前端（构建脚本会自动执行，也可手动）：

```powershell
python scripts/sync-plugin-version.py --platform windows-x64
```

版本追踪位置：

| 位置 | 说明 |
|------|------|
| Settings 弹窗底部 | `Plugin v0.5.0 · windows-x64 · build-id` |
| `GET http://127.0.0.1:5002/health` | JSON 字段 `plugin` |
| `GET /french-reader/version` | 完整插件信息 |
| zip 内 `VERSION.txt` | 给最终用户查看 |

---

## 五、一键打包

在仓库根目录 **PowerShell** 中：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-portable-windows.ps1
```

### 常用参数

```powershell
# 只打 engine + 启动器（跳过 Stirling 桌面，用于调试 sidecar）
powershell -ExecutionPolicy Bypass -File .\scripts\build-portable-windows.ps1 -SkipDesktop

# 只生成文件夹，不压 zip
powershell -ExecutionPolicy Bypass -File .\scripts\build-portable-windows.ps1 -SkipZip

# 分步（排错时）
powershell -ExecutionPolicy Bypass -File .\scripts\bundle-sidecar-windows.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\fetch-tesseract-windows.ps1
```

首次完整构建 **约 20–60 分钟**（含 `build-stirling-desktop-portable-windows.ps1`：Gradle bootJar + jlink + Tauri exe，不打包 MSI）。

打包结束时会自动运行 `scripts/verify-portable-staging.ps1`（Tesseract、Stirling JRE/JAR、引擎 `ocr_ready` / `bubble_ready`）。详见 [portable-dependency-checklist.md](portable-dependency-checklist.md)。

---

## 五（备选）、GitHub Actions 自动打包（仅手动触发）

无需本地 Windows 构建机时，可在 GitHub 上手动打 Release：

1. 发版前更新 `extensions/french-reader-version.json` 中的 `version`
2. 将改动 push 到 GitHub
3. 打开仓库 **Actions** → **Release Portable** → **Run workflow**
4. 填写参数：

| 输入项 | 说明 |
|--------|------|
| `release_tag` | 如 `v0.5.0`（创建 Release 时必填） |
| `create_github_release` | 是否创建 GitHub Release 并附上 zip |
| `draft_release` | 建议首次勾选，草稿审阅后再发布 |
| `skip_desktop` | 仅测 engine 时可勾选（跳过 Stirling 桌面包，较快） |

5. 完成后在 **Releases** 或 **Artifacts** 下载 zip

工作流文件：`.github/workflows/release-portable.yml`  
与 macOS 包在同一 workflow 中并行构建，最终合并到**同一个 GitHub Release** 的 Assets 里。

公开仓库使用标准 `windows-latest` Runner 时，Actions 分钟数通常 **免费**（见 [GitHub Actions 计费](https://docs.github.com/en/billing/concepts/product-billing/github-actions)）。

**首次调试建议：** 勾选 `skip_desktop=true`，先验证 engine + zip 流程（约 10–20 分钟），通过后再跑完整桌面包。

常见失败：

| 现象 | 处理 |
|------|------|
| `python3: command not found` | 已修复：`install-extensions.sh` 使用 `python` 回退 |
| `Tesseract not found` | workflow 会搜索 Chocolatey 与 Program Files 路径 |
| `spotlessJava` / `build.shibboleth.net` timeout | Gradle 已加 `-x spotless*`（与 Docker 构建一致）；Spotless 仅格式化，不影响运行时 JAR |
| `task desktop:build` 失败 | 便携包不调用 `desktop:build`（MSI + 签名）；确认 **JDK 25**（含 `jlink`）、Rust、`task install` |
| `TAURI_SIGNING_PRIVATE_KEY` | 仅完整 `desktop:build`（MSI + 自动更新签名）需要；便携 zip 使用 `npx tauri build --no-bundle` |
| Node.js 20 弃用警告 | 可忽略；workflow 已设置 `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` |

---

## 六、在测试机上使用

1. 将 `French-Reading-Assistant-*-windows-x64.zip` 拷到 Windows 电脑  
2. 右键 zip → **全部提取**  
3. 双击 **`Start French Reading Assistant.bat`**  
4. 若 SmartScreen 提示 → **更多信息** → **仍要运行**  
5. 在 Stirling 中打开 PDF → **Recommended tools** → **French Reading Assistant**

### 验证版本

```powershell
Invoke-RestMethod http://127.0.0.1:5002/french-reader/version
```

---

## 七、故障排除（构建）

| 问题 | 处理 |
|------|------|
| `git submodule` 失败 | 检查网络与 GitHub 访问 |
| `CommandNotFoundException`（`jlink`/`cp`） | 使用 `scripts/build-stirling-desktop-portable-windows.ps1`，勿用 `task desktop:build:dev` |
| `task desktop:build` 失败 | 确认 JDK 25（`JAVA_HOME\bin\jlink.exe`）、Rust、`task install` 在 stirling-upstream 可运行 |
| `TAURI_SIGNING_PRIVATE_KEY` | 便携包不调用 `desktop:build`，无需 Stirling 更新签名私钥 |
| Tesseract 未找到 | 安装 UB-Mannheim Tesseract，确认 `fra` 语言包 |
| PyInstaller 失败 | 删除 `dist/build-venv-windows` 后重跑 `bundle-sidecar-windows.ps1` |
| `app\` 为空 | 重新运行 `build-portable-windows.ps1`；`app\` 须含 `stirling-pdf.exe`、`runtime\jre\`、`libs\*.jar` |
| `app\` 只有 exe | 旧版打包脚本缺陷；`desktop:build:dev` 只生成 exe，须额外复制 `runtime` 与 `libs`（脚本已修复） |

---

## 八、故障排除（最终用户）

| 问题 | 处理 |
|------|------|
| 双击 bat 闪退 | 在 cmd 中运行 bat 查看错误；检查杀毒软件是否拦截 engine |
| **Backend failed to restart** | 检查 `app\runtime\jre\bin\java.exe` 与 `app\libs\stirling-pdf-*.jar` 是否存在；缺则需重新打包 |
| 有界面但 OCR 失败 | 确认 `tesseract\tessdata\fra.traineddata` 存在；旧包缺 CORS 配置，须用新 zip（启动脚本含 `FRENCH_READER_CORS_ORIGINS`） |
| `libtiff-6.dll` / `libjpeg-8.dll` 等缺失 | 旧打包脚本未复制全部 Tesseract DLL；新脚本会复制安装目录下所有 `*.dll` 并自检 |
| OCR is not configured | 引擎找不到 `tesseract.exe` 或依赖 DLL；确认 `tesseract\` 完整，并用 bat 启动（会设置 PATH） |
| AI 不可用 | Settings 中填写 API Key |
| 朗读无声音 | 需要网络（edge-tts） |

---

## 九、与 Docker 的关系

| 方式 | 用户 |
|------|------|
| **Windows zip（本文）** | 普通用户，免 Docker |
| Docker Compose | 技术人员自托管 |

---

## English summary

**Deliverable:** `French-Reading-Assistant-{version}-windows-x64.zip`  
**End-user entrypoint:** `Start French Reading Assistant.bat`  

**Build on Windows x64** (local or GitHub Actions manual workflow):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-portable-windows.ps1
```

**GitHub Actions (manual only):** Actions → *Release Portable* → Run workflow with tag `v0.5.0` (Windows + macOS arm64 + macOS x64 in one release).

**Version tracking:** edit `extensions/french-reader-version.json`; synced to engine `/french-reader/version`, `/health`, UI Settings footer, and `VERSION.txt` in the zip.

See also [10-distribution-strategy.md](../plan/10-distribution-strategy.md).
