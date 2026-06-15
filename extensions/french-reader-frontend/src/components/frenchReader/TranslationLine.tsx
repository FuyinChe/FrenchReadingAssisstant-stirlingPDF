import { Box, Group, Loader, Text } from "@mantine/core";
import { useTranslation } from "react-i18next";

import { AiMarkdownContent } from "@app/components/frenchReader/AiMarkdownContent";
import { CopyHoverPanel } from "@app/components/frenchReader/CopyHoverPanel";
import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";
import { stripMarkdownForCopy } from "@app/utils/stripMarkdownForCopy";

interface TranslationLineProps {
  text: string;
  mode?: AiExplainMode | null;
  streaming?: boolean;
}

const MODE_LABEL: Record<AiExplainMode, { key: string; fallback: string }> = {
  translate: { key: "frenchReader.ai.modeTranslate", fallback: "Translation" },
  vocabulary: { key: "frenchReader.ai.modeVocabulary", fallback: "Vocabulary" },
  grammar: { key: "frenchReader.ai.modeGrammar", fallback: "Grammar" },
};

export function TranslationLine({ text, mode, streaming }: TranslationLineProps) {
  const { t } = useTranslation();

  if (!text && !streaming) {
    return null;
  }

  const label = mode
    ? t(MODE_LABEL[mode].key, MODE_LABEL[mode].fallback)
    : t("frenchReader.ai.notes", "Notes");

  return (
    <Box
      mt="xs"
      p="sm"
      style={{
        borderLeft: "3px solid var(--mantine-color-teal-5)",
        background: "var(--mantine-color-teal-0)",
        borderRadius: "var(--mantine-radius-sm)",
      }}
    >
      <CopyHoverPanel
        copyValue={stripMarkdownForCopy(text)}
        copyTooltip={t("frenchReader.panel.copy", "Copy")}
        copiedTooltip={t("frenchReader.panel.copied", "Copied")}
      >
        <Group gap="xs" mb={4} wrap="nowrap">
          <Text size="xs" fw={600} c="teal.8">
            {label}
          </Text>
          {streaming && <Loader size="xs" color="teal" />}
        </Group>
        {text ? (
          <AiMarkdownContent text={text} />
        ) : streaming ? (
          <Text size="sm" c="teal.9">
            …
          </Text>
        ) : null}
      </CopyHoverPanel>
    </Box>
  );
}
