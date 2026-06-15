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

export interface LlmProviderInfo {
  id: string;
  name: string;
  base_url: string;
  default_model: string;
  key_hint: string;
  docs_url: string;
  api_style?: string;
  requires_endpoint?: boolean;
  group?: string;
}

export interface LlmProvidersResponse {
  default_provider: string;
  providers: LlmProviderInfo[];
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

export interface DetectedParagraph {
  bbox: NormalizedBBox;
  confidence: number;
  detector: string;
  order: number;
}

export interface AutoParagraphsResponse {
  page: number;
  paragraphs: DetectedParagraph[];
  detector: string;
  preprocess: boolean;
}

export interface ParagraphDetectorStatusResponse {
  ready: boolean;
  opencv_available: boolean;
  detail: string;
}
