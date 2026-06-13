const STORAGE_KEY = "french-reader-user-llm-api-key";

export function loadUserLlmApiKey(): string {
  try {
    return localStorage.getItem(STORAGE_KEY)?.trim() ?? "";
  } catch {
    return "";
  }
}

export function saveUserLlmApiKey(apiKey: string): void {
  const cleaned = apiKey.trim();
  if (cleaned) {
    localStorage.setItem(STORAGE_KEY, cleaned);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function clearUserLlmApiKey(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function maskUserLlmApiKey(apiKey: string): string {
  const cleaned = apiKey.trim();
  if (!cleaned) return "";
  if (cleaned.length <= 8) return "••••••••";
  return `••••${cleaned.slice(-4)}`;
}
