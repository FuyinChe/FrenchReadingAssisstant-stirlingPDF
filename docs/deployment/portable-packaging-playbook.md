# Portable 打包问题手册（Playbook）

> 面向 **Windows / macOS 便携 zip** 的构建与排障。发版前必读，避免重复改打包脚本。  
> 平台细则：[Windows](windows-portable-packaging.md) · [macOS](macos-portable-packaging.md) · [依赖清单](portable-dependency-checklist.md)

---

## 1. 架构速览

```text
用户双击启动脚本
  → 设置 PATH / TESSDATA_PREFIX / CORS 等环境变量
  → 启动 engine（PyInstaller，:5002）
  → 启动 Stirling 桌面（Tauri + JRE + JAR）
  → 前端通过 VITE_FRENCH_READER_API_URL 访问 engine
```

| 目录 | 作用 |
|------|------|
| `app/` | Stirling 桌面 |
| `engine/` | French Reader 引擎（OCR / TTS / AI / 导出） |
| `tesseract/` | 外部 Tesseract 二进制 + 原生库 + `fra.traineddata` |

**构建时**必须设置 `VITE_FRENCH_READER_API_URL=http://127.0.0.1:5002/french-reader`（`build-portable-*.sh` 已默认）。

---

## 2. 发版前检查（每次打 zip 必做）

```bash
# macOS staging
./scripts/build-portable-macos.sh --arch arm64
# 或 CI: Actions → Release Portable

# Windows（在 Windows 构建机）
./scripts/build-portable-windows.ps1
```

构建结束会自动运行 **`verify-portable-staging.sh` / `.ps1`**，必须通过：

| 检查项 | 说明 |
|--------|------|
| 目录结构 | engine、tesseract、Stirling、`fra.traineddata` |
| Tesseract | `--version`、`--list-langs` 含 `fra` |
| 引擎状态 | `GET /french-reader/status` → `ocr_ready=true`, `bubble_ready=true` |
| OCR 端到端 | `POST /ocr/region` 非 5xx |
| PDF 导出 | `POST /export/pdf` 返回 `%PDF` |
| CORS | `OPTIONS /ocr/region` + `Origin: https://tauri.localhost` |

**不要**仅靠 `ocr_ready` 判断——它只检查 `tesseract --list-langs`，不保证 OCR 路径正确（见 Windows TESSDATA 案例）。

---

## 3. 已遇到问题与根因（按组件）

### 3.1 引擎（PyInstaller）

| 现象 | 平台 | 根因 | 修复思路 | 相关文件 |
|------|------|------|----------|----------|
| `Killed: 9`，无日志 | macOS | 解压后 `_internal/*.so` 无 ad-hoc 签名，AMFI 秒杀 | 构建 + 启动时运行 `sign-engine-bundle.sh`；**不要**只对主 exe `codesign --deep` | `packaging/macos/sign-engine-bundle.sh`, `Start … .command` |
| 卡在 Starting 20–60s | macOS | onedir 首次加载 OpenCV 慢 | 启动脚本已有进度提示；属正常 | `Start … .command` |
| `bubble_ready=false` | 双平台 | `cv2` 未打进 PyInstaller | spec 中 `collect_all("cv2")` + verify 检查 `bubble_ready` | `packaging/*/pyinstaller-engine.spec` |
| Export `CharisSIL-Regular.ttf` 缺失 | 双平台 | 字体未列入 `datas` | spec 加入 `assets/fonts/*.ttf` | `pyinstaller-engine.spec`, `pdf_fonts.py` |
| `No module named ultralytics` / `paddleocr` | 双平台 | **预期**，便携包故意排除 | 使用 OpenCV 气泡 + Tesseract OCR；日志可忽略 | spec `excludes` |

### 3.2 Tesseract（外部二进制）

| 现象 | 平台 | 根因 | 修复思路 | 相关文件 |
|------|------|------|----------|----------|
| OCR 503，`fra.traineddata` 路径错误 | **Windows** | `TESSDATA_PREFIX=tesseract\` 少了一层 `tessdata` | 设为 `tesseract\tessdata` | `Start … .bat` |
| OCR 503，tessdata 路径 | macOS | 应指向 `tesseract/share/tessdata` | 已正确；勿改成父目录 | `Start … .command` |
| `Library not loaded` / dyld 报错 | macOS | 只复制了 `bin/tesseract`，缺 `lib/*.dylib` | `fetch-tesseract-macos.sh` 捆绑全部依赖 | `fetch-tesseract-macos.sh` |
| `libtiff-6.dll` 等缺失 | Windows | 未复制全部 DLL | `fetch-tesseract-windows.ps1` 复制 `*.dll` | `fetch-tesseract-windows.ps1` |

### 3.3 启动器环境变量

| 变量 | Windows | macOS | 常见错误 |
|------|---------|-------|----------|
| `PATH` | `%ROOT%tesseract` | `$ROOT/tesseract/bin` | 引擎找不到 `tesseract` |
| `TESSDATA_PREFIX` | `%ROOT%tesseract\tessdata` | `$ROOT/tesseract/share/tessdata` | OCR 503 |
| `DYLD_LIBRARY_PATH` | — | **不要**在启动 engine 前设置 | 与 PyInstaller 冲突 → `Killed: 9` |
| `FRENCH_READER_CORS_ORIGINS` | 含 `tauri.localhost` 等 | 同左 | UI 显示 Load failed / CORS 失败 |

Tesseract 子进程：macOS 捆绑的 `tesseract` 已设 `@rpath/../lib`，**无需** `DYLD_LIBRARY_PATH`。

### 3.4 Stirling 桌面

| 现象 | 平台 | 根因 | 修复思路 |
|------|------|------|----------|
| Backend failed to restart | Windows | 缺 `runtime\jre` 或 `libs\*.jar` | 用 `gradle-bootjar-portable.sh` + jlink，勿用 `task desktop:build` |
| 闪退 `missing field pubkey` | macOS | 误删 updater pubkey | `patch-tauri-portable.py` 保留 pubkey，`createUpdaterArtifacts: false` |
| 钥匙串循环要密码 | macOS | 未签名 .app | 启动脚本设 `STIRLING_PDF_TEST_FORCE_*_KEYRING_FAIL` |

### 3.5 用户界面误导

| UI 显示 | 实际可能原因 | 处理 |
|---------|--------------|------|
| Auto detection needs OpenCV | **引擎未启动**（fetch 失败） | 先确认 `:5002` 与启动终端窗口；新 UI 会显示 engine unavailable |
| OCR failed / Load failed | 引擎未达、CORS、或 OCR 503 | 查 engine 日志 / 终端 |
| OCR is not configured | Tesseract 路径或 DLL 问题 | 见 3.2 |

---

## 4. macOS 用户侧排障（解压后）

```bash
cd /path/to/French-Reading-Assistant-*-macos-arm64
chmod -R u+w .
xattr -cr .
./sign-engine-bundle.sh engine/french-reader-engine
./Start\ French\ Reading\ Assistant.command
```

验证引擎：

```bash
curl -s http://127.0.0.1:5002/french-reader/status | python3 -m json.tool
# 期望: ocr_ready true, bubble_ready true
```

---

## 5. Windows 用户侧排障

1. 确认 `Start French Reading Assistant.bat` 第 7 行：`TESSDATA_PREFIX=%ROOT%tesseract\tessdata`
2. cmd 中运行 bat 查看报错
3. `curl http://127.0.0.1:5002/french-reader/status`

---

## 6. 修改打包时的原则（避免反复改）

1. **先跑 verify 脚本**，再发 zip；新增能力时同步加冒烟测试（OCR roundtrip、PDF export）。
2. **环境变量以启动脚本为唯一真相**；构建机 verify 应用与启动脚本相同的路径规则。
3. **PyInstaller 改 spec 时同时改 Windows + macOS** 两份 spec（`datas` / `hiddenimports` 保持同步）。
4. **macOS 引擎**：onedir + `sign-engine-bundle.sh`；不要恢复全局 `DYLD_LIBRARY_PATH`。
5. **不要**为便携包捆绑 YOLO/Paddle（体积与签名复杂度）；OpenCV + Tesseract 即可。
6. 前端 API 地址在 **Stirling 构建时** 烘焙，发版 workflow 已设 `VITE_FRENCH_READER_API_URL`。

---

## 7. 关键文件索引

| 用途 | 路径 |
|------|------|
| macOS 启动 | `packaging/macos/Start French Reading Assistant.command` |
| Windows 启动 | `packaging/windows/Start French Reading Assistant.bat` |
| 引擎签名 | `packaging/macos/sign-engine-bundle.sh` |
| PyInstaller | `packaging/macos/pyinstaller-engine.spec`, `packaging/windows/pyinstaller-engine.spec` |
| 捆绑引擎 | `scripts/bundle-sidecar-macos.sh`, `scripts/bundle-sidecar-windows.ps1` |
| 捆绑 OCR | `scripts/fetch-tesseract-macos.sh`, `scripts/fetch-tesseract-windows.ps1` |
| 发版前验证 | `scripts/verify-portable-staging.sh`, `scripts/verify-portable-staging.ps1` |
| 总构建 | `scripts/build-portable-macos.sh`, `scripts/build-portable-windows.ps1` |
| CI | `.github/workflows/release-portable.yml` |

---

## English summary

Portable zips bundle Stirling desktop + PyInstaller engine + external Tesseract. Common failures: **wrong `TESSDATA_PREFIX` (Windows)**, **unsigned Mach-O after unzip (macOS `Killed: 9`)**, **missing PyInstaller `datas` (fonts, cv2)**, **CORS / engine not running (UI “Load failed”)**. Always run `verify-portable-staging` before release; see platform guides for build steps.
