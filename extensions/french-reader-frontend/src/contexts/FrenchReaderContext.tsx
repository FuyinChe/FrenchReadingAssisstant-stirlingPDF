import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type {
  FrenchReaderSelection,
  OcrResult,
} from "@app/hooks/tools/frenchReader/types";

interface FrenchReaderContextValue {
  selection: FrenchReaderSelection | null;
  ocrResult: OcrResult | null;
  ocrLoading: boolean;
  ocrError: string | null;
  setSelection: (selection: FrenchReaderSelection | null) => void;
  setOcrResult: (result: OcrResult | null) => void;
  setOcrLoading: (loading: boolean) => void;
  setOcrError: (error: string | null) => void;
  clearOcr: () => void;
}

const FrenchReaderContext = createContext<FrenchReaderContextValue | null>(null);

export function FrenchReaderProvider({ children }: { children: ReactNode }) {
  const [selection, setSelection] = useState<FrenchReaderSelection | null>(
    null,
  );
  const [ocrResult, setOcrResult] = useState<OcrResult | null>(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState<string | null>(null);

  const clearOcr = useCallback(() => {
    setSelection(null);
    setOcrResult(null);
    setOcrError(null);
    setOcrLoading(false);
  }, []);

  const value = useMemo(
    () => ({
      selection,
      ocrResult,
      ocrLoading,
      ocrError,
      setSelection,
      setOcrResult,
      setOcrLoading,
      setOcrError,
      clearOcr,
    }),
    [selection, ocrResult, ocrLoading, ocrError, clearOcr],
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
