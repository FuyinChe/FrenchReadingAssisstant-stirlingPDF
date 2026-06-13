import { useCallback, useEffect, useRef, useState } from "react";
import { Box } from "@mantine/core";

import type { NormalizedBBox } from "@app/hooks/tools/frenchReader/types";

interface RegionSelectorProps {
  pageIndex: number;
  onComplete: (bbox: NormalizedBBox) => void;
}

interface DragState {
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
}

function normalizeRect(
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  width: number,
  height: number,
): NormalizedBBox | null {
  const x1 = Math.max(0, Math.min(startX, endX));
  const y1 = Math.max(0, Math.min(startY, endY));
  const x2 = Math.min(width, Math.max(startX, endX));
  const y2 = Math.min(height, Math.max(startY, endY));
  const w = x2 - x1;
  const h = y2 - y1;
  if (w < 12 || h < 12) {
    return null;
  }
  return {
    x: x1 / width,
    y: y1 / height,
    w: w / width,
    h: h / height,
  };
}

export function RegionSelector({ pageIndex, onComplete }: RegionSelectorProps) {
  const [drag, setDrag] = useState<DragState | null>(null);
  const pageRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    pageRef.current = document.querySelector(
      `[data-page-index="${pageIndex}"]`,
    ) as HTMLElement | null;
  }, [pageIndex]);

  const toLocal = useCallback((clientX: number, clientY: number) => {
    const page = pageRef.current;
    if (!page) return null;
    const rect = page.getBoundingClientRect();
    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
      width: rect.width,
      height: rect.height,
    };
  }, []);

  const handlePointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    const local = toLocal(event.clientX, event.clientY);
    if (!local) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrag({
      startX: local.x,
      startY: local.y,
      currentX: local.x,
      currentY: local.y,
    });
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drag) return;
    const local = toLocal(event.clientX, event.clientY);
    if (!local) return;
    setDrag((prev) =>
      prev
        ? {
            ...prev,
            currentX: local.x,
            currentY: local.y,
          }
        : prev,
    );
  };

  const handlePointerUp = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drag) return;
    const local = toLocal(event.clientX, event.clientY);
    if (!local) {
      setDrag(null);
      return;
    }
    const bbox = normalizeRect(
      drag.startX,
      drag.startY,
      local.x,
      local.y,
      local.width,
      local.height,
    );
    setDrag(null);
    if (bbox) {
      onComplete(bbox);
    }
  };

  const selectionStyle = (() => {
    if (!drag || !pageRef.current) return null;
    const width = pageRef.current.getBoundingClientRect().width;
    const height = pageRef.current.getBoundingClientRect().height;
    const bbox = normalizeRect(
      drag.startX,
      drag.startY,
      drag.currentX,
      drag.currentY,
      width,
      height,
    );
    if (!bbox) return null;
    return {
      left: `${bbox.x * 100}%`,
      top: `${bbox.y * 100}%`,
      width: `${bbox.w * 100}%`,
      height: `${bbox.h * 100}%`,
    };
  })();

  return (
    <Box
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={() => setDrag(null)}
      style={{
        position: "absolute",
        inset: 0,
        cursor: "crosshair",
        zIndex: 40,
        touchAction: "none",
      }}
    >
      {selectionStyle && (
        <Box
          style={{
            position: "absolute",
            ...selectionStyle,
            border: "2px solid var(--mantine-color-blue-6)",
            backgroundColor: "rgba(37, 99, 235, 0.15)",
            pointerEvents: "none",
          }}
        />
      )}
    </Box>
  );
}
