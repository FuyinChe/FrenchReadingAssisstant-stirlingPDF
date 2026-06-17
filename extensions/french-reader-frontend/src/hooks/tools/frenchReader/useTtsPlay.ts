import { useCallback, useEffect, useRef, useState } from "react";

import type { OcrLineResult, TtsRate } from "@app/hooks/tools/frenchReader/types";
import { synthesizeTts } from "@app/services/frenchReaderApi";
import { playTtsAudio } from "@app/services/playTtsAudio";

function segmentsFromText(text: string, lines: OcrLineResult[]): string[] {
  if (lines.length > 0) {
    return lines.map((line) => line.text).filter((line) => line.trim());
  }
  return text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

export function useTtsPlay() {
  const [synthesizing, setSynthesizing] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  const releaseAudio = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setPlaying(false);
  }, []);

  useEffect(() => () => releaseAudio(), [releaseAudio]);

  const stop = useCallback(() => {
    releaseAudio();
    setSynthesizing(false);
  }, [releaseAudio]);

  const play = useCallback(
    async (text: string, lines: OcrLineResult[], voice: string, rate: TtsRate) => {
      if (!text.trim() || !voice) return;

      stop();
      const segments = segmentsFromText(text, lines);
      if (segments.length === 0) return;

      const controller = new AbortController();
      abortRef.current = controller;
      setError(null);

      for (const segment of segments) {
        if (controller.signal.aborted) return;

        setSynthesizing(true);
        let blob: Blob;
        try {
          blob = await synthesizeTts({ text: segment, voice, rate });
        } catch (err) {
          if (controller.signal.aborted) return;
          setError(err instanceof Error ? err.message : "TTS failed");
          setSynthesizing(false);
          return;
        } finally {
          setSynthesizing(false);
        }

        if (controller.signal.aborted) return;

        setPlaying(true);
        try {
          await playTtsAudio(blob, controller.signal);
        } catch (err) {
          if (!controller.signal.aborted) {
            const message = err instanceof Error ? err.message : "Playback failed";
            setError(
              message.toLowerCase().includes("not supported")
                ? "TTS audio playback is not supported in this environment. Try updating the app."
                : message,
            );
          }
        }

        if (controller.signal.aborted) return;
      }

      setPlaying(false);
    },
    [stop],
  );

  return {
    play,
    stop,
    synthesizing,
    playing,
    error,
    busy: synthesizing || playing,
  };
}
