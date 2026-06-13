import type { AiExplainMode, AiTranslationResults } from "@app/hooks/tools/frenchReader/types";
import type { OcrHistoryEntry } from "@app/hooks/tools/frenchReader/historyTypes";

const MODE_LABEL: Record<AiExplainMode, string> = {
  translate: "Translation",
  vocabulary: "Vocabulary",
  grammar: "Grammar",
};

const MODE_ORDER: AiExplainMode[] = ["translate", "vocabulary", "grammar"];

const STORAGE_KEY = "french-reader-ocr-history";
const MAX_ENTRIES = 200;

function readRaw(): OcrHistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as OcrHistoryEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeRaw(entries: OcrHistoryEntry[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
}

export function loadOcrHistory(): OcrHistoryEntry[] {
  return readRaw();
}

export function appendOcrHistory(entry: OcrHistoryEntry): OcrHistoryEntry[] {
  const next = [entry, ...readRaw()].slice(0, MAX_ENTRIES);
  writeRaw(next);
  return next;
}

export function updateOcrHistoryTranslation(
  id: string,
  translation: string,
  mode: AiExplainMode,
): OcrHistoryEntry[] {
  return updateOcrHistoryTranslations(id, { [mode]: translation });
}

export function updateOcrHistoryTranslations(
  id: string,
  patch: AiTranslationResults,
): OcrHistoryEntry[] {
  const next = readRaw().map((entry) => {
    if (entry.id !== id) return entry;
    const translations = { ...(entry.translations ?? {}), ...patch };
    if (entry.translation && entry.translationMode && !translations[entry.translationMode]) {
      translations[entry.translationMode] = entry.translation;
    }
    const primaryMode =
      (Object.keys(translations)[0] as AiExplainMode | undefined) ?? "translate";
    return {
      ...entry,
      translations,
      translation: translations.translate ?? translations[primaryMode],
      translationMode: translations.translate ? "translate" : primaryMode,
    };
  });
  writeRaw(next);
  return next;
}

function entryTranslations(entry: OcrHistoryEntry): AiTranslationResults {
  if (entry.translations && Object.keys(entry.translations).length > 0) {
    return entry.translations;
  }
  if (entry.translation) {
    return { [entry.translationMode ?? "translate"]: entry.translation };
  }
  return {};
}

function appendTranslationExportLines(lines: string[], entry: OcrHistoryEntry): void {
  const translations = entryTranslations(entry);
  for (const mode of MODE_ORDER) {
    const text = translations[mode];
    if (!text) continue;
    lines.push("", `${MODE_LABEL[mode]}:`, text);
  }
}

export function clearOcrHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function exportHistoryAsText(
  entries: OcrHistoryEntry[],
  sourceFileName: string,
): string {
  const header = `French Reading Assistant Notes — ${sourceFileName}\nExported: ${formatTimestamp(new Date().toISOString())}\n${"=".repeat(48)}\n\n`;
  const body = entries
    .map((entry, index) => {
      const lines = [
        `[${index + 1}] ${formatTimestamp(entry.createdAt)} · Page ${entry.page}`,
        `File: ${entry.fileName}`,
        "",
        "French:",
        entry.text,
      ];
      appendTranslationExportLines(lines, entry);
      return lines.join("\n");
    })
    .join("\n\n" + "-".repeat(32) + "\n\n");
  return header + body + "\n";
}

export function exportHistoryAsMarkdown(
  entries: OcrHistoryEntry[],
  sourceFileName: string,
): string {
  const header = `# French Reading Assistant Notes\n\n**Source:** ${sourceFileName}  \n**Exported:** ${formatTimestamp(new Date().toISOString())}\n\n---\n\n`;
  const body = entries
    .map((entry, index) => {
      const lines = [
        `## ${index + 1}. Page ${entry.page} · ${formatTimestamp(entry.createdAt)}`,
        "",
        `> ${entry.fileName}`,
        "",
        "**French**",
        "",
        entry.text
          .split("\n")
          .map((line) => (line ? line : ""))
          .join("\n\n"),
      ];
      const translations = entryTranslations(entry);
      for (const mode of MODE_ORDER) {
        const text = translations[mode];
        if (!text) continue;
        lines.push("", `**${MODE_LABEL[mode]}**`, "", text);
      }
      return lines.join("\n");
    })
    .join("\n\n---\n\n");
  return header + body + "\n";
}

export function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  downloadBlobFile(filename, blob);
}

export function downloadBlobFile(filename: string, blob: Blob): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function buildHistoryExportFilename(
  sourceFileName: string,
  extension: "txt" | "md" | "pdf",
): string {
  const stamp = new Date().toISOString().slice(0, 10);
  const safeName = sourceFileName.replace(/[^\w.-]+/g, "_") || "notes";
  return `french-reader-${safeName}-${stamp}.${extension}`;
}
