French Reading Assistant for Stirling PDF (macOS portable)
=========================================================

START HERE / 从这里启动
  Double-click:  Start French Reading Assistant.command

  若被系统拦截（无法打开 / 已损坏 / 来自 unidentified developer）：
  方法一（推荐）— 终端一次性解除隔离并启动：
    1. 打开「终端」(Terminal)
    2. 把解压后的整个文件夹拖进终端窗口，前面会自动出现路径
    3. 在该路径前输入 cd 和一个空格，回车，例如：
         cd ~/Downloads/French-Reading-Assistant-0.5.0-macos-arm64
    4. 粘贴并执行（先恢复写权限，再解除 quarantine）：
         chmod -R u+w .
         xattr -cr .
         chmod +x "Start French Reading Assistant.command"
    5. 再执行：
         ./Start\ French\ Reading\ Assistant.command

  方法二 — 右键打开：
    在 Finder 中右键 Start French Reading Assistant.command → 打开 → 再点「打开」
    （不要双击；首次必须用右键。）

  方法三 — 系统设置：
    尝试双击被拦后，打开 系统设置 → 隐私与安全性 → 底部「仍要打开」

  若 Stirling PDF.app 也被拦：对 app/ 里的 .app 同样右键 → 打开。
  或对整包再执行一次：xattr -cr .

CONTENTS / 目录说明
  app/       Stirling PDF.app (with French Reader tool)
  engine/    French Reader OCR / TTS / AI (local :5002)
  tesseract/ OCR binaries + tessdata (French when bundled)

FIRST RUN / 首次使用
  1. 用上面任一方法启动 .command（会打开终端窗口并启动 engine + Stirling）
  2. 在 Stirling 中打开 PDF
  3. Recommended tools → French Reading Assistant
  4. Optional: Settings → LLM API key

  注意：不要关闭启动时弹出的终端窗口；关闭它会停止 French Reader 引擎。

  Stirling 窗口在哪？
    • 启动成功后看程序坞 (Dock) 的 Stirling PDF 图标，或按 Cmd+Tab 切换
    • 终端窗口是引擎，不是 Stirling 主界面

  若窗口一闪就消失（Stirling 闪退）：
    1. 对 app 里的 .app 右键 → 打开 → 再点「打开」
    2. 或在终端（另开一个窗口）运行，查看报错：
         cd /path/to/解压文件夹
         xattr -dr com.apple.quarantine app/Stirling-PDF.app
         app/Stirling-PDF.app/Contents/MacOS/stirling-pdf
    3. 仍失败：打开「控制台」(Console.app) 搜索 stirling

ARCHITECTURE / 架构
  Apple Silicon (arm64): French-Reading-Assistant-*-macos-arm64.zip
  Intel Mac (x64):       French-Reading-Assistant-*-macos-x64.zip

NETWORK / 网络
  PDF stays local; TTS and AI need internet.

Powered by Stirling PDF — https://github.com/Stirling-Tools/Stirling-PDF
