# LLM 集成说明（M4）

French Reader 使用 **sidecar engine**（`:5002`），不修改 Stirling 专有 `engine/`。

## 当前方案

| 项 | 选择 |
|----|------|
| 协议 | OpenAI Chat Completions（`stream: true`） |
| 配置 | 环境变量（见下） |
| 端点 | `POST /french-reader/ai/explain` → SSE |
| 模式 | `translate`（M4 MVP）、`vocabulary`、`grammar` |

## 环境变量

| 变量 | 说明 |
|------|------|
| `FRENCH_READER_LLM_API_KEY` | API Key（优先） |
| `OPENAI_API_KEY` | 未设置上项时回退 |
| `FRENCH_READER_LLM_BASE_URL` | 默认 `https://api.openai.com/v1`，兼容 Azure / 本地 Ollama OpenAI 网关 |
| `FRENCH_READER_LLM_MODEL` | 默认 `gpt-4o-mini` |
| `FRENCH_READER_AI_MAX_CHARS` | 单次上限，默认 5000 |

## 与 Stirling 的关系

上游 Stirling Agent Chat 的 LLM 配置在完整 submodule 中；本仓库 sidecar **暂不读取** Stirling engine 配置，避免耦合与许可证风险。

生产可选 **M305 Java 代理**：`8080/api/v1/french-reader/ai/explain` → sidecar，与 OCR/TTS 同模式。

## Prompt 模板

见 `extensions/french-reader-engine/src/french_reader/prompts/templates.py`。
