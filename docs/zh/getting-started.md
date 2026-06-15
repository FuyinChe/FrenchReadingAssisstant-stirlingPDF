# 快速开始

**French Reading Assistant for Stirling PDF** 是基于 [**Stirling PDF**](https://github.com/Stirling-Tools/Stirling-PDF) 的插件扩展。使用本仓库时需同时拉取 Stirling 子模块（`stirling-upstream/`），Stirling 不会单独打包下载，而是通过 `git submodule` 引入。

| | |
|---|---|
| **本仓库** | [FuyinChe/FrenchReadingAssisstant-stirlingPDF](https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF) |
| **基座（上游）** | [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) |
| **Stirling 官方文档** | [docs.stirlingpdf.com](https://docs.stirlingpdf.com/) |

[English getting started](../en/getting-started.md)

---

## 环境要求

| 依赖 | 用途 |
|------|------|
| Git + submodule | 拉取 Stirling 上游代码 |
| Docker Desktop / Engine | Docker 部署（推荐给最终用户） |
| JDK 25、Node 20+、Task、uv | 仅本地开发需要 |

---

## 克隆仓库

```bash
git clone --recursive https://github.com/FuyinChe/FrenchReadingAssisstant-stirlingPDF.git
cd FrenchReadingAssisstant-stirlingPDF
```

若已 clone 但未初始化子模块：

```bash
git submodule update --init --recursive
```

子模块指向 [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF.git)（见 `.gitmodules`）。

---

## Docker 部署（推荐）

在**本机构建**镜像，**不会**自动上传到 Docker Hub。

```bash
chmod +x scripts/*.sh
cp .env.docker.example .env    # 可选：FRENCH_READER_LLM_API_KEY
./scripts/docker-up.sh
# 等价于：docker compose up --build
```

- 首次构建可能需要 **30–60 分钟**（Stirling + 前端 + JDK）。
- 浏览器打开 http://localhost:8080
- 进入 **Recommended tools（推荐工具）** → **French Reading Assistant**

可选环境变量见 [.env.docker.example](../../.env.docker.example)。

---

## 开发模式运行

```bash
chmod +x scripts/*.sh
./scripts/install-extensions.sh
./scripts/dev.sh
```

| 服务 | 地址 |
|------|------|
| Stirling 前端 | http://localhost:5173 |
| Stirling 后端 | http://localhost:8080 |
| French Reader 引擎 | http://localhost:5002 |

完整开发说明：[dev-setup.md](../dev-setup.md)。

---

## 桌面版（Tauri）

在 Stirling 桌面构建中启用 French Reader：

```bash
./scripts/build-desktop.sh
./scripts/desktop-dev.sh
```

Rust / JDK 要求见 [Stirling DeveloperGuide](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/DeveloperGuide.md)。

---

## AI 配置

任选其一：

1. **应用内：** Settings（齿轮）→ 选择 LLM 厂商并填写 API Key → Save  
2. **环境变量：** 在 `.env` 中设置 `FRENCH_READER_LLM_API_KEY`（开发或 Docker sidecar）

---

## 下一步

- [用户手册（含截图占位）](user-guide.md)
- [文档中心](../README.md)
- [Sidecar 降级部署](../deployment/sidecar-fallback.md)
