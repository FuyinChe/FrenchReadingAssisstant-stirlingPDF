import { useCallback, useEffect, useState } from "react";

import type { TtsRate } from "@app/hooks/tools/frenchReader/types";
import { fetchTtsVoices } from "@app/services/frenchReaderApi";
import {
  loadTtsPreferences,
  saveTtsPreferences,
} from "@app/services/frenchReaderTtsPrefs";

export function useTtsSettings() {
  const [voices, setVoices] = useState<{ value: string; label: string }[]>([]);
  const [voice, setVoiceState] = useState(() => loadTtsPreferences().voice);
  const [rate, setRateState] = useState<TtsRate>(() => loadTtsPreferences().rate);
  const [loadingVoices, setLoadingVoices] = useState(true);
  const [voicesError, setVoicesError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchTtsVoices("fr")
      .then((response) => {
        if (cancelled) return;
        const options = response.voices.map((item) => ({
          value: item.id,
          label: `${item.name} (${item.locale})`,
        }));
        setVoices(options);
        const prefs = loadTtsPreferences();
        const resolved =
          prefs.voice && options.some((item) => item.value === prefs.voice)
            ? prefs.voice
            : response.default_voice;
        setVoiceState(resolved);
        saveTtsPreferences({ voice: resolved, rate: prefs.rate });
      })
      .catch((err) => {
        if (cancelled) return;
        setVoicesError(err instanceof Error ? err.message : "Failed to load voices");
      })
      .finally(() => {
        if (!cancelled) setLoadingVoices(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const setVoice = useCallback(
    (next: string) => {
      setVoiceState(next);
      saveTtsPreferences({ voice: next, rate });
    },
    [rate],
  );

  const setRate = useCallback(
    (next: TtsRate) => {
      setRateState(next);
      saveTtsPreferences({ voice, rate: next });
    },
    [voice],
  );

  return {
    voices,
    voice,
    setVoice,
    rate,
    setRate,
    loadingVoices,
    voicesError,
  };
}
