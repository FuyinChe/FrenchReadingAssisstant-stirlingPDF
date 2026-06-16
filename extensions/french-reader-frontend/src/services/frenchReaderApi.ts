import type { OcrHistoryEntry } from "@app/hooks/tools/frenchReader/historyTypes";
import type {
  AiExplainMode,
  AiStatusResponse,
  AutoBubblesResponse,
  AutoParagraphsResponse,
  BubbleDetectorStatusResponse,
  FrenchReaderSelection,
  LlmProvidersResponse,
  OcrResult,
  ParagraphDetectorStatusResponse,
  TtsRate,
  TtsVoicesResponse,
} from "@app/hooks/tools/frenchReader/types";
import type { UserLlmSettings } from "@app/services/frenchReaderLlmSettings";
import { FALLBACK_LLM_PROVIDERS, providerRequiresEndpoint } from "@app/services/frenchReaderLlmSettings";
import { frenchReaderFetch } from "@app/services/frenchReaderFetch";

const API_BASE =
  import.meta.env.VITE_FRENCH_READER_API_URL ?? "/french-reader";

interface OcrRegionResponse {
  text: string;
  confidence: number;
  lines: { text: string; confidence: number }[];
}

interface FastApiValidationError {
  loc?: (string | number)[];
  msg?: string;
}

async function readErrorDetail(response: Response): Promise<string> {
  let detail = response.statusText;
  try {
    const body = (await response.json()) as {
      detail?: string | FastApiValidationError[];
    };
    if (typeof body.detail === "string") {
      detail = body.detail;
    } else if (Array.isArray(body.detail)) {
      detail = body.detail
        .map((item) => {
          if (typeof item === "string") return item;
          const path = item.loc?.slice(1).join(".") ?? "request";
          return `${path}: ${item.msg ?? "invalid"}`;
        })
        .join("; ");
    }
  } catch {
    // ignore parse errors
  }
  return detail || "Request failed";
}

const EXPORT_MODES = ["translate", "vocabulary", "grammar"] as const;

function normalizeExportConfidence(value: number): number {
  if (!Number.isFinite(value)) return 0;
  let confidence = value;
  if (confidence > 1) confidence /= 100;
  return Math.min(1, Math.max(0, confidence));
}

function sanitizeExportTranslations(
  translations?: OcrHistoryEntry["translations"],
): Partial<Record<(typeof EXPORT_MODES)[number], string>> | undefined {
  if (!translations) return undefined;
  const out: Partial<Record<(typeof EXPORT_MODES)[number], string>> = {};
  for (const mode of EXPORT_MODES) {
    const text = translations[mode]?.trim();
    if (text) out[mode] = text;
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

function serializeHistoryExportEntries(entries: OcrHistoryEntry[]) {
  return entries.flatMap((entry) => {
    const text = entry.text?.trim() ?? "";
    if (!text) return [];

    const translationMode =
      entry.translationMode && EXPORT_MODES.includes(entry.translationMode)
        ? entry.translationMode
        : undefined;

    return [
      {
        id: entry.id,
        created_at: entry.createdAt,
        file_name: entry.fileName || "document",
        page: Math.max(1, entry.page || 1),
        text,
        confidence: normalizeExportConfidence(entry.confidence),
        translations: sanitizeExportTranslations(entry.translations),
        translation: entry.translation?.trim() || undefined,
        translation_mode: translationMode,
      },
    ];
  });
}

export async function ocrRegion(
  imageBase64: string,
  selection: FrenchReaderSelection,
): Promise<OcrResult> {
  const response = await frenchReaderFetch(`${API_BASE}/ocr/region`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_base64: imageBase64,
      page: selection.page,
      bbox: selection.bbox,
      lang: "fr",
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  const data = (await response.json()) as OcrRegionResponse;
  return {
    text: data.text,
    confidence: data.confidence,
    lines: data.lines ?? [],
  };
}

export async function fetchBubbleDetectorStatus(): Promise<BubbleDetectorStatusResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/ocr/bubbles/status`);
  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }
  return (await response.json()) as BubbleDetectorStatusResponse;
}

export async function detectAutoBubbles(params: {
  imageBase64: string;
  page: number;
  confidenceThreshold?: number;
  preprocess?: boolean;
  preferYolo?: boolean;
}): Promise<AutoBubblesResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/ocr/auto-bubbles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_base64: params.imageBase64,
      page: params.page,
      confidence_threshold: params.confidenceThreshold ?? 0.35,
      preprocess: params.preprocess ?? false,
      prefer_yolo: params.preferYolo ?? true,
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return (await response.json()) as AutoBubblesResponse;
}

export async function fetchParagraphDetectorStatus(): Promise<ParagraphDetectorStatusResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/ocr/paragraphs/status`);
  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }
  return (await response.json()) as ParagraphDetectorStatusResponse;
}

export async function detectAutoParagraphs(params: {
  imageBase64: string;
  page: number;
  confidenceThreshold?: number;
  preprocess?: boolean;
}): Promise<AutoParagraphsResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/ocr/auto-paragraphs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_base64: params.imageBase64,
      page: params.page,
      confidence_threshold: params.confidenceThreshold ?? 0.35,
      preprocess: params.preprocess ?? false,
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return (await response.json()) as AutoParagraphsResponse;
}

export async function fetchTtsVoices(lang = "fr"): Promise<TtsVoicesResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/tts/voices?lang=${encodeURIComponent(lang)}`);
  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }
  return (await response.json()) as TtsVoicesResponse;
}

export async function synthesizeTts(params: {
  text: string;
  voice: string;
  rate?: TtsRate;
}): Promise<Blob> {
  const response = await frenchReaderFetch(`${API_BASE}/tts/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: params.text,
      voice: params.voice,
      rate: params.rate ?? "+0%",
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return response.blob();
}

export async function fetchAiStatus(
  llmSettings?: Pick<UserLlmSettings, "providerId" | "apiKey" | "customBaseUrl" | "customModel">,
): Promise<AiStatusResponse> {
  const params = new URLSearchParams();
  const apiKey = llmSettings?.apiKey?.trim();
  if (apiKey) params.set("api_key", apiKey);
  if (llmSettings?.providerId) params.set("provider", llmSettings.providerId);
  if (llmSettings && providerRequiresEndpoint(llmSettings.providerId)) {
    if (llmSettings.customBaseUrl) params.set("base_url", llmSettings.customBaseUrl);
    if (llmSettings.customModel) params.set("model", llmSettings.customModel);
  }
  const query = params.toString();
  const response = await frenchReaderFetch(`${API_BASE}/ai/status${query ? `?${query}` : ""}`);
  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }
  return (await response.json()) as AiStatusResponse;
}

export async function fetchLlmProviders(): Promise<LlmProvidersResponse> {
  const response = await frenchReaderFetch(`${API_BASE}/ai/providers`);
  if (!response.ok) {
    return {
      default_provider: "kimi",
      providers: FALLBACK_LLM_PROVIDERS,
    };
  }
  return (await response.json()) as LlmProvidersResponse;
}

export async function streamAiExplain(
  params: {
    text: string;
    mode: AiExplainMode;
    targetLang?: string;
    llmSettings?: UserLlmSettings;
  },
  onDelta: (chunk: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const llmSettings = params.llmSettings;
  const userApiKey = llmSettings?.apiKey?.trim();
  const response = await frenchReaderFetch(`${API_BASE}/ai/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      text: params.text,
      mode: params.mode,
      target_lang: params.targetLang ?? "zh",
      ...(userApiKey ? { api_key: userApiKey } : {}),
      ...(llmSettings?.providerId ? { provider: llmSettings.providerId } : {}),
      ...(llmSettings && providerRequiresEndpoint(llmSettings.providerId) && llmSettings.customBaseUrl
        ? { base_url: llmSettings.customBaseUrl }
        : {}),
      ...(llmSettings && providerRequiresEndpoint(llmSettings.providerId) && llmSettings.customModel
        ? { model: llmSettings.customModel }
        : {}),
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Streaming response unavailable");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      for (const line of event.split("\n")) {
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (!payload || payload === "[DONE]") continue;

        let parsed: { delta?: string; error?: string };
        try {
          parsed = JSON.parse(payload) as { delta?: string; error?: string };
        } catch {
          continue;
        }

        if (parsed.error) {
          throw new Error(parsed.error);
        }
        if (parsed.delta) {
          onDelta(parsed.delta);
        }
      }
    }
  }
}

export async function exportHistoryPdf(params: {
  sourceFileName: string;
  entries: OcrHistoryEntry[];
}): Promise<Blob> {
  const entries = serializeHistoryExportEntries(params.entries);
  if (entries.length === 0) {
    throw new Error("No history entries with recognized text to export");
  }

  const response = await frenchReaderFetch(`${API_BASE}/export/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_file_name: params.sourceFileName.trim() || "notes",
      entries,
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return response.blob();
}
