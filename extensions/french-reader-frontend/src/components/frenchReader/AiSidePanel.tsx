import {
  Alert,
  Button,
  Checkbox,
  Divider,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import ClearIcon from "@mui/icons-material/Clear";
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
  currentPage: number;
}

export function AiSidePanel({ activeFile, currentPage }: AiSidePanelProps) {
  const { t } = useTranslation();
  const {
    ocrResult,
    ocrLoading,
    ocrError,
    clearOcr,
    ttsError,
    detectBubblesForPage,
    clearBubblesForPage,
    bubbleDetectLoading,
    bubbleDetectError,
    bubblePreprocess,
    setBubblePreprocess,
    bubbleDetectorReady,
    lastBubbleDetector,
    getBubblesForPage,
    detectParagraphsForPage,
    clearParagraphsForPage,
    paragraphDetectLoading,
    paragraphDetectError,
    setParagraphPreprocess,
    paragraphDetectorReady,
    lastParagraphDetector,
    getParagraphsForPage,
  } = useFrenchReaderContext();

  const fileLabel =
    activeFile && isStirlingFile(activeFile)
      ? activeFile.name
      : t("frenchReader.panel.noFile", "No PDF loaded");

  const pageBubbles = getBubblesForPage(currentPage);
  const pageParagraphs = getParagraphsForPage(currentPage);

  const handleDetectBubbles = async () => {
    if (!activeFile) return;
    await detectBubblesForPage({
      file: activeFile,
      pageNumber: currentPage,
    });
  };

  const handleDetectParagraphs = async () => {
    if (!activeFile) return;
    await detectParagraphsForPage({
      file: activeFile,
      pageNumber: currentPage,
    });
  };

  const detectPreprocess = bubblePreprocess;
  const setDetectPreprocess = (enabled: boolean) => {
    setBubblePreprocess(enabled);
    setParagraphPreprocess(enabled);
  };
  const detectOpenCvReady =
    bubbleDetectorReady !== false && paragraphDetectorReady !== false;

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center" wrap="nowrap">
        <Text size="xs" c="dimmed" style={{ flex: 1 }}>
          {t(
            "frenchReader.panel.selectHint",
            "Drag a rectangle, run Bubble or Paragraph Detect, or click a highlighted region to OCR.",
          )}
        </Text>
        <FrenchReaderSettingsButton />
      </Group>

      <Paper withBorder p="sm" radius="md">
        <Stack gap="sm">
          <Text size="sm" fw={500}>
            {t("frenchReader.detect.title", "AUTO DETECTORS")}
          </Text>

          <Text size="sm" fs="italic" c="red">
            {t(
              "frenchReader.detect.manualBest",
              "*Manual rectangle selection is the most accurate way to pick text.",
            )}
          </Text>

          <Group gap="xs" wrap="nowrap">
            <Tooltip
              label={t(
                "frenchReader.bubbles.tooltip",
                "For comics and picture books — finds speech bubbles.",
              )}
              withArrow
              multiline
              w={260}
            >
              <span style={{ display: "inline-flex", flex: 1 }}>
                <Button
                  size="compact-sm"
                  variant="light"
                  color="violet"
                  fullWidth
                  leftSection={<AutoFixHighIcon sx={{ fontSize: 16 }} />}
                  loading={bubbleDetectLoading}
                  disabled={!activeFile || bubbleDetectorReady === false}
                  onClick={() => void handleDetectBubbles()}
                >
                  {t("frenchReader.bubbles.detect", "BUBBLES")}
                </Button>
              </span>
            </Tooltip>

            <Tooltip
              label={t(
                "frenchReader.paragraphs.tooltip",
                "For prose and picture-book text — finds whole paragraph blocks.",
              )}
              withArrow
              multiline
              w={260}
            >
              <span style={{ display: "inline-flex", flex: 1 }}>
                <Button
                  size="compact-sm"
                  variant="light"
                  color="teal"
                  fullWidth
                  leftSection={<AutoFixHighIcon sx={{ fontSize: 16 }} />}
                  loading={paragraphDetectLoading}
                  disabled={!activeFile || paragraphDetectorReady === false}
                  onClick={() => void handleDetectParagraphs()}
                >
                  {t("frenchReader.paragraphs.detect", "PARAGRAPHS")}
                </Button>
              </span>
            </Tooltip>
          </Group>

          {(pageBubbles.length > 0 || pageParagraphs.length > 0) && (
            <Group gap="xs">
              {pageBubbles.length > 0 && (
                <Button
                  variant="subtle"
                  size="compact-xs"
                  color="gray"
                  leftSection={<ClearIcon sx={{ fontSize: 14 }} />}
                  onClick={() => clearBubblesForPage(currentPage)}
                >
                  {t("frenchReader.bubbles.clear", "Clear bubbles")}
                </Button>
              )}
              {pageParagraphs.length > 0 && (
                <Button
                  variant="subtle"
                  size="compact-xs"
                  color="gray"
                  leftSection={<ClearIcon sx={{ fontSize: 14 }} />}
                  onClick={() => clearParagraphsForPage(currentPage)}
                >
                  {t("frenchReader.paragraphs.clear", "Clear paragraphs")}
                </Button>
              )}
            </Group>
          )}

          <Checkbox
            size="xs"
            label={t(
              "frenchReader.detect.preprocess",
              "Enhance page contrast before detection (OpenCV)",
            )}
            checked={detectPreprocess}
            onChange={(event) => setDetectPreprocess(event.currentTarget.checked)}
          />

          {!detectOpenCvReady && (
            <Alert color="yellow" variant="light">
              {t(
                "frenchReader.detect.notReady",
                "Auto detection needs OpenCV. Run: cd extensions/french-reader-engine && uv sync --extra bubble",
              )}
            </Alert>
          )}

          {bubbleDetectError && (
            <Alert color="red" variant="light" title={t("frenchReader.bubbles.error", "Detection failed")}>
              {bubbleDetectError}
            </Alert>
          )}

          {paragraphDetectError && (
            <Alert
              color="red"
              variant="light"
              title={t("frenchReader.paragraphs.error", "Detection failed")}
            >
              {paragraphDetectError}
            </Alert>
          )}

          {!bubbleDetectLoading && pageBubbles.length > 0 && (
            <Text size="xs" c="dimmed">
              {t("frenchReader.bubbles.found", "{{count}} bubble(s) on page {{page}} · {{detector}}", {
                count: pageBubbles.length,
                page: currentPage,
                detector: lastBubbleDetector ?? pageBubbles[0]?.detector ?? "opencv",
              })}
            </Text>
          )}

          {!paragraphDetectLoading && pageParagraphs.length > 0 && (
            <Text size="xs" c="dimmed">
              {t(
                "frenchReader.paragraphs.found",
                "{{count}} paragraph(s) on page {{page}} · {{detector}}",
                {
                  count: pageParagraphs.length,
                  page: currentPage,
                  detector: lastParagraphDetector ?? pageParagraphs[0]?.detector ?? "opencv-paragraph",
                },
              )}
            </Text>
          )}
        </Stack>
      </Paper>

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
                "No text yet. Select a region or click a detected bubble or paragraph.",
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
