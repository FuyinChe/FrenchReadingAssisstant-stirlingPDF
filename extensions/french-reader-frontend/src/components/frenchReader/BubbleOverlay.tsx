import { Box, Tooltip } from "@mantine/core";

import type { DetectedBubble, NormalizedBBox } from "@app/hooks/tools/frenchReader/types";

interface BubbleOverlayProps {
  bubbles: DetectedBubble[];
  activeBbox: NormalizedBBox | null;
  disabled?: boolean;
  onBubbleClick: (bbox: NormalizedBBox) => void;
}

function bboxKey(bbox: NormalizedBBox): string {
  return `${bbox.x.toFixed(4)}:${bbox.y.toFixed(4)}:${bbox.w.toFixed(4)}:${bbox.h.toFixed(4)}`;
}

function bboxMatches(a: NormalizedBBox, b: NormalizedBBox): boolean {
  return bboxKey(a) === bboxKey(b);
}

export function BubbleOverlay({
  bubbles,
  activeBbox,
  disabled = false,
  onBubbleClick,
}: BubbleOverlayProps) {
  if (bubbles.length === 0) {
    return null;
  }

  return (
    <Box
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 45,
        pointerEvents: "none",
      }}
    >
      {bubbles.map((bubble, index) => {
        const active = activeBbox ? bboxMatches(activeBbox, bubble.bbox) : false;
        return (
          <Tooltip
            key={`${index}-${bboxKey(bubble.bbox)}`}
            label={`${Math.round(bubble.confidence * 100)}% · ${bubble.detector}`}
            withArrow
            position="top"
          >
            <Box
              component="button"
              type="button"
              disabled={disabled}
              onClick={(event) => {
                event.stopPropagation();
                if (!disabled) {
                  onBubbleClick(bubble.bbox);
                }
              }}
              style={{
                position: "absolute",
                left: `${bubble.bbox.x * 100}%`,
                top: `${bubble.bbox.y * 100}%`,
                width: `${bubble.bbox.w * 100}%`,
                height: `${bubble.bbox.h * 100}%`,
                margin: 0,
                padding: 0,
                border: active
                  ? "2px solid var(--mantine-color-orange-6)"
                  : "2px dashed var(--mantine-color-violet-6)",
                backgroundColor: active
                  ? "rgba(253, 126, 20, 0.18)"
                  : "rgba(132, 94, 247, 0.12)",
                borderRadius: 12,
                cursor: disabled ? "not-allowed" : "pointer",
                pointerEvents: disabled ? "none" : "auto",
                opacity: disabled ? 0.55 : 1,
              }}
              aria-label={`Speech bubble ${index + 1}`}
            />
          </Tooltip>
        );
      })}
    </Box>
  );
}
