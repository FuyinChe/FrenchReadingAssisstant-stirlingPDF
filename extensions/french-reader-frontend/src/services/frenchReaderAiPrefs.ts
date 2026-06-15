import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";

const STORAGE_KEY = "french-reader-ai-prefs";

const ALL_MODES: AiExplainMode[] = ["translate", "vocabulary", "grammar"];

export interface AiPreferences {
  modes: AiExplainMode[];
  targetLang: string;
}

const DEFAULT_PREFS: AiPreferences = {
  modes: ["translate"],
  targetLang: "zh",
};

function normalizeModes(raw: unknown): AiExplainMode[] {
  if (!Array.isArray(raw)) return DEFAULT_PREFS.modes;
  const modes = raw.filter(
    (item): item is AiExplainMode =>
      typeof item === "string" && ALL_MODES.includes(item as AiExplainMode),
  );
  return modes.length > 0 ? modes : DEFAULT_PREFS.modes;
}

export function loadAiPreferences(): AiPreferences {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return DEFAULT_PREFS;
    const parsed = JSON.parse(stored) as Partial<AiPreferences>;
    return {
      modes: normalizeModes(parsed.modes),
      targetLang: parsed.targetLang === "en" ? "en" : "zh",
    };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function saveAiPreferences(prefs: AiPreferences): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      modes: normalizeModes(prefs.modes),
      targetLang: prefs.targetLang === "en" ? "en" : "zh",
    }),
  );
}

export const AI_MODE_OPTIONS: AiExplainMode[] = ALL_MODES;
