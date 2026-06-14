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

export interface DetectedBubble {
  bbox: NormalizedBBox;
  confidence: number;
  detector: string;
}

export interface AutoBubblesResponse {
  page: number;
  bubbles: DetectedBubble[];
  detector: string;
  preprocess: boolean;
}

export interface BubbleDetectorStatusResponse {
  ready: boolean;
  opencv_available: boolean;
  yolo_available: boolean;
  detail: string;
  default_model: string;
}
