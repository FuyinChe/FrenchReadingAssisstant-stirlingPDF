import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { isStirlingFile } from "@app/types/fileContext";
import { BubbleOverlay } from "@app/components/frenchReader/BubbleOverlay";
import { RegionSelector } from "@app/components/frenchReader/RegionSelector";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import { useFrenchReaderOcr } from "@app/hooks/tools/frenchReader/useFrenchReaderOcr";
import type { NormalizedBBox } from "@app/hooks/tools/frenchReader/types";
import { useViewScopedFiles } from "@app/hooks/tools/shared/useViewScopedFiles";

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
  const { runOcr } = useFrenchReaderOcr();
  const {
    selection,
    ocrLoading,
    getBubblesForPage,
  } = useFrenchReaderContext();

  const bubbles = getBubblesForPage(pageNumber);

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

  const handleRegionComplete = async (bbox: NormalizedBBox) => {
    if (!activeFile) {
      return;
    }

    await runOcr({
      file: activeFile,
      fileName:
        activeFile && isStirlingFile(activeFile)
          ? activeFile.name
          : "document.pdf",
      pageNumber,
      pageIndex,
      bbox,
    });
  };

  const handleBubbleClick = async (bbox: NormalizedBBox) => {
    if (!activeFile || ocrLoading) {
      return;
    }

    await runOcr({
      file: activeFile,
      fileName:
        activeFile && isStirlingFile(activeFile)
          ? activeFile.name
          : "document.pdf",
      pageNumber,
      pageIndex,
      bbox,
    });
  };

  if (!mountNode) {
    return null;
  }

  return createPortal(
    <>
      <RegionSelector pageIndex={pageIndex} onComplete={handleRegionComplete} />
      <BubbleOverlay
        bubbles={bubbles}
        activeBbox={selection?.page === pageNumber ? selection.bbox : null}
        disabled={ocrLoading}
        onBubbleClick={handleBubbleClick}
      />
    </>,
    mountNode,
  );
}
