import { downloadBlobFile } from "@app/services/frenchReaderHistory";

export type ExportFormat = "txt" | "md" | "pdf";

export interface SaveExportResult {
  saved: boolean;
  cancelled: boolean;
  displayPath: string;
  usedSystemDialog: boolean;
}

const FORMAT_META: Record<
  ExportFormat,
  { mime: string; extension: string; description: string }
> = {
  pdf: { mime: "application/pdf", extension: "pdf", description: "PDF document" },
  md: { mime: "text/markdown;charset=utf-8", extension: "md", description: "Markdown" },
  txt: { mime: "text/plain;charset=utf-8", extension: "txt", description: "Plain text" },
};

function isTauriRuntime(): boolean {
  if (typeof window === "undefined") return false;
  const w = window as Window & { __TAURI_INTERNALS__?: unknown; __TAURI__?: unknown };
  return Boolean(w.__TAURI_INTERNALS__ || w.__TAURI__);
}

export function defaultDownloadsFolderHint(): string {
  if (typeof navigator === "undefined") return "Downloads";
  const ua = navigator.userAgent;
  const platform = navigator.platform ?? "";
  if (/Win/i.test(ua) || /Win/i.test(platform)) {
    return "%USERPROFILE%\\Downloads";
  }
  if (/Mac/i.test(ua) || /Mac/i.test(platform)) {
    return "~/Downloads";
  }
  return "Downloads";
}

async function saveViaTauri(
  suggestedName: string,
  blob: Blob,
  format: ExportFormat,
): Promise<SaveExportResult | null> {
  if (!isTauriRuntime()) return null;
  try {
    const dialog = await import("@tauri-apps/plugin-dialog");
    const fs = await import("@tauri-apps/plugin-fs");
    const meta = FORMAT_META[format];
    const path = await dialog.save({
      defaultPath: suggestedName,
      filters: [{ name: meta.description, extensions: [meta.extension] }],
    });
    if (!path) {
      return { saved: false, cancelled: true, displayPath: "", usedSystemDialog: true };
    }
    await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
    return { saved: true, cancelled: false, displayPath: path, usedSystemDialog: true };
  } catch {
    return null;
  }
}

async function saveViaFilePicker(
  suggestedName: string,
  blob: Blob,
  format: ExportFormat,
): Promise<SaveExportResult | null> {
  const picker = (
    window as Window & {
      showSaveFilePicker?: (options: {
        suggestedName?: string;
        types?: { description: string; accept: Record<string, string[]> }[];
      }) => Promise<FileSystemFileHandle>;
    }
  ).showSaveFilePicker;
  if (!picker) return null;

  const meta = FORMAT_META[format];
  try {
    const handle = await picker({
      suggestedName,
      types: [
        {
          description: meta.description,
          accept: { [meta.mime]: [`.${meta.extension}`] },
        },
      ],
    });
    const writable = await handle.createWritable();
    await writable.write(blob);
    await writable.close();
    return {
      saved: true,
      cancelled: false,
      displayPath: handle.name,
      usedSystemDialog: true,
    };
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      return { saved: false, cancelled: true, displayPath: "", usedSystemDialog: true };
    }
    return null;
  }
}

/** Save export with native dialog (Tauri / File System Access API) or browser download fallback. */
export async function saveExportFile(
  suggestedName: string,
  content: string | Blob,
  format: ExportFormat,
): Promise<SaveExportResult> {
  const meta = FORMAT_META[format];
  const blob =
    content instanceof Blob ? content : new Blob([content], { type: meta.mime });

  const tauriResult = await saveViaTauri(suggestedName, blob, format);
  if (tauriResult) return tauriResult;

  const pickerResult = await saveViaFilePicker(suggestedName, blob, format);
  if (pickerResult) return pickerResult;

  downloadBlobFile(suggestedName, blob);
  return {
    saved: true,
    cancelled: false,
    displayPath: `${defaultDownloadsFolderHint()}/${suggestedName}`,
    usedSystemDialog: false,
  };
}
