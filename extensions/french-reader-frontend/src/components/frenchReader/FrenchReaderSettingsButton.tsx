import {
  ActionIcon,
  Anchor,
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
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import SettingsIcon from "@mui/icons-material/Settings";

import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import type { AiExplainMode, LlmProviderInfo, TtsRate } from "@app/hooks/tools/frenchReader/types";
import { fetchLlmProviders } from "@app/services/frenchReaderApi";
import {
  DEFAULT_LLM_PROVIDER_ID,
  DEFAULT_USER_LLM_SETTINGS,
  FALLBACK_LLM_PROVIDERS,
  maskUserLlmApiKey,
  providerRequiresEndpoint,
  type UserLlmSettings,
} from "@app/services/frenchReaderLlmSettings";
import {
  FRENCH_READER_BUILD_ID,
  FRENCH_READER_BUILD_PLATFORM,
  FRENCH_READER_PLUGIN_VERSION,
} from "@app/services/frenchReaderVersion";

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

const PROVIDER_GROUP_LABELS: Record<string, { key: string; fallback: string }> = {
  recommended: { key: "frenchReader.ai.providerGroupRecommended", fallback: "Recommended" },
  international: {
    key: "frenchReader.ai.providerGroupInternational",
    fallback: "Major providers",
  },
  other: { key: "frenchReader.ai.providerGroupOther", fallback: "Other" },
};

function settingsEqual(a: UserLlmSettings, b: UserLlmSettings): boolean {
  return (
    a.providerId === b.providerId &&
    a.apiKey.trim() === b.apiKey.trim() &&
    a.customBaseUrl.trim() === b.customBaseUrl.trim() &&
    a.customModel.trim() === b.customModel.trim()
  );
}

function buildProviderSelectData(
  providers: LlmProviderInfo[],
  t: (key: string, fallback: string) => string,
) {
  const grouped = new Map<string, { value: string; label: string }[]>();
  for (const provider of providers) {
    const groupKey = provider.group ?? "other";
    const items = grouped.get(groupKey) ?? [];
    items.push({ value: provider.id, label: provider.name });
    grouped.set(groupKey, items);
  }

  const order = ["recommended", "international", "other"];
  return order
    .filter((key) => grouped.has(key))
    .map((key) => {
      const meta = PROVIDER_GROUP_LABELS[key] ?? PROVIDER_GROUP_LABELS.other;
      return {
        group: t(meta.key, meta.fallback),
        items: grouped.get(key) ?? [],
      };
    });
}

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
    llmSettings,
    saveLlmSettings,
    clearLlmSettings,
  } = useFrenchReaderContext();

  const [providers, setProviders] = useState<LlmProviderInfo[]>(FALLBACK_LLM_PROVIDERS);
  const [defaultProviderId, setDefaultProviderId] = useState(DEFAULT_LLM_PROVIDER_ID);
  const [draftLlmSettings, setDraftLlmSettings] = useState<UserLlmSettings>(llmSettings);

  useEffect(() => {
    if (opened) {
      setDraftLlmSettings(llmSettings);
      void fetchLlmProviders().then((response) => {
        if (response.providers.length > 0) {
          setProviders(response.providers);
        }
        if (response.default_provider) {
          setDefaultProviderId(response.default_provider);
        }
      });
    }
  }, [opened, llmSettings]);

  const selectedProvider = useMemo(
    () =>
      providers.find((item) => item.id === draftLlmSettings.providerId) ??
      providers.find((item) => item.id === defaultProviderId) ??
      providers[0],
    [defaultProviderId, draftLlmSettings.providerId, providers],
  );

  const providerSelectData = useMemo(
    () => buildProviderSelectData(providers, t),
    [providers, t],
  );

  const showEndpointFields = providerRequiresEndpoint(
    draftLlmSettings.providerId,
    selectedProvider,
  );
  const isCopilot = draftLlmSettings.providerId === "copilot";

  const settingsBusy = ttsBusy;
  const hasSavedKey = Boolean(llmSettings.apiKey.trim());
  const draftUnchanged = settingsEqual(draftLlmSettings, llmSettings);

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

            <Select
              label={t("frenchReader.ai.provider", "LLM provider")}
              description={t(
                "frenchReader.ai.providerHint",
                "Choose your model vendor, then paste the matching API key below.",
              )}
              data={providerSelectData}
              value={draftLlmSettings.providerId || defaultProviderId}
              onChange={(value) =>
                setDraftLlmSettings((prev) => ({
                  ...prev,
                  providerId: value || defaultProviderId,
                }))
              }
              searchable
              nothingFoundMessage={t("frenchReader.ai.noProviders", "No providers found")}
              disabled={settingsBusy}
            />

            {selectedProvider?.default_model && !showEndpointFields ? (
              <Text size="xs" c="dimmed">
                {t("frenchReader.ai.defaultModel", "Default model: {{model}}", {
                  model: selectedProvider.default_model,
                })}
              </Text>
            ) : null}

            {showEndpointFields && (
              <>
                <TextInput
                  label={
                    isCopilot
                      ? t("frenchReader.ai.azureEndpoint", "Azure endpoint URL")
                      : t("frenchReader.ai.customBaseUrl", "Base URL")
                  }
                  placeholder={
                    isCopilot
                      ? "https://YOUR-RESOURCE.openai.azure.com"
                      : "https://api.example.com/v1"
                  }
                  value={draftLlmSettings.customBaseUrl}
                  onChange={(event) =>
                    setDraftLlmSettings((prev) => ({
                      ...prev,
                      customBaseUrl: event.currentTarget.value,
                    }))
                  }
                  disabled={settingsBusy}
                />
                <TextInput
                  label={
                    isCopilot
                      ? t("frenchReader.ai.azureDeployment", "Deployment name")
                      : t("frenchReader.ai.customModel", "Model")
                  }
                  placeholder={isCopilot ? "gpt-4o-mini" : "your-model-name"}
                  value={draftLlmSettings.customModel}
                  onChange={(event) =>
                    setDraftLlmSettings((prev) => ({
                      ...prev,
                      customModel: event.currentTarget.value,
                    }))
                  }
                  disabled={settingsBusy}
                />
              </>
            )}

            <PasswordInput
              label={t("frenchReader.ai.apiKey", "API key")}
              description={
                selectedProvider?.key_hint ||
                t(
                  "frenchReader.ai.apiKeyHint",
                  "Stored only in this browser. When empty, the server .env key is used.",
                )
              }
              placeholder="sk-..."
              value={draftLlmSettings.apiKey}
              onChange={(event) =>
                setDraftLlmSettings((prev) => ({
                  ...prev,
                  apiKey: event.currentTarget.value,
                }))
              }
              disabled={settingsBusy}
            />

            {selectedProvider?.docs_url ? (
              <Text size="xs" c="dimmed">
                {t("frenchReader.ai.getApiKey", "Get an API key:")}{" "}
                <Anchor href={selectedProvider.docs_url} target="_blank" rel="noreferrer">
                  {selectedProvider.docs_url}
                </Anchor>
              </Text>
            ) : null}

            <Group gap="xs">
              <Button
                size="compact-xs"
                variant="light"
                onClick={() => saveLlmSettings(draftLlmSettings)}
                disabled={settingsBusy || draftUnchanged}
              >
                {t("frenchReader.ai.apiKeySave", "Save settings")}
              </Button>
              <Button
                size="compact-xs"
                variant="subtle"
                color="red"
                onClick={() => {
                  clearLlmSettings();
                  setDraftLlmSettings(DEFAULT_USER_LLM_SETTINGS);
                }}
                disabled={settingsBusy || !hasSavedKey}
              >
                {t("frenchReader.ai.apiKeyClear", "Clear key")}
              </Button>
            </Group>
            {hasSavedKey && (
              <Text size="xs" c="dimmed">
                {t("frenchReader.ai.apiKeySaved", "Saved: {{provider}} · {{masked}}", {
                  provider:
                    providers.find((item) => item.id === llmSettings.providerId)?.name ??
                    llmSettings.providerId,
                  masked: maskUserLlmApiKey(llmSettings.apiKey),
                })}
              </Text>
            )}
          </Stack>

          <Text size="xs" c="dimmed" ta="center">
            {t("frenchReader.version.label", "Plugin v{{version}}", {
              version: FRENCH_READER_PLUGIN_VERSION,
            })}
            {FRENCH_READER_BUILD_PLATFORM
              ? ` · ${FRENCH_READER_BUILD_PLATFORM}`
              : ""}
            {FRENCH_READER_BUILD_ID ? ` · ${FRENCH_READER_BUILD_ID}` : ""}
          </Text>

          <Button onClick={close}>{t("frenchReader.tts.settingsDone", "Done")}</Button>
        </Stack>
      </Modal>
    </>
  );
}
