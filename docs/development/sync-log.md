# M603 — Upstream sync log

记录 `./scripts/sync-upstream.sh` 的执行情况，便于重复合并 Stirling 主分支。

## 2026-06-14

### 2026-06-14 — 执行成功

```bash
./scripts/sync-upstream.sh
# → Fetch origin/main, merge (Already up to date), reinstall-extensions OK
```

- Submodule HEAD: 见 `stirling-upstream` 当前 commit（sync 后 `git log -1`）
- **无合并冲突**
- `install-extensions.sh` 重新应用 frontend patch + engine deps

### 修复（同日早些时候）

- `sync-upstream.sh` 原先使用 `[[ -d stirling-upstream/.git ]]`，对 git submodule（`.git` 为文件）会误判为 missing；已改为 `[[ -e .../.git ]]`。

### 推荐执行步骤

```bash
git submodule update --init --recursive
./scripts/sync-upstream.sh
cd stirling-upstream && task check   # 可选，耗时
./scripts/dev.sh                     # 冒烟
```

### 预期冲突位置

合并 `origin/main` 后若冲突，通常出现在（ reinstall 前需手动解决）：

| 文件 | 原因 |
|------|------|
| `frontend/editor/src/core/data/usePrototypeToolRegistry.tsx` | Tool 注册 patch |
| `frontend/editor/src/core/types/prototypeToolId.ts` | Tool ID patch |
| `frontend/editor/vite.config.ts` | `/french-reader` proxy |
| `public/locales/*/translation.json` | i18n（若上游也改） |

解决后：

```bash
./scripts/install-extensions.sh
```

### 本次 CI / 沙箱执行

- 在自动化环境中执行 sync 需 `git submodule` 已初始化且可访问 GitHub。
- 本地开发机请在网络可用时运行上述命令，并将结果追加到本文件（冲突文件列表、解决摘要）。

### 验证清单（sync 后）

- [ ] `./scripts/install-extensions.sh` 成功
- [ ] `./scripts/dev.sh` — Tool 可见，OCR/TTS/AI 正常
- [ ] `cd extensions/french-reader-engine && uv run pytest -q`
