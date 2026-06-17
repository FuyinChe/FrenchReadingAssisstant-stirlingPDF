import { isTauriRuntime } from "@app/services/frenchReaderFetch";

/**
 * WKWebView (macOS Tauri) often rejects `new Audio(blobUrl).play()` with
 * NotSupportedError even for valid MP3. Web Audio API works reliably on desktop.
 */
export async function playTtsAudio(blob: Blob, signal: AbortSignal): Promise<void> {
  if (isTauriRuntime()) {
    await playViaWebAudio(blob, signal);
    return;
  }

  const url = URL.createObjectURL(blob);
  try {
    const audio = new Audio(url);
    await new Promise<void>((resolve, reject) => {
      const onAbort = () => {
        audio.pause();
        resolve();
      };
      signal.addEventListener("abort", onAbort, { once: true });
      audio.onended = () => resolve();
      audio.onerror = () => reject(new Error("Audio playback failed"));
      void audio.play().catch(reject);
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

async function playViaWebAudio(blob: Blob, signal: AbortSignal): Promise<void> {
  const context = new AudioContext();
  try {
    if (context.state === "suspended") {
      await context.resume();
    }
    const buffer = await context.decodeAudioData(await blob.arrayBuffer());
    if (signal.aborted) return;

    await new Promise<void>((resolve, reject) => {
      const source = context.createBufferSource();
      source.buffer = buffer;
      source.connect(context.destination);

      const cleanup = () => {
        signal.removeEventListener("abort", onAbort);
      };
      const onAbort = () => {
        try {
          source.stop();
        } catch {
          // already stopped
        }
        cleanup();
        resolve();
      };

      signal.addEventListener("abort", onAbort);
      source.onended = () => {
        cleanup();
        resolve();
      };
      try {
        source.start(0);
      } catch (error) {
        cleanup();
        reject(error instanceof Error ? error : new Error("Audio playback failed"));
      }
    });
  } finally {
    await context.close();
  }
}
