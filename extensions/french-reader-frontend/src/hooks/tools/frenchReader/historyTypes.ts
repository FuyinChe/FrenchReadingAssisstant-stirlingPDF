import type { AiExplainMode, AiTranslationResults, OcrLineResult, TtsRate } from "@app/hooks/tools/frenchReader/types";

export interface OcrHistoryEntry {
  id: string;
  createdAt: string;
  fileName: string;
  page: number;
  text: string;
  lines: OcrLineResult[];
  confidence: number;
  translation?: string;
  translationMode?: AiExplainMode;
  translations?: AiTranslationResults;
}

export interface TtsPreferences {
  voice: string;
  rate: TtsRate;
}
