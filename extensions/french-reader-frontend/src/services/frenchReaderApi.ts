import type { OcrHistoryEntry } from "@app/hooks/tools/frenchReader/historyTypes";
import type {
  AiExplainMode,
  AiStatusResponse,
  FrenchReaderSelection,
  OcrResult,
  TtsRate,
  TtsVoicesResponse,
} from "@app/hooks/tools/frenchReader/types";

const API_BASE =
  import.meta.env.VITE_FRENCH_READER_API_URL ?? "/french-reader";

interface OcrRegionResponse {
  text: string;
  confidence: number;
  lines: { text: string; confidence: number }[];
}

async function readErrorDetail(response: Response): Promise<string> {
  let detail = response.statusText;
  try {
    const body = (await response.json()) as { detail?: string };
    if (body.detail) detail = body.detail;
  } catch {
    // ignore parse errors
  }
  return detail || "Request failed";
}

export async function ocrRegion(
  imageBase64: string,
  selection: FrenchReaderSelection,
): Promise<OcrResult> {
  const response = await fetch(`${API_BASE}/ocr/region`, {
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

export async function fetchTtsVoices(lang = "fr"): Promise<TtsVoicesResponse> {
  const response = await fetch(`${API_BASE}/tts/voices?lang=${encodeURIComponent(lang)}`);
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
  const response = await fetch(`${API_BASE}/tts/synthesize`, {
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

export async function fetchAiStatus(): Promise<AiStatusResponse> {
  const response = await fetch(`${API_BASE}/ai/status`);
  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }
  return (await response.json()) as AiStatusResponse;
}

export async function streamAiExplain(
  params: {
    text: string;
    mode: AiExplainMode;
    targetLang?: string;
    userApiKey?: string;
  },
  onDelta: (chunk: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const userApiKey = params.userApiKey?.trim();
  const response = await fetch(`${API_BASE}/ai/explain`, {
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
  const response = await fetch(`${API_BASE}/export/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_file_name: params.sourceFileName,
      entries: params.entries.map((entry) => ({
        id: entry.id,
        created_at: entry.createdAt,
        file_name: entry.fileName,
        page: entry.page,
        text: entry.text,
        confidence: entry.confidence,
        translations: entry.translations,
        translation: entry.translation,
        translation_mode: entry.translationMode,
      })),
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorDetail(response));
  }

  return response.blob();
}
