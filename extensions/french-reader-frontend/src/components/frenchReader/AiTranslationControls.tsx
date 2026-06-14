import {
  Alert,
  Button,
  Group,
  Loader,
  Stack,
  Text,
} from "@mantine/core";
import { useTranslation } from "react-i18next";
import StopIcon from "@mui/icons-material/Stop";
import TranslateIcon from "@mui/icons-material/Translate";

import { TranslationLine } from "@app/components/frenchReader/TranslationLine";
import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import { useAiExplain } from "@app/hooks/tools/frenchReader/useAiExplain";
import type { AiExplainMode } from "@app/hooks/tools/frenchReader/types";

interface AiTranslationControlsProps {
  text: string;
}

const MODE_ORDER: AiExplainMode[] = ["translate", "vocabulary", "grammar"];

export function AiTranslationControls({ text }: AiTranslationControlsProps) {
  const { t } = useTranslation();
  const {
    currentTranslations,
    setTranslationForMode,
    aiModes,
    aiTargetLang,
    llmSettings,
  } = useFrenchReaderContext();

  const {
    aiReady,
    aiDetail,
    results,
    activeMode,
    streaming,
    error,
    run,
    stop,
    canRun,
    loading,
  } = useAiExplain({
    text,
    modes: aiModes,
    targetLang: aiTargetLang,
    llmSettings,
    onComplete: setTranslationForMode,
  });

  const busy = loading || streaming;

  const mergedResults: Partial<Record<AiExplainMode, string>> = {
    ...currentTranslations,
    ...results,
  };

  const visibleModes = MODE_ORDER.filter(
    (mode) => aiModes.includes(mode) && (mergedResults[mode] || (streaming && activeMode === mode)),
  );

  if (aiReady === null) {
    return (
      <Group gap="xs">
        <Loader size="xs" />
        <Text size="sm" c="dimmed">
          {t("frenchReader.ai.checking", "Checking AI configuration…")}
        </Text>
      </Group>
    );
  }

  if (!aiReady) {
    return (
      <Alert color="yellow" variant="light" title={t("frenchReader.ai.unavailable", "AI unavailable")}>
        {t(
          "frenchReader.ai.unavailableHint",
          "Set FRENCH_READER_LLM_API_KEY in .env on the engine, or choose a provider and paste your API key in Settings (gear icon).",
        )}
        {aiDetail ? ` (${aiDetail})` : ""}
      </Alert>
    );
  }

  return (
    <Stack gap="xs">
      <Group gap="xs" wrap="nowrap" align="center">
        <Button
          size="compact-xs"
          variant="light"
          leftSection={<TranslateIcon sx={{ fontSize: 16 }} />}
          onClick={() => void run()}
          disabled={!canRun || busy}
          loading={loading && visibleModes.length === 0}
          style={{ flexShrink: 0 }}
        >
          {t("frenchReader.ai.run", "Explain")}
        </Button>
        <Button
          size="compact-xs"
          variant="subtle"
          color="red"
          leftSection={<StopIcon sx={{ fontSize: 16 }} />}
          onClick={stop}
          disabled={!busy}
          style={{ flexShrink: 0 }}
        >
          {t("frenchReader.ai.stop", "Stop")}
        </Button>
      </Group>

      {visibleModes.map((mode) => (
        <TranslationLine
          key={mode}
          text={mergedResults[mode] ?? ""}
          mode={mode}
          streaming={streaming && activeMode === mode}
        />
      ))}

      {error && (
        <Alert color="red" variant="light" title={t("frenchReader.ai.error", "AI failed")}>
          {error}
        </Alert>
      )}
    </Stack>
  );
}
