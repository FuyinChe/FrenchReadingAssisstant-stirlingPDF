import { useCallback, useState } from "react";

import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";
import {
  loadAiPreferences,
  saveAiPreferences,
} from "@app/services/frenchReaderAiPrefs";
import {
  clearUserLlmSettings,
  loadUserLlmSettings,
  saveUserLlmSettings,
  type UserLlmSettings,
} from "@app/services/frenchReaderLlmSettings";

export function useAiSettings() {
  const [modes, setModesState] = useState<AiExplainMode[]>(
    () => loadAiPreferences().modes,
  );
  const [targetLang, setTargetLangState] = useState(
    () => loadAiPreferences().targetLang,
  );
  const [llmSettings, setLlmSettingsState] = useState<UserLlmSettings>(
    () => loadUserLlmSettings(),
  );

  const setModes = useCallback(
    (next: AiExplainMode[]) => {
      const cleaned = next.length > 0 ? next : loadAiPreferences().modes;
      setModesState(cleaned);
      saveAiPreferences({ modes: cleaned, targetLang });
    },
    [targetLang],
  );

  const setTargetLang = useCallback(
    (next: string) => {
      const cleaned = next === "en" ? "en" : "zh";
      setTargetLangState(cleaned);
      saveAiPreferences({ modes, targetLang: cleaned });
    },
    [modes],
  );

  const saveLlmSettings = useCallback((next: UserLlmSettings) => {
    const cleaned: UserLlmSettings = {
      providerId: next.providerId.trim() || loadUserLlmSettings().providerId,
      apiKey: next.apiKey.trim(),
      customBaseUrl: next.customBaseUrl.trim(),
      customModel: next.customModel.trim(),
    };
    saveUserLlmSettings(cleaned);
    setLlmSettingsState(cleaned);
  }, []);

  const clearLlmSettings = useCallback(() => {
    clearUserLlmSettings();
    setLlmSettingsState(loadUserLlmSettings());
  }, []);

  return {
    modes,
    setModes,
    targetLang,
    setTargetLang,
    llmSettings,
    saveLlmSettings,
    clearLlmSettings,
  };
}
