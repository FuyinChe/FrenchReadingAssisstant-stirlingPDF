import { useCallback, useEffect, useState } from "react";
import { useViewer } from "@app/contexts/ViewerContext";

export interface FrenchReaderPageState {
  currentPage: number;
  totalPages: number;
  zoomPercent: number;
  scrollToPage: (page: number) => void;
  scrollToPreviousPage: () => void;
  scrollToNextPage: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
}

export function useFrenchReaderPageState(): FrenchReaderPageState {
  const viewer = useViewer();
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [zoomPercent, setZoomPercent] = useState(100);

  useEffect(() => {
    if (!viewer) return;

    const syncFromViewer = () => {
      const scroll = viewer.getScrollState();
      setCurrentPage(scroll.currentPage);
      setTotalPages(scroll.totalPages);
      const zoom = viewer.getZoomState();
      setZoomPercent(Math.round(zoom.zoomPercent));
    };

    syncFromViewer();

    const unsubScroll = viewer.registerImmediateScrollUpdate(
      (page, total) => {
        setCurrentPage(page);
        setTotalPages(total);
      },
    );
    const unsubZoom = viewer.registerImmediateZoomUpdate((percent) => {
      setZoomPercent(Math.round(percent));
    });

    return () => {
      unsubScroll();
      unsubZoom();
    };
  }, [viewer]);

  const scrollToPage = useCallback(
    (page: number) => {
      viewer?.scrollActions.scrollToPage(page, "smooth");
    },
    [viewer],
  );

  const scrollToPreviousPage = useCallback(() => {
    viewer?.scrollActions.scrollToPreviousPage();
  }, [viewer]);

  const scrollToNextPage = useCallback(() => {
    viewer?.scrollActions.scrollToNextPage();
  }, [viewer]);

  const zoomIn = useCallback(() => {
    viewer?.zoomActions.zoomIn();
  }, [viewer]);

  const zoomOut = useCallback(() => {
    viewer?.zoomActions.zoomOut();
  }, [viewer]);

  return {
    currentPage,
    totalPages,
    zoomPercent,
    scrollToPage,
    scrollToPreviousPage,
    scrollToNextPage,
    zoomIn,
    zoomOut,
  };
}
