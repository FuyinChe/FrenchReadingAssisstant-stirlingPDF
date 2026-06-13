import {
  Alert,
  Divider,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import { isStirlingFile } from "@app/types/fileContext";
import type { StirlingFile } from "@app/types/fileContext";
import { AiTranslationControls } from "@app/components/frenchReader/AiTranslationControls";
import { CopyHoverPanel } from "@app/components/frenchReader/CopyHoverPanel";
import { OcrHistoryPanel } from "@app/components/frenchReader/OcrHistoryPanel";
import { OcrTextBlock } from "@app/components/frenchReader/OcrTextBlock";
import { FrenchReaderSettingsButton } from "@app/components/frenchReader/FrenchReaderSettingsButton";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";

interface AiSidePanelProps {
  activeFile: StirlingFile | null;
}

export function AiSidePanel({ activeFile }: AiSidePanelProps) {
  const { t } = useTranslation();
  const { ocrResult, ocrLoading, ocrError, clearOcr, ttsError } =
    useFrenchReaderContext();

  const fileLabel =
    activeFile && isStirlingFile(activeFile)
      ? activeFile.name
      : t("frenchReader.panel.noFile", "No PDF loaded");

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center" wrap="nowrap">
        <Text size="xs" c="dimmed" style={{ flex: 1 }}>
          {t(
            "frenchReader.panel.selectHint",
            "Drag a rectangle on the current PDF page to extract French text.",
          )}
        </Text>
        <FrenchReaderSettingsButton />
      </Group>

      <Divider />

      <Paper withBorder p="sm" radius="md" bg="var(--bg-muted, var(--mantine-color-gray-0))">
        <Stack gap="sm">
          {ocrLoading && (
            <Stack gap="xs" align="center" py="sm">
              <Loader size="sm" />
              <Text size="sm" c="dimmed">
                {t("frenchReader.panel.ocrLoading", "Recognizing French…")}
              </Text>
            </Stack>
          )}

          {ocrError && !ocrLoading && (
            <Alert color="red" variant="light" title={t("frenchReader.panel.ocrError", "OCR failed")}>
              {ocrError}
            </Alert>
          )}

          {!ocrLoading && !ocrError && ocrResult && (
            <>
              <CopyHoverPanel
                copyValue={ocrResult.text}
                copyTooltip={t("frenchReader.panel.copyFrench", "Copy French")}
                copiedTooltip={t("frenchReader.panel.copied", "Copied")}
                onClear={clearOcr}
                clearTooltip={t("frenchReader.panel.clear", "Clear selection")}
              >
                <OcrTextBlock
                  text={ocrResult.text}
                  lines={ocrResult.lines}
                  confidence={ocrResult.confidence}
                />
              </CopyHoverPanel>
              <AiTranslationControls text={ocrResult.text} />
            </>
          )}

          {!ocrLoading && !ocrError && !ocrResult && (
            <Text size="sm" c="dimmed">
              {t(
                "frenchReader.panel.ocrEmpty",
                "No text yet. Select a region on the page.",
              )}
            </Text>
          )}

          {ttsError && (
            <Alert color="red" variant="light" title={t("frenchReader.tts.error", "TTS failed")}>
              {ttsError}
            </Alert>
          )}
        </Stack>
      </Paper>

      <OcrHistoryPanel sourceFileName={fileLabel} />
    </Stack>
  );
}
