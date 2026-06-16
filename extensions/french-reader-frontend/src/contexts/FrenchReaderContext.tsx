import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { OcrHistoryEntry } from "@app/hooks/tools/frenchReader/historyTypes";
import { useAiSettings } from "@app/hooks/tools/frenchReader/useAiSettings";
import { useBubbleDetection } from "@app/hooks/tools/frenchReader/useBubbleDetection";
import { useParagraphDetection } from "@app/hooks/tools/frenchReader/useParagraphDetection";
import { useTtsPlay } from "@app/hooks/tools/frenchReader/useTtsPlay";
import { useTtsSettings } from "@app/hooks/tools/frenchReader/useTtsSettings";
import type {
  AiExplainMode,
  AiTranslationResults,
  DetectedBubble,
  DetectedParagraph,
  FrenchReaderSelection,
  OcrLineResult,
  OcrResult,
  TtsRate,
} from "@app/hooks/tools/frenchReader/types";
import type { UserLlmSettings } from "@app/services/frenchReaderLlmSettings";
import { exportHistoryPdf } from "@app/services/frenchReaderApi";
import {
  appendOcrHistory,
  clearOcrHistory,
  buildHistoryExportFilename,
  exportHistoryAsMarkdown,
  exportHistoryAsText,
  loadOcrHistory,
  removeOcrHistoryEntry,
  updateOcrHistoryTranslations,
} from "@app/services/frenchReaderHistory";
import { saveExportFile } from "@app/services/saveExportFile";

interface FrenchReaderContextValue {
  selection: FrenchReaderSelection | null;
  ocrResult: OcrResult | null;
  ocrLoading: boolean;
  ocrError: string | null;
  currentTranslations: AiTranslationResults;
  history: OcrHistoryEntry[];
  currentEntryId: string | null;
  setSelection: (selection: FrenchReaderSelection | null) => void;
  setOcrResult: (result: OcrResult | null) => void;
  setOcrLoading: (loading: boolean) => void;
  setOcrError: (error: string | null) => void;
  clearOcr: () => void;
  recordOcrResult: (params: {
    fileName: string;
    page: number;
    result: OcrResult;
  }) => void;
  setTranslationForMode: (mode: AiExplainMode, text: string) => void;
  restoreHistoryEntry: (id: string) => void;
  removeHistoryEntry: (id: string) => void;
  clearHistory: () => void;
  exportHistory: (format: "txt" | "md" | "pdf", sourceFileName: string) => Promise<void>;
  exportError: string | null;
  exportSuccess: { displayPath: string; usedSystemDialog: boolean } | null;
  exportInProgress: boolean;
  clearExportFeedback: () => void;
  aiModes: AiExplainMode[];
  setAiModes: (modes: AiExplainMode[]) => void;
  aiTargetLang: string;
  setAiTargetLang: (lang: string) => void;
  llmSettings: UserLlmSettings;
  saveLlmSettings: (settings: UserLlmSettings) => void;
  clearLlmSettings: () => void;
  ttsVoice: string;
  ttsRate: TtsRate;
  setTtsVoice: (voice: string) => void;
  setTtsRate: (rate: TtsRate) => void;
  ttsVoices: { value: string; label: string }[];
  ttsVoicesLoading: boolean;
  ttsVoicesError: string | null;
  playTts: (text: string, lines: OcrLineResult[]) => Promise<void>;
  stopTts: () => void;
  ttsPlaying: boolean;
  ttsSynthesizing: boolean;
  ttsBusy: boolean;
  ttsError: string | null;
  getBubblesForPage: (page: number) => DetectedBubble[];
  detectBubblesForPage: (params: {
    file: File | Blob;
    pageNumber: number;
    confidenceThreshold?: number;
  }) => Promise<{ bubbles: DetectedBubble[]; detector: string }>;
  clearBubblesForPage: (page: number) => void;
  clearAllBubbles: () => void;
  bubbleDetectLoading: boolean;
  bubbleDetectError: string | null;
  bubblePreprocess: boolean;
  setBubblePreprocess: (enabled: boolean) => void;
  bubbleDetectorReady: boolean | null;
  bubbleStatusLoadFailed: boolean;
  lastBubbleDetector: string | null;
  getParagraphsForPage: (page: number) => DetectedParagraph[];
  detectParagraphsForPage: (params: {
    file: File | Blob;
    pageNumber: number;
    confidenceThreshold?: number;
  }) => Promise<{ paragraphs: DetectedParagraph[]; detector: string }>;
  clearParagraphsForPage: (page: number) => void;
  clearAllParagraphs: () => void;
  paragraphDetectLoading: boolean;
  paragraphDetectError: string | null;
  paragraphPreprocess: boolean;
  setParagraphPreprocess: (enabled: boolean) => void;
  paragraphDetectorReady: boolean | null;
  paragraphStatusLoadFailed: boolean;
  lastParagraphDetector: string | null;
}

const FrenchReaderContext = createContext<FrenchReaderContextValue | null>(null);

function translationsFromEntry(entry: OcrHistoryEntry): AiTranslationResults {
  if (entry.translations && Object.keys(entry.translations).length > 0) {
    return entry.translations;
  }
  if (entry.translation) {
    return { [entry.translationMode ?? "translate"]: entry.translation };
  }
  return {};
}

export function FrenchReaderProvider({ children }: { children: ReactNode }) {
  const [selection, setSelection] = useState<FrenchReaderSelection | null>(null);
  const [ocrResult, setOcrResult] = useState<OcrResult | null>(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [currentTranslations, setCurrentTranslations] = useState<AiTranslationResults>({});
  const [history, setHistory] = useState<OcrHistoryEntry[]>(() => loadOcrHistory());
  const [currentEntryId, setCurrentEntryId] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<{
    displayPath: string;
    usedSystemDialog: boolean;
  } | null>(null);
  const [exportInProgress, setExportInProgress] = useState(false);

  const clearExportFeedback = useCallback(() => {
    setExportError(null);
    setExportSuccess(null);
  }, []);

  const ttsSettings = useTtsSettings();
  const ttsPlay = useTtsPlay();
  const aiSettings = useAiSettings();
  const bubbleDetection = useBubbleDetection();
  const paragraphDetection = useParagraphDetection();

  const clearOcr = useCallback(() => {
    setSelection(null);
    setOcrResult(null);
    setOcrError(null);
    setOcrLoading(false);
    setCurrentTranslations({});
    setCurrentEntryId(null);
    ttsPlay.stop();
  }, [ttsPlay]);

  const recordOcrResult = useCallback(
    ({ fileName, page, result }: { fileName: string; page: number; result: OcrResult }) => {
      const entry: OcrHistoryEntry = {
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
        fileName,
        page,
        text: result.text,
        lines: result.lines,
        confidence: result.confidence,
      };
      setHistory(appendOcrHistory(entry));
      setCurrentEntryId(entry.id);
      setCurrentTranslations({});
    },
    [],
  );

  const setTranslationForMode = useCallback(
    (mode: AiExplainMode, text: string) => {
      setCurrentTranslations((prev) => ({ ...prev, [mode]: text }));
      if (currentEntryId) {
        setHistory(updateOcrHistoryTranslations(currentEntryId, { [mode]: text }));
      }
    },
    [currentEntryId],
  );

  const restoreHistoryEntry = useCallback(
    (id: string) => {
      const entry = history.find((item) => item.id === id);
      if (!entry) return;
      setOcrResult({
        text: entry.text,
        confidence: entry.confidence,
        lines: entry.lines,
      });
      setCurrentEntryId(entry.id);
      setCurrentTranslations(translationsFromEntry(entry));
      setOcrError(null);
    },
    [history],
  );

  const removeHistoryEntry = useCallback(
    (id: string) => {
      const next = removeOcrHistoryEntry(id);
      setHistory(next);
      if (currentEntryId === id) {
        setOcrResult(null);
        setCurrentEntryId(null);
        setCurrentTranslations({});
        setOcrError(null);
        ttsPlay.stop();
      }
    },
    [currentEntryId, ttsPlay],
  );

  const clearHistory = useCallback(() => {
    clearOcrHistory();
    setHistory([]);
  }, []);

  const exportHistory = useCallback(
    async (format: "txt" | "md" | "pdf", sourceFileName: string) => {
      if (history.length === 0) return;
      setExportError(null);
      setExportSuccess(null);
      setExportInProgress(true);
      const filename = buildHistoryExportFilename(sourceFileName, format);
      try {
        let result;
        if (format === "md") {
          result = await saveExportFile(
            filename,
            exportHistoryAsMarkdown(history, sourceFileName),
            format,
          );
        } else if (format === "txt") {
          result = await saveExportFile(
            filename,
            exportHistoryAsText(history, sourceFileName),
            format,
          );
        } else {
          const blob = await exportHistoryPdf({
            sourceFileName,
            entries: history,
          });
          result = await saveExportFile(filename, blob, format);
        }
        if (result.cancelled) return;
        setExportSuccess({
          displayPath: result.displayPath,
          usedSystemDialog: result.usedSystemDialog,
        });
      } catch (error) {
        setExportError(error instanceof Error ? error.message : "Export failed");
      } finally {
        setExportInProgress(false);
      }
    },
    [history],
  );

  const playTts = useCallback(
    async (text: string, lines: OcrLineResult[]) => {
      await ttsPlay.play(text, lines, ttsSettings.voice, ttsSettings.rate);
    },
    [ttsPlay, ttsSettings.rate, ttsSettings.voice],
  );

  const value = useMemo(
    () => ({
      selection,
      ocrResult,
      ocrLoading,
      ocrError,
      currentTranslations,
      history,
      currentEntryId,
      setSelection,
      setOcrResult,
      setOcrLoading,
      setOcrError,
      clearOcr,
      recordOcrResult,
      setTranslationForMode,
      restoreHistoryEntry,
      removeHistoryEntry,
      clearHistory,
      exportHistory,
      exportError,
      exportSuccess,
      exportInProgress,
      clearExportFeedback,
      aiModes: aiSettings.modes,
      setAiModes: aiSettings.setModes,
      aiTargetLang: aiSettings.targetLang,
      setAiTargetLang: aiSettings.setTargetLang,
      llmSettings: aiSettings.llmSettings,
      saveLlmSettings: aiSettings.saveLlmSettings,
      clearLlmSettings: aiSettings.clearLlmSettings,
      ttsVoice: ttsSettings.voice,
      ttsRate: ttsSettings.rate,
      setTtsVoice: ttsSettings.setVoice,
      setTtsRate: ttsSettings.setRate,
      ttsVoices: ttsSettings.voices,
      ttsVoicesLoading: ttsSettings.loadingVoices,
      ttsVoicesError: ttsSettings.voicesError,
      playTts,
      stopTts: ttsPlay.stop,
      ttsPlaying: ttsPlay.playing,
      ttsSynthesizing: ttsPlay.synthesizing,
      ttsBusy: ttsPlay.busy,
      ttsError: ttsPlay.error,
      getBubblesForPage: bubbleDetection.getBubblesForPage,
      detectBubblesForPage: bubbleDetection.detectBubblesForPage,
      clearBubblesForPage: bubbleDetection.clearBubblesForPage,
      clearAllBubbles: bubbleDetection.clearAllBubbles,
      bubbleDetectLoading: bubbleDetection.bubbleDetectLoading,
      bubbleDetectError: bubbleDetection.bubbleDetectError,
      bubblePreprocess: bubbleDetection.bubblePreprocess,
      setBubblePreprocess: bubbleDetection.setBubblePreprocess,
      bubbleDetectorReady: bubbleDetection.bubbleDetectorReady,
      bubbleStatusLoadFailed: bubbleDetection.bubbleStatusLoadFailed,
      lastBubbleDetector: bubbleDetection.lastBubbleDetector,
      getParagraphsForPage: paragraphDetection.getParagraphsForPage,
      detectParagraphsForPage: paragraphDetection.detectParagraphsForPage,
      clearParagraphsForPage: paragraphDetection.clearParagraphsForPage,
      clearAllParagraphs: paragraphDetection.clearAllParagraphs,
      paragraphDetectLoading: paragraphDetection.paragraphDetectLoading,
      paragraphDetectError: paragraphDetection.paragraphDetectError,
      paragraphPreprocess: paragraphDetection.paragraphPreprocess,
      setParagraphPreprocess: paragraphDetection.setParagraphPreprocess,
      paragraphDetectorReady: paragraphDetection.paragraphDetectorReady,
      paragraphStatusLoadFailed: paragraphDetection.paragraphStatusLoadFailed,
      lastParagraphDetector: paragraphDetection.lastParagraphDetector,
    }),
    [
      selection,
      ocrResult,
      ocrLoading,
      ocrError,
      currentTranslations,
      history,
      currentEntryId,
      clearOcr,
      recordOcrResult,
      setTranslationForMode,
      restoreHistoryEntry,
      removeHistoryEntry,
      clearHistory,
      exportHistory,
      exportError,
      exportSuccess,
      exportInProgress,
      clearExportFeedback,
      aiSettings,
      ttsSettings,
      playTts,
      ttsPlay,
      bubbleDetection,
      paragraphDetection,
    ],
  );

  return (
    <FrenchReaderContext.Provider value={value}>
      {children}
    </FrenchReaderContext.Provider>
  );
}

export function useFrenchReaderContext(): FrenchReaderContextValue {
  const ctx = useContext(FrenchReaderContext);
  if (!ctx) {
    throw new Error("useFrenchReaderContext must be used within FrenchReaderProvider");
  }
  return ctx;
}
