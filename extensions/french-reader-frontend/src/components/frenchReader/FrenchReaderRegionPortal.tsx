import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { RegionSelector } from "@app/components/frenchReader/RegionSelector";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import { cropPageRegionToBase64 } from "@app/services/cropPageRegion";
import { ocrRegion } from "@app/services/frenchReaderApi";
import { useViewScopedFiles } from "@app/hooks/tools/shared/useViewScopedFiles";
import type { NormalizedBBox } from "@app/hooks/tools/frenchReader/types";

interface FrenchReaderRegionPortalProps {
  pageNumber: number;
  pageIndex: number;
}

export function FrenchReaderRegionPortal({
  pageNumber,
  pageIndex,
}: FrenchReaderRegionPortalProps) {
  const [mountNode, setMountNode] = useState<HTMLElement | null>(null);
  const scopedFiles = useViewScopedFiles();
  const activeFile = scopedFiles[0];
  const {
    setSelection,
    setOcrLoading,
    setOcrResult,
    setOcrError,
  } = useFrenchReaderContext();

  useEffect(() => {
    const page = document.querySelector(
      `[data-page-index="${pageIndex}"]`,
    ) as HTMLElement | null;
    if (!page) {
      setMountNode(null);
      return;
    }
    const host = page;
    const previousPosition = host.style.position;
    if (!previousPosition || previousPosition === "static") {
      host.style.position = "relative";
    }
    setMountNode(host);
    return () => {
      if (!previousPosition || previousPosition === "static") {
        host.style.position = previousPosition;
      }
    };
  }, [pageIndex, pageNumber]);

  const handleComplete = async (bbox: NormalizedBBox) => {
    if (!activeFile) {
      setOcrError("No PDF file loaded");
      return;
    }

    const selection = { page: pageNumber, pageIndex, bbox };
    setSelection(selection);
    setOcrLoading(true);
    setOcrError(null);
    setOcrResult(null);

    try {
      const imageBase64 = await cropPageRegionToBase64(
        activeFile,
        pageNumber,
        bbox,
      );
      const result = await ocrRegion(imageBase64, selection);
      setOcrResult(result);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "OCR failed unexpectedly";
      setOcrError(message);
    } finally {
      setOcrLoading(false);
    }
  };

  if (!mountNode) {
    return null;
  }

  return createPortal(
    <RegionSelector pageIndex={pageIndex} onComplete={handleComplete} />,
    mountNode,
  );
}
