import {
  Alert,
  Button,
  CopyButton,
  Divider,
  Loader,
  Paper,
  Stack,
  Text,
  Textarea,
  Title,
  Tooltip,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { isStirlingFile } from "@app/types/fileContext";
import type { StirlingFile } from "@app/types/fileContext";
import { FrenchReaderViewerControls } from "@app/components/frenchReader/FrenchReaderViewerControls";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import type { FrenchReaderPageState } from "@app/hooks/tools/frenchReader/useFrenchReaderPageState";

interface AiSidePanelProps {
  activeFile: StirlingFile | null;
  pageState: FrenchReaderPageState;
}

export function AiSidePanel({ activeFile, pageState }: AiSidePanelProps) {
  const { t } = useTranslation();
  const { ocrResult, ocrLoading, ocrError, clearOcr } = useFrenchReaderContext();

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

      <Text size="xs" c="dimmed">
        {t(
          "frenchReader.panel.selectHint",
          "Drag a rectangle on the current PDF page to extract French text.",
        )}
      </Text>

      <Divider />

      <Paper withBorder p="sm" radius="md" bg="var(--bg-muted, var(--mantine-color-gray-0))">
        <Stack gap="xs">
          <Text size="sm" fw={500}>
            {t("frenchReader.panel.ocrTitle", "Extracted text")}
          </Text>

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
              <Text size="xs" c="dimmed">
                {t("frenchReader.panel.confidence", "Confidence")}:{" "}
                {(ocrResult.confidence * 100).toFixed(1)}%
              </Text>
              <Textarea
                value={ocrResult.text}
                readOnly
                autosize
                minRows={3}
                maxRows={10}
              />
              <GroupActions text={ocrResult.text} onClear={clearOcr} t={t} />
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

function GroupActions({
  text,
  onClear,
  t,
}: {
  text: string;
  onClear: () => void;
  t: (key: string, defaultValue: string) => string;
}) {
  return (
    <Stack gap="xs">
      <CopyButton value={text}>
        {({ copied, copy }) => (
          <Tooltip label={copied ? t("frenchReader.panel.copied", "Copied") : t("frenchReader.panel.copy", "Copy")}>
            <Button
              variant="light"
              size="xs"
              leftSection={<ContentCopyIcon sx={{ fontSize: 16 }} />}
              onClick={copy}
            >
              {copied
                ? t("frenchReader.panel.copied", "Copied")
                : t("frenchReader.panel.copy", "Copy text")}
            </Button>
          </Tooltip>
        )}
      </CopyButton>
      <Button variant="subtle" size="xs" onClick={onClear}>
        {t("frenchReader.panel.clear", "Clear selection")}
      </Button>
    </Stack>
  );
}
