import type { TtsPreferences } from "@app/hooks/tools/frenchReader/historyTypes";
import type { TtsRate } from "@app/hooks/tools/frenchReader/types";

const STORAGE_KEY = "french-reader-tts-prefs";

const DEFAULT_PREFS: TtsPreferences = {
  voice: "",
  rate: "+0%",
};

export function loadTtsPreferences(): TtsPreferences {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_PREFS;
    const parsed = JSON.parse(raw) as Partial<TtsPreferences>;
    return {
      voice: parsed.voice ?? DEFAULT_PREFS.voice,
      rate: (parsed.rate as TtsRate) ?? DEFAULT_PREFS.rate,
    };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function saveTtsPreferences(prefs: TtsPreferences): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
}
