import { Divider, Paper, Stack, Text, Title } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { isStirlingFile } from "@app/types/fileContext";
import type { StirlingFile } from "@app/types/fileContext";
import { FrenchReaderViewerControls } from "@app/components/frenchReader/FrenchReaderViewerControls";
import type { FrenchReaderPageState } from "@app/hooks/tools/frenchReader/useFrenchReaderPageState";

interface AiSidePanelProps {
  activeFile: StirlingFile | null;
  pageState: FrenchReaderPageState;
}

export function AiSidePanel({ activeFile, pageState }: AiSidePanelProps) {
  const { t } = useTranslation();

  const fileLabel =
    activeFile && isStirlingFile(activeFile)
      ? activeFile.name
      : t("frenchReader.panel.noFile", "No PDF loaded");

  return (
    <Stack gap="md">
      <Stack gap={4}>
        <Title order={5}>{t("frenchReader.panel.title", "Reading assistant")}</Title>
        <Text size="sm" c="dimmed" lineClamp={2}>
          {fileLabel}
        </Text>
      </Stack>

      <FrenchReaderViewerControls pageState={pageState} />

      <Divider />

      <Paper withBorder p="sm" radius="md" bg="var(--bg-muted, var(--mantine-color-gray-0))">
        <Stack gap="xs">
          <Text size="sm" fw={500}>
            {t("frenchReader.panel.ocrPlaceholder", "Extracted text")}
          </Text>
          <Text size="sm" c="dimmed">
            {t(
              "frenchReader.panel.ocrHint",
              "Drag a rectangle on the PDF in the viewer to OCR French text (coming in M2).",
            )}
          </Text>
        </Stack>
      </Paper>

      <Paper withBorder p="sm" radius="md">
        <Stack gap="xs">
          <Text size="sm" fw={500}>
            {t("frenchReader.panel.ttsPlaceholder", "Pronunciation")}
          </Text>
          <Text size="sm" c="dimmed">
            {t(
              "frenchReader.panel.ttsHint",
              "TTS playback will appear here after OCR (M3).",
            )}
          </Text>
        </Stack>
      </Paper>
    </Stack>
  );
}
