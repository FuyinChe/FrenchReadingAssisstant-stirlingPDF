import {
  ActionIcon,
  Button,
  Divider,
  Group,
  Loader,
  Modal,
  MultiSelect,
  PasswordInput,
  Select,
  Stack,
  Text,
  Title,
  Tooltip,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import SettingsIcon from "@mui/icons-material/Settings";

import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import type { AiExplainMode, TtsRate } from "@app/hooks/tools/frenchReader/types";
import { maskUserLlmApiKey } from "@app/services/frenchReaderUserApiKey";

const RATE_OPTIONS: { value: TtsRate; labelKey: string; fallback: string }[] = [
  { value: "-15%", labelKey: "frenchReader.tts.rateSlow", fallback: "Slow" },
  { value: "+0%", labelKey: "frenchReader.tts.rateNormal", fallback: "Normal" },
  { value: "+15%", labelKey: "frenchReader.tts.rateFast", fallback: "Fast" },
];

const MODE_OPTIONS: { value: AiExplainMode; labelKey: string; fallback: string }[] = [
  { value: "translate", labelKey: "frenchReader.ai.modeTranslate", fallback: "Translate" },
  { value: "vocabulary", labelKey: "frenchReader.ai.modeVocabulary", fallback: "Vocabulary" },
  { value: "grammar", labelKey: "frenchReader.ai.modeGrammar", fallback: "Grammar" },
];

const TARGET_OPTIONS = [
  { value: "zh", label: "中文" },
  { value: "en", label: "English" },
];

export function FrenchReaderSettingsButton() {
  const { t } = useTranslation();
  const [opened, { open, close }] = useDisclosure(false);
  const {
    ttsVoice,
    ttsRate,
    setTtsVoice,
    setTtsRate,
    ttsVoices,
    ttsVoicesLoading,
    ttsVoicesError,
    ttsBusy,
    aiModes,
    setAiModes,
    aiTargetLang,
    setAiTargetLang,
    userApiKey,
    setUserApiKey,
    clearUserApiKey,
  } = useFrenchReaderContext();

  const [draftApiKey, setDraftApiKey] = useState(userApiKey);

  useEffect(() => {
    if (opened) {
      setDraftApiKey(userApiKey);
    }
  }, [opened, userApiKey]);

  const settingsBusy = ttsBusy;

  return (
    <>
      <Tooltip label={t("frenchReader.settings.open", "Settings")}>
        <ActionIcon variant="subtle" size="sm" onClick={open} aria-label="French Reading Assistant settings">
          <SettingsIcon sx={{ fontSize: 18 }} />
        </ActionIcon>
      </Tooltip>

      <Modal
        opened={opened}
        onClose={close}
        title={t("frenchReader.settings.title", "French Reading Assistant settings")}
        size="sm"
      >
        <Stack gap="md">
          <Stack gap="sm">
            <Title order={6}>{t("frenchReader.tts.settingsTitle", "Pronunciation")}</Title>
            {ttsVoicesLoading ? (
              <Group gap="xs">
                <Loader size="xs" />
                <Text size="sm" c="dimmed">
                  {t("frenchReader.tts.loadingVoices", "Loading French voices…")}
                </Text>
              </Group>
            ) : (
              <>
                <Select
                  label={t("frenchReader.tts.voice", "Voice")}
                  data={ttsVoices}
                  value={ttsVoice || null}
                  onChange={(value) => setTtsVoice(value ?? "")}
                  searchable
                  nothingFoundMessage={t("frenchReader.tts.noVoices", "No voices found")}
                  disabled={settingsBusy}
                />
                <Select
                  label={t("frenchReader.tts.speed", "Speed")}
                  data={RATE_OPTIONS.map((option) => ({
                    value: option.value,
                    label: t(option.labelKey, option.fallback),
                  }))}
                  value={ttsRate}
                  onChange={(value) => setTtsRate((value as TtsRate) ?? "+0%")}
                  disabled={settingsBusy}
                />
              </>
            )}
            {ttsVoicesError && (
              <Text size="sm" c="red">
                {ttsVoicesError}
              </Text>
            )}
          </Stack>

          <Divider />

          <Stack gap="sm">
            <Title order={6}>{t("frenchReader.ai.settingsTitle", "AI explanation")}</Title>
            <MultiSelect
              label={t("frenchReader.ai.mode", "Mode")}
              description={t(
                "frenchReader.ai.modeMultiHint",
                "Select one or more modes to run when you click Explain.",
              )}
              data={MODE_OPTIONS.map((option) => ({
                value: option.value,
                label: t(option.labelKey, option.fallback),
              }))}
              value={aiModes}
              onChange={(value) => {
                if (value.length === 0) return;
                setAiModes(value as AiExplainMode[]);
              }}
              disabled={settingsBusy}
              clearable={false}
            />
            <Select
              label={t("frenchReader.ai.targetLang", "Language")}
              data={TARGET_OPTIONS}
              value={aiTargetLang}
              onChange={(value) => setAiTargetLang(value ?? "zh")}
              disabled={settingsBusy}
            />
            <PasswordInput
              label={t("frenchReader.ai.apiKey", "Kimi API key")}
              description={t(
                "frenchReader.ai.apiKeyHint",
                "Paste your Moonshot/Kimi key here. It is stored only in this browser. When empty, the server .env key is used.",
              )}
              placeholder="sk-..."
              value={draftApiKey}
              onChange={(event) => setDraftApiKey(event.currentTarget.value)}
              disabled={settingsBusy}
            />
            <Group gap="xs">
              <Button
                size="compact-xs"
                variant="light"
                onClick={() => setUserApiKey(draftApiKey)}
                disabled={settingsBusy || draftApiKey.trim() === userApiKey.trim()}
              >
                {t("frenchReader.ai.apiKeySave", "Save key")}
              </Button>
              <Button
                size="compact-xs"
                variant="subtle"
                color="red"
                onClick={() => {
                  clearUserApiKey();
                  setDraftApiKey("");
                }}
                disabled={settingsBusy || !userApiKey}
              >
                {t("frenchReader.ai.apiKeyClear", "Clear key")}
              </Button>
            </Group>
            {userApiKey && (
              <Text size="xs" c="dimmed">
                {t("frenchReader.ai.apiKeySaved", "Saved key: {{masked}}", {
                  masked: maskUserLlmApiKey(userApiKey),
                })}
              </Text>
            )}
          </Stack>

          <Button onClick={close}>{t("frenchReader.tts.settingsDone", "Done")}</Button>
        </Stack>
      </Modal>
    </>
  );
}
