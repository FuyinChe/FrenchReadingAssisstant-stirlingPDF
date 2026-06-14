import { useCallback } from "react";

import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import type { NormalizedBBox } from "@app/hooks/tools/frenchReader/types";
import { cropPageRegionToBase64 } from "@app/services/cropPageRegion";
import { ocrRegion } from "@app/services/frenchReaderApi";

interface RunOcrParams {
  file: File | Blob;
  fileName: string;
  pageNumber: number;
  pageIndex: number;
  bbox: NormalizedBBox;
}

export function useFrenchReaderOcr() {
  const {
    setSelection,
    setOcrLoading,
    setOcrResult,
    setOcrError,
    recordOcrResult,
  } = useFrenchReaderContext();

  const runOcr = useCallback(
    async ({ file, fileName, pageNumber, pageIndex, bbox }: RunOcrParams) => {
      const selection = { page: pageNumber, pageIndex, bbox };
      setSelection(selection);
      setOcrLoading(true);
      setOcrError(null);
      setOcrResult(null);

      try {
        const imageBase64 = await cropPageRegionToBase64(file, pageNumber, bbox);
        const result = await ocrRegion(imageBase64, selection);
        setOcrResult(result);
        recordOcrResult({
          fileName,
          page: pageNumber,
          result,
        });
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "OCR failed unexpectedly";
        setOcrError(message);
      } finally {
        setOcrLoading(false);
      }
    },
    [
      recordOcrResult,
      setOcrError,
      setOcrLoading,
      setOcrResult,
      setSelection,
    ],
  );

  return { runOcr };
}
