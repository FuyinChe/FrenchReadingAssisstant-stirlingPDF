export interface NormalizedBBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface OcrLineResult {
  text: string;
  confidence: number;
}

export interface OcrResult {
  text: string;
  confidence: number;
  lines: OcrLineResult[];
}

export interface TtsVoice {
  id: string;
  name: string;
  locale: string;
  gender: string;
}

export interface TtsVoicesResponse {
  voices: TtsVoice[];
  default_voice: string;
}

export type TtsRate = "+0%" | "-15%" | "+15%";

export type AiExplainMode = "translate" | "vocabulary" | "grammar";

export type AiTranslationResults = Partial<Record<AiExplainMode, string>>;

export interface AiStatusResponse {
  ready: boolean;
  server_configured?: boolean;
  client_configured?: boolean;
  provider: string;
  model: string;
  detail: string;
}

export interface FrenchReaderSelection {
  page: number;
  pageIndex: number;
  bbox: NormalizedBBox;
}
