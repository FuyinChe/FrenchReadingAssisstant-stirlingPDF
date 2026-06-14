# Sidecar 降级部署方案

当无法或不想修改 Stirling 源码/镜像时，French Reader 可以 **完全以 sidecar 形式独立运行**，Stirling 仅作为 PDF 宿主（甚至可以是未打补丁的上游 Stirling）。

## 架构

```text
浏览器
  ├─ Stirling UI (:8080 或 :5173)     ← 标准 Stirling，可无 French Reader Tool
  └─ 独立 French Reader 页面 (可选)   ← 未来外链入口

French Reader engine (:5002)
  └─ /french-reader/*  API
```

当前 MVP 中 Tool UI **内嵌在 Stirling 前端**；降级模式下有两种用法：

1. **开发 proxy**：Vite 将 `/french-reader` 代理到 `:5002`（已内置）。
2. **生产 gateway**：Nginx 将 `/french-reader` 代理到 sidecar（见 `docker/gateway/nginx.conf`）。

若 Stirling 前端 **未** 安装扩展，用户看不到 Tool，但 API 仍可被其他客户端调用。

---

## 仅运行 sidecar

```bash
cd extensions/french-reader-engine
uv sync --dev --extra bubble
./scripts/setup-ocr.sh   # 首次
uv run uvicorn french_reader.main:app --host 0.0.0.0 --port 5002
```

验证：

```bash
curl http://localhost:5002/health
curl http://localhost:5002/french-reader/ai/providers
```

---

## 与上游 Stirling 并存（零改 Stirling 源码）

1. 正常启动上游 Stirling（Docker 官方镜像或 `task dev`）。
2. 单独启动 French Reader sidecar（上节）。
3. 在前端增加反向代理，使浏览器能访问 `/french-reader`：

### Nginx 示例

```nginx
location /french-reader/ {
    proxy_pass http://127.0.0.1:5002/french-reader/;
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_read_timeout 600s;
}
```

### CORS

若前端与 API 不同源，设置：

```bash
export FRENCH_READER_CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

---

## Docker：仅 engine 服务

```bash
docker build -f docker/french-reader-engine/Dockerfile -t french-pdf-reader-engine .
docker run --rm -p 5002:5002 --env-file .env french-pdf-reader-engine
```

自行将 Stirling 或 Nginx 的 `/french-reader` 指到该容器。

---

## 与完整 Docker 栈的区别

| 方案 | Stirling 镜像 | French Reader UI | 复杂度 |
|------|---------------|------------------|--------|
| 完整栈 `docker-compose.yml` | 扩展构建（含 Tool） | ✅ | 高 |
| Sidecar 降级 | 官方/上游 | ❌（除非另接 UI） | 低 |

完整栈见仓库根目录 `docker-compose.yml` 与 `./scripts/docker-up.sh`。

---

## 何时选用降级方案

- 频繁同步 Stirling 上游，暂不想维护扩展 Docker 构建。
- 仅需 API（自动化 OCR/TTS/AI），不需要 Tool UI。
- 在已有 Stirling 部署上 **追加** 法语能力，不改现有镜像。

---

## 环境变量

与 sidecar 相同，见 [dev-setup.md](../dev-setup.md) 与 `.env.example`。
