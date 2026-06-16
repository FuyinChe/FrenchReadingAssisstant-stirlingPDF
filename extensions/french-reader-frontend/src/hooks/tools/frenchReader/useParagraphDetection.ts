import { useCallback, useEffect, useState } from "react";

import {
  detectAutoParagraphs,
  fetchParagraphDetectorStatus,
} from "@app/services/frenchReaderApi";
import { renderPageToBase64 } from "@app/services/renderPageToBase64";
import type { DetectedParagraph } from "@app/hooks/tools/frenchReader/types";

export function useParagraphDetection() {
  const [paragraphsByPage, setParagraphsByPage] = useState<
    Record<number, DetectedParagraph[]>
  >({});
  const [paragraphDetectLoading, setParagraphDetectLoading] = useState(false);
  const [paragraphDetectError, setParagraphDetectError] = useState<string | null>(null);
  const [paragraphPreprocess, setParagraphPreprocess] = useState(false);
  const [paragraphDetectorReady, setParagraphDetectorReady] = useState<boolean | null>(
    null,
  );
  const [paragraphStatusLoadFailed, setParagraphStatusLoadFailed] = useState(false);
  const [lastParagraphDetector, setLastParagraphDetector] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchParagraphDetectorStatus()
      .then((status) => {
        if (!cancelled) {
          setParagraphDetectorReady(status.opencv_available);
          setParagraphStatusLoadFailed(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setParagraphDetectorReady(null);
          setParagraphStatusLoadFailed(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const getParagraphsForPage = useCallback(
    (page: number) => paragraphsByPage[page] ?? [],
    [paragraphsByPage],
  );

  const setParagraphsForPage = useCallback(
    (page: number, paragraphs: DetectedParagraph[]) => {
      setParagraphsByPage((prev) => ({ ...prev, [page]: paragraphs }));
    },
    [],
  );

  const clearParagraphsForPage = useCallback((page: number) => {
    setParagraphsByPage((prev) => {
      if (!(page in prev)) return prev;
      const next = { ...prev };
      delete next[page];
      return next;
    });
  }, []);

  const clearAllParagraphs = useCallback(() => {
    setParagraphsByPage({});
    setLastParagraphDetector(null);
  }, []);

  const detectParagraphsForPage = useCallback(
    async (params: {
      file: File | Blob;
      pageNumber: number;
      confidenceThreshold?: number;
    }) => {
      setParagraphDetectLoading(true);
      setParagraphDetectError(null);
      try {
        const imageBase64 = await renderPageToBase64(params.file, params.pageNumber);
        const response = await detectAutoParagraphs({
          imageBase64,
          page: params.pageNumber,
          confidenceThreshold: params.confidenceThreshold,
          preprocess: paragraphPreprocess,
        });
        setParagraphsForPage(params.pageNumber, response.paragraphs);
        setLastParagraphDetector(response.detector);
        return response;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Paragraph detection failed";
        setParagraphDetectError(message);
        throw error;
      } finally {
        setParagraphDetectLoading(false);
      }
    },
    [paragraphPreprocess, setParagraphsForPage],
  );

  return {
    paragraphsByPage,
    getParagraphsForPage,
    setParagraphsForPage,
    clearParagraphsForPage,
    clearAllParagraphs,
    detectParagraphsForPage,
    paragraphDetectLoading,
    paragraphDetectError,
    paragraphPreprocess,
    setParagraphPreprocess,
    paragraphDetectorReady,
    paragraphStatusLoadFailed,
    lastParagraphDetector,
  };
}
