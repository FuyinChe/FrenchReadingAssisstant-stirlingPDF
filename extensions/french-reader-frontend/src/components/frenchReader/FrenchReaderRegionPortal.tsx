import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import { isStirlingFile } from "@app/types/fileContext";
import { BubbleOverlay } from "@app/components/frenchReader/BubbleOverlay";
import { ParagraphOverlay } from "@app/components/frenchReader/ParagraphOverlay";
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
    getParagraphsForPage,
  } = useFrenchReaderContext();

  const bubbles = getBubblesForPage(pageNumber);
  const paragraphs = getParagraphsForPage(pageNumber);

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

  const runRegionOcr = async (bbox: NormalizedBBox) => {
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
      <RegionSelector pageIndex={pageIndex} onComplete={runRegionOcr} />
      <ParagraphOverlay
        paragraphs={paragraphs}
        activeBbox={selection?.page === pageNumber ? selection.bbox : null}
        disabled={ocrLoading}
        onParagraphClick={runRegionOcr}
      />
      <BubbleOverlay
        bubbles={bubbles}
        activeBbox={selection?.page === pageNumber ? selection.bbox : null}
        disabled={ocrLoading}
        onBubbleClick={runRegionOcr}
      />
    </>,
    mountNode,
  );
}
