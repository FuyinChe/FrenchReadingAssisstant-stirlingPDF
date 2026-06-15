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
    ├── VERSION.txt                          ← 插件版本与 build id
    ├── app\                                 ← Stirling 桌面 .exe
    ├── engine\
    │   └── french-reader-engine.exe         ← OCR / TTS / AI
    └── tesseract\                           ← OCR（含 fra 法语包）
        ├── tesseract.exe
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

首次完整构建 **约 30–90 分钟**（含 `task desktop:build`）。

---

## 五（备选）、GitHub Actions 自动打包（仅手动触发）

无需本地 Windows 构建机时，可在 GitHub 上手动打 Release：

1. 发版前更新 `extensions/french-reader-version.json` 中的 `version`
2. 将改动 push 到 GitHub
3. 打开仓库 **Actions** → **Release Windows Portable** → **Run workflow**
4. 填写参数：

| 输入项 | 说明 |
|--------|------|
| `release_tag` | 如 `v0.5.0`（创建 Release 时必填） |
| `create_github_release` | 是否创建 GitHub Release 并附上 zip |
| `draft_release` | 建议首次勾选，草稿审阅后再发布 |
| `skip_desktop` | 仅测 engine 时可勾选（跳过 Stirling 桌面包，较快） |

5. 完成后在 **Releases** 或 **Artifacts** 下载 zip

工作流文件：`.github/workflows/release-windows-portable.yml`  
**不会**在 push/PR 时自动运行，仅 `workflow_dispatch` 手动触发。

公开仓库使用标准 `windows-latest` Runner 时，Actions 分钟数通常 **免费**（见 [GitHub Actions 计费](https://docs.github.com/en/billing/concepts/product-billing/github-actions)）。

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
| `task desktop:build` 失败 | 确认 JDK 25、Rust、`task install` 在 stirling-upstream 可运行 |
| Tesseract 未找到 | 安装 UB-Mannheim Tesseract，确认 `fra` 语言包 |
| PyInstaller 失败 | 删除 `dist/build-venv-windows` 后重跑 `bundle-sidecar-windows.ps1` |
| `app\` 为空 | 手动从 `stirling-upstream/frontend/editor/src-tauri/target/release/*.exe` 复制到 zip 的 `app\` |

---

## 八、故障排除（最终用户）

| 问题 | 处理 |
|------|------|
| 双击 bat 闪退 | 在 cmd 中运行 bat 查看错误；检查杀毒软件是否拦截 engine |
| 有界面但 OCR 失败 | 确认 `tesseract\tessdata\fra.traineddata` 存在 |
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

**GitHub Actions (manual only):** Actions → *Release Windows Portable* → Run workflow with tag `v0.5.0`.

**Version tracking:** edit `extensions/french-reader-version.json`; synced to engine `/french-reader/version`, `/health`, UI Settings footer, and `VERSION.txt` in the zip.

See also [10-distribution-strategy.md](../plan/10-distribution-strategy.md).
