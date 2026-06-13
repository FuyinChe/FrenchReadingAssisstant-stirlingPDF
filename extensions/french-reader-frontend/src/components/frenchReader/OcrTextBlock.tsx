import { Box, Group, Text } from "@mantine/core";
import { useTranslation } from "react-i18next";

import { TtsPlayButton } from "@app/components/frenchReader/TtsPlayButton";
import type { OcrLineResult } from "@app/hooks/tools/frenchReader/types";

interface OcrTextBlockProps {
  text: string;
  lines: OcrLineResult[];
  confidence?: number;
  compact?: boolean;
}

export function OcrTextBlock({ text, lines, confidence, compact }: OcrTextBlockProps) {
  const { t } = useTranslation();

  return (
    <Group align="flex-start" gap="xs" wrap="nowrap">
      <TtsPlayButton text={text} lines={lines} size={compact ? "sm" : "md"} />
      <Box style={{ flex: 1, minWidth: 0 }}>
        {confidence !== undefined && !compact && (
          <Text size="xs" c="dimmed" mb={4}>
            {t("frenchReader.panel.confidence", "Confidence")}:{" "}
            {(confidence * 100).toFixed(1)}%
          </Text>
        )}
        <Text
          size={compact ? "xs" : "sm"}
          style={{
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            fontFamily: "var(--mantine-font-family-monospace)",
            lineHeight: 1.55,
          }}
        >
          {text}
        </Text>
      </Box>
    </Group>
  );
}
