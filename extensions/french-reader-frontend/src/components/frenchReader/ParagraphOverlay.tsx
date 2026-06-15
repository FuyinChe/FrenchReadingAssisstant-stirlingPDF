import { Box, Text, Tooltip } from "@mantine/core";

import type { DetectedParagraph, NormalizedBBox } from "@app/hooks/tools/frenchReader/types";

interface ParagraphOverlayProps {
  paragraphs: DetectedParagraph[];
  activeBbox: NormalizedBBox | null;
  disabled?: boolean;
  onParagraphClick: (bbox: NormalizedBBox) => void;
}

function bboxKey(bbox: NormalizedBBox): string {
  return `${bbox.x.toFixed(4)}:${bbox.y.toFixed(4)}:${bbox.w.toFixed(4)}:${bbox.h.toFixed(4)}`;
}

function bboxMatches(a: NormalizedBBox, b: NormalizedBBox): boolean {
  return bboxKey(a) === bboxKey(b);
}

export function ParagraphOverlay({
  paragraphs,
  activeBbox,
  disabled = false,
  onParagraphClick,
}: ParagraphOverlayProps) {
  if (paragraphs.length === 0) {
    return null;
  }

  return (
    <Box
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 44,
        pointerEvents: "none",
      }}
    >
      {paragraphs.map((paragraph) => {
        const active = activeBbox ? bboxMatches(activeBbox, paragraph.bbox) : false;
        const label = paragraph.order;
        return (
          <Tooltip
            key={`${label}-${bboxKey(paragraph.bbox)}`}
            label={`P${label} · ${Math.round(paragraph.confidence * 100)}% · ${paragraph.detector}`}
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
                  onParagraphClick(paragraph.bbox);
                }
              }}
              style={{
                position: "absolute",
                left: `${paragraph.bbox.x * 100}%`,
                top: `${paragraph.bbox.y * 100}%`,
                width: `${paragraph.bbox.w * 100}%`,
                height: `${paragraph.bbox.h * 100}%`,
                margin: 0,
                padding: 0,
                border: active
                  ? "2px solid var(--mantine-color-orange-6)"
                  : "2px dashed var(--mantine-color-teal-6)",
                backgroundColor: active
                  ? "rgba(253, 126, 20, 0.16)"
                  : "rgba(18, 184, 134, 0.1)",
                borderRadius: 6,
                cursor: disabled ? "not-allowed" : "pointer",
                pointerEvents: disabled ? "none" : "auto",
                opacity: disabled ? 0.55 : 1,
              }}
              aria-label={`Paragraph ${label}`}
            >
              <Text
                component="span"
                size="xs"
                fw={700}
                c={active ? "orange.7" : "teal.7"}
                style={{
                  position: "absolute",
                  top: 4,
                  left: 6,
                  lineHeight: 1,
                  pointerEvents: "none",
                  textShadow: "0 0 4px rgba(255,255,255,0.9)",
                }}
              >
                {label}
              </Text>
            </Box>
          </Tooltip>
        );
      })}
    </Box>
  );
}
