export const DEFAULT_LLM_PROVIDER_ID = "kimi";

export interface LlmProviderInfo {
  id: string;
  name: string;
  base_url: string;
  default_model: string;
  key_hint: string;
  docs_url: string;
  api_style?: string;
  requires_endpoint?: boolean;
  group?: string;
}

export interface LlmProvidersResponse {
  default_provider: string;
  providers: LlmProviderInfo[];
}

export interface UserLlmSettings {
  providerId: string;
  apiKey: string;
  customBaseUrl: string;
  customModel: string;
}

const STORAGE_KEY = "french-reader-llm-settings";
const LEGACY_API_KEY_STORAGE = "french-reader-user-llm-api-key";

export const DEFAULT_USER_LLM_SETTINGS: UserLlmSettings = {
  providerId: DEFAULT_LLM_PROVIDER_ID,
  apiKey: "",
  customBaseUrl: "",
  customModel: "",
};

export function providerRequiresEndpoint(
  providerId: string,
  provider?: Pick<LlmProviderInfo, "requires_endpoint">,
): boolean {
  if (provider?.requires_endpoint) return true;
  return providerId === "custom" || providerId === "copilot";
}

function normalizeProviderId(raw: unknown): string {
  return typeof raw === "string" && raw.trim() ? raw.trim() : DEFAULT_LLM_PROVIDER_ID;
}

export function loadUserLlmSettings(): UserLlmSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as Partial<UserLlmSettings>;
      return {
        providerId: normalizeProviderId(parsed.providerId),
        apiKey: typeof parsed.apiKey === "string" ? parsed.apiKey.trim() : "",
        customBaseUrl:
          typeof parsed.customBaseUrl === "string" ? parsed.customBaseUrl.trim() : "",
        customModel: typeof parsed.customModel === "string" ? parsed.customModel.trim() : "",
      };
    }
  } catch {
    // fall through to legacy migration
  }

  try {
    const legacyKey = localStorage.getItem(LEGACY_API_KEY_STORAGE)?.trim() ?? "";
    if (legacyKey) {
      return {
        ...DEFAULT_USER_LLM_SETTINGS,
        apiKey: legacyKey,
      };
    }
  } catch {
    // ignore
  }

  return DEFAULT_USER_LLM_SETTINGS;
}

export function saveUserLlmSettings(settings: UserLlmSettings): void {
  const cleaned: UserLlmSettings = {
    providerId: normalizeProviderId(settings.providerId),
    apiKey: settings.apiKey.trim(),
    customBaseUrl: settings.customBaseUrl.trim(),
    customModel: settings.customModel.trim(),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cleaned));
  if (cleaned.apiKey) {
    localStorage.removeItem(LEGACY_API_KEY_STORAGE);
  }
}

export function clearUserLlmSettings(): void {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(LEGACY_API_KEY_STORAGE);
}

export function maskUserLlmApiKey(apiKey: string): string {
  const cleaned = apiKey.trim();
  if (!cleaned) return "";
  if (cleaned.length <= 8) return "••••••••";
  return `••••${cleaned.slice(-4)}`;
}

export const FALLBACK_LLM_PROVIDERS: LlmProviderInfo[] = [
  {
    id: "kimi",
    name: "Kimi (Moonshot)",
    base_url: "https://api.moonshot.ai/v1",
    default_model: "moonshot-v1-32k",
    key_hint: "Moonshot international API key",
    docs_url: "https://platform.moonshot.ai/",
    group: "recommended",
  },
  {
    id: "openai",
    name: "OpenAI",
    base_url: "https://api.openai.com/v1",
    default_model: "gpt-4o-mini",
    key_hint: "OpenAI API key",
    docs_url: "https://platform.openai.com/api-keys",
    group: "international",
  },
  {
    id: "gemini",
    name: "Google Gemini",
    base_url: "https://generativelanguage.googleapis.com/v1beta/openai",
    default_model: "gemini-2.0-flash",
    key_hint: "Google AI Studio API key",
    docs_url: "https://aistudio.google.com/apikey",
    group: "international",
  },
  {
    id: "claude",
    name: "Anthropic Claude",
    base_url: "https://api.anthropic.com",
    default_model: "claude-3-5-sonnet-latest",
    key_hint: "Anthropic API key",
    docs_url: "https://console.anthropic.com/settings/keys",
    api_style: "anthropic",
    group: "international",
  },
  {
    id: "copilot",
    name: "Microsoft Copilot (Azure OpenAI)",
    base_url: "",
    default_model: "",
    key_hint: "Azure OpenAI API key",
    docs_url: "https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI",
    api_style: "azure_openai",
    requires_endpoint: true,
    group: "international",
  },
  {
    id: "kimi-cn",
    name: "Kimi 国内版",
    base_url: "https://api.moonshot.cn/v1",
    default_model: "moonshot-v1-32k",
    key_hint: "Moonshot China API key",
    docs_url: "https://platform.moonshot.cn/",
    group: "other",
  },
  {
    id: "deepseek",
    name: "DeepSeek",
    base_url: "https://api.deepseek.com/v1",
    default_model: "deepseek-chat",
    key_hint: "DeepSeek API key",
    docs_url: "https://platform.deepseek.com/",
    group: "other",
  },
  {
    id: "zhipu",
    name: "智谱 AI (GLM)",
    base_url: "https://open.bigmodel.cn/api/paas/v4",
    default_model: "glm-4-flash",
    key_hint: "Zhipu API key",
    docs_url: "https://open.bigmodel.cn/",
    group: "other",
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    base_url: "https://openrouter.ai/api/v1",
    default_model: "openai/gpt-4o-mini",
    key_hint: "OpenRouter API key",
    docs_url: "https://openrouter.ai/keys",
    group: "other",
  },
  {
    id: "custom",
    name: "Custom (OpenAI-compatible)",
    base_url: "",
    default_model: "",
    key_hint: "API key for your custom endpoint",
    docs_url: "",
    requires_endpoint: true,
    group: "other",
  },
];
