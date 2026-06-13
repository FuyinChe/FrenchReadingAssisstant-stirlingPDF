import { useCallback, useEffect, useRef, useState } from "react";

import type { AiExplainMode, AiTranslationResults } from "@app/hooks/tools/frenchReader/types";
import { fetchAiStatus, streamAiExplain } from "@app/services/frenchReaderApi";

interface UseAiExplainOptions {
  text: string;
  modes: AiExplainMode[];
  targetLang: string;
  userApiKey?: string;
  onComplete?: (mode: AiExplainMode, result: string) => void;
}

export function useAiExplain({
  text,
  modes,
  targetLang,
  userApiKey = "",
  onComplete,
}: UseAiExplainOptions) {
  const [serverReady, setServerReady] = useState<boolean | null>(null);
  const [aiDetail, setAiDetail] = useState("");
  const [results, setResults] = useState<AiTranslationResults>({});
  const [activeMode, setActiveMode] = useState<AiExplainMode | null>(null);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const onCompleteRef = useRef(onComplete);

  const trimmedUserKey = userApiKey.trim();
  const aiReady =
    serverReady === null ? null : serverReady || Boolean(trimmedUserKey);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    let cancelled = false;
    fetchAiStatus()
      .then((status) => {
        if (cancelled) return;
        setServerReady(Boolean(status.server_configured ?? status.ready));
        setAiDetail(status.detail);
      })
      .catch((err) => {
        if (cancelled) return;
        setServerReady(Boolean(trimmedUserKey));
        setAiDetail(err instanceof Error ? err.message : "AI status unavailable");
      });

    return () => {
      cancelled = true;
    };
  }, [trimmedUserKey]);

  useEffect(() => {
    setResults({});
    setActiveMode(null);
    setError(null);
    abortRef.current?.abort();
    abortRef.current = null;
    setStreaming(false);
    setLoading(false);
  }, [text]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setActiveMode(null);
    setStreaming(false);
    setLoading(false);
  }, []);

  const run = useCallback(async () => {
    if (!text.trim() || aiReady === false || modes.length === 0) return;

    stop();
    setResults({});
    setError(null);
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      for (const mode of modes) {
        if (controller.signal.aborted) return;

        setActiveMode(mode);
        setStreaming(true);
        let finalResult = "";

        await streamAiExplain(
          { text, mode, targetLang, userApiKey: trimmedUserKey || undefined },
          (chunk) => {
            finalResult += chunk;
            setResults((prev) => ({
              ...prev,
              [mode]: `${prev[mode] ?? ""}${chunk}`,
            }));
          },
          controller.signal,
        );

        onCompleteRef.current?.(mode, finalResult);
      }
    } catch (err) {
      if (controller.signal.aborted) return;
      const message = err instanceof Error ? err.message : "AI request failed";
      setError(message);
    } finally {
      if (!controller.signal.aborted) {
        setActiveMode(null);
        setStreaming(false);
        setLoading(false);
      }
      abortRef.current = null;
    }
  }, [aiReady, modes, stop, targetLang, text, trimmedUserKey]);

  useEffect(() => () => stop(), [stop]);

  return {
    aiReady,
    aiDetail,
    results,
    activeMode,
    loading,
    streaming,
    error,
    run,
    stop,
    canRun: Boolean(text.trim() && aiReady && modes.length > 0),
  };
}
