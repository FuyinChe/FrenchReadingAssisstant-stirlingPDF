import { useCallback, useState } from "react";

import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";
import {
  clearUserLlmApiKey,
  loadUserLlmApiKey,
  saveUserLlmApiKey,
} from "@app/services/frenchReaderUserApiKey";
import {
  loadAiPreferences,
  saveAiPreferences,
} from "@app/services/frenchReaderAiPrefs";

export function useAiSettings() {
  const [modes, setModesState] = useState<AiExplainMode[]>(
    () => loadAiPreferences().modes,
  );
  const [targetLang, setTargetLangState] = useState(
    () => loadAiPreferences().targetLang,
  );
  const [userApiKey, setUserApiKeyState] = useState(() => loadUserLlmApiKey());

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

  const setUserApiKey = useCallback((next: string) => {
    const cleaned = next.trim();
    saveUserLlmApiKey(cleaned);
    setUserApiKeyState(cleaned);
  }, []);

  const clearUserApiKey = useCallback(() => {
    clearUserLlmApiKey();
    setUserApiKeyState("");
  }, []);

  return { modes, setModes, targetLang, setTargetLang, userApiKey, setUserApiKey, clearUserApiKey };
}
