import { useCallback, useEffect, useState } from "react";

import { detectAutoBubbles, fetchBubbleDetectorStatus } from "@app/services/frenchReaderApi";
import { renderPageToBase64 } from "@app/services/renderPageToBase64";
import type { DetectedBubble } from "@app/hooks/tools/frenchReader/types";

export function useBubbleDetection() {
  const [bubblesByPage, setBubblesByPage] = useState<Record<number, DetectedBubble[]>>({});
  const [bubbleDetectLoading, setBubbleDetectLoading] = useState(false);
  const [bubbleDetectError, setBubbleDetectError] = useState<string | null>(null);
  const [bubblePreprocess, setBubblePreprocess] = useState(false);
  const [bubbleDetectorReady, setBubbleDetectorReady] = useState<boolean | null>(null);
  const [lastDetector, setLastDetector] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchBubbleDetectorStatus()
      .then((status) => {
        if (!cancelled) {
          setBubbleDetectorReady(status.ready);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setBubbleDetectorReady(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const getBubblesForPage = useCallback(
    (page: number) => bubblesByPage[page] ?? [],
    [bubblesByPage],
  );

  const setBubblesForPage = useCallback((page: number, bubbles: DetectedBubble[]) => {
    setBubblesByPage((prev) => ({ ...prev, [page]: bubbles }));
  }, []);

  const clearBubblesForPage = useCallback((page: number) => {
    setBubblesByPage((prev) => {
      if (!(page in prev)) return prev;
      const next = { ...prev };
      delete next[page];
      return next;
    });
  }, []);

  const clearAllBubbles = useCallback(() => {
    setBubblesByPage({});
    setLastDetector(null);
  }, []);

  const detectBubblesForPage = useCallback(
    async (params: {
      file: File | Blob;
      pageNumber: number;
      confidenceThreshold?: number;
    }) => {
      setBubbleDetectLoading(true);
      setBubbleDetectError(null);
      try {
        const imageBase64 = await renderPageToBase64(params.file, params.pageNumber);
        const response = await detectAutoBubbles({
          imageBase64,
          page: params.pageNumber,
          confidenceThreshold: params.confidenceThreshold,
          preprocess: bubblePreprocess,
        });
        setBubblesForPage(params.pageNumber, response.bubbles);
        setLastDetector(response.detector);
        return response;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Bubble detection failed";
        setBubbleDetectError(message);
        throw error;
      } finally {
        setBubbleDetectLoading(false);
      }
    },
    [bubblePreprocess, setBubblesForPage],
  );

  return {
    bubblesByPage,
    getBubblesForPage,
    setBubblesForPage,
    clearBubblesForPage,
    clearAllBubbles,
    detectBubblesForPage,
    bubbleDetectLoading,
    bubbleDetectError,
    bubblePreprocess,
    setBubblePreprocess,
    bubbleDetectorReady,
    lastDetector,
  };
}
