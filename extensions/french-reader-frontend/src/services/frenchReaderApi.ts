import type { OcrResult, FrenchReaderSelection } from "@app/hooks/tools/frenchReader/types";

const API_BASE =
  import.meta.env.VITE_FRENCH_READER_API_URL ?? "/french-reader";

interface OcrRegionResponse {
  text: string;
  confidence: number;
  lines: { text: string; confidence: number }[];
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
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail || "OCR request failed");
  }

  const data = (await response.json()) as OcrRegionResponse;
  return {
    text: data.text,
    confidence: data.confidence,
    lines: data.lines ?? [],
  };
}
