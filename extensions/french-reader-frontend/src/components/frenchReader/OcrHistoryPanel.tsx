import {
  Alert,
  Button,
  CopyButton,
  Group,
  Menu,
  Paper,
  ScrollArea,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import DeleteOutlineOutlinedIcon from "@mui/icons-material/DeleteOutlineOutlined";
import DownloadIcon from "@mui/icons-material/Download";
import HistoryIcon from "@mui/icons-material/History";

import { OcrTextBlock } from "@app/components/frenchReader/OcrTextBlock";
import { TranslationLine } from "@app/components/frenchReader/TranslationLine";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";

import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";
import type { OcrHistoryEntry } from "@app/hooks/tools/frenchReader/historyTypes";

interface OcrHistoryPanelProps {
  sourceFileName: string;
}

const MODE_ORDER: AiExplainMode[] = ["translate", "vocabulary", "grammar"];

function historyTranslations(entry: OcrHistoryEntry) {
  if (entry.translations && Object.keys(entry.translations).length > 0) {
    return entry.translations;
  }
  if (entry.translation) {
    return { [entry.translationMode ?? "translate"]: entry.translation };
  }
  return {};
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function OcrHistoryPanel({ sourceFileName }: OcrHistoryPanelProps) {
  const { t } = useTranslation();
  const {
    history,
    currentEntryId,
    restoreHistoryEntry,
    clearHistory,
    exportHistory,
    exportError,
  } = useFrenchReaderContext();

  if (history.length === 0) {
    return (
      <Paper withBorder p="sm" radius="md">
        <Group gap="xs" mb="xs">
          <HistoryIcon sx={{ fontSize: 18, opacity: 0.6 }} />
          <Text size="sm" fw={500}>
            {t("frenchReader.history.title", "Recognition history")}
          </Text>
        </Group>
        <Text size="sm" c="dimmed">
          {t("frenchReader.history.empty", "Previous selections will appear here.")}
        </Text>
      </Paper>
    );
  }

  return (
    <Paper withBorder p="sm" radius="md">
      <Group justify="space-between" mb="xs" wrap="nowrap">
        <Group gap="xs">
          <HistoryIcon sx={{ fontSize: 18, opacity: 0.6 }} />
          <Text size="sm" fw={500}>
            {t("frenchReader.history.title", "Recognition history")}
          </Text>
          <Text size="xs" c="dimmed">
            ({history.length})
          </Text>
        </Group>
        <Group gap={4} wrap="nowrap">
          <Menu shadow="md" width={180}>
            <Menu.Target>
              <Button
                size="compact-xs"
                variant="light"
                leftSection={<DownloadIcon sx={{ fontSize: 14 }} />}
              >
                {t("frenchReader.history.export", "Export")}
              </Button>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Item onClick={() => exportHistory("txt", sourceFileName)}>
                {t("frenchReader.history.exportTxt", "Export as .txt")}
              </Menu.Item>
              <Menu.Item onClick={() => exportHistory("md", sourceFileName)}>
                {t("frenchReader.history.exportMd", "Export as .md")}
              </Menu.Item>
              <Menu.Item onClick={() => exportHistory("pdf", sourceFileName)}>
                {t("frenchReader.history.exportPdf", "Export as .pdf")}
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
          <Tooltip label={t("frenchReader.history.clear", "Clear history")}>
            <Button
              size="compact-xs"
              variant="subtle"
              color="red"
              onClick={clearHistory}
            >
              <DeleteOutlineOutlinedIcon sx={{ fontSize: 16 }} />
            </Button>
          </Tooltip>
        </Group>
      </Group>

      {exportError && (
        <Alert color="red" variant="light" mb="xs" title={t("frenchReader.history.exportError", "Export failed")}>
          {exportError}
        </Alert>
      )}

      <ScrollArea.Autosize mah={280} type="scroll">
        <Stack gap="xs">
          {history.map((entry) => {
            const active = entry.id === currentEntryId;
            return (
              <Paper
                key={entry.id}
                withBorder
                p="xs"
                radius="sm"
                onClick={() => restoreHistoryEntry(entry.id)}
                style={{
                  cursor: "pointer",
                  borderColor: active
                    ? "var(--mantine-color-blue-4)"
                    : undefined,
                  background: active
                    ? "var(--mantine-color-blue-0)"
                    : "var(--bg-muted, var(--mantine-color-gray-0))",
                }}
              >
                <Group justify="space-between" mb={4} wrap="nowrap">
                  <Text size="xs" c="dimmed" lineClamp={1}>
                    {t("frenchReader.history.meta", "Page {{page}} · {{time}}", {
                      page: entry.page,
                      time: formatTime(entry.createdAt),
                    })}
                  </Text>
                </Group>
                <OcrTextBlock
                  text={entry.text}
                  lines={entry.lines}
                  compact
                />
                {MODE_ORDER.map((mode) => {
                  const note = historyTranslations(entry)[mode];
                  if (!note) return null;
                  return (
                    <TranslationLine
                      key={mode}
                      text={note}
                      mode={mode}
                    />
                  );
                })}
              </Paper>
            );
          })}
        </Stack>
      </ScrollArea.Autosize>
    </Paper>
  );
}
