import { useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import { createToolFlow } from "@app/components/tools/shared/createToolFlow";
import { useAllFiles } from "@app/contexts/FileContext";
import {
  useNavigationActions,
  useNavigationState,
} from "@app/contexts/NavigationContext";
import { useViewer } from "@app/contexts/ViewerContext";
import { useToolWorkflow } from "@app/contexts/ToolWorkflowContext";
import { useViewScopedFiles } from "@app/hooks/tools/shared/useViewScopedFiles";
import { useFrenchReaderPageState } from "@app/hooks/tools/frenchReader/useFrenchReaderPageState";
import { AiSidePanel } from "@app/components/frenchReader/AiSidePanel";
import { FrenchReaderRegionPortal } from "@app/components/frenchReader/FrenchReaderRegionPortal";
import { FrenchReaderProvider } from "@app/contexts/FrenchReaderContext";
import type { BaseToolProps } from "@app/types/tool";

const EMPTY_OPERATION = {
  files: [],
  thumbnails: [],
  isGeneratingThumbnails: false,
  downloadUrl: null,
  downloadFilename: "",
  isLoading: false,
  status: "",
  errorMessage: null,
  progress: null,
  executeOperation: async () => {},
  resetResults: () => {},
  clearError: () => {},
  cancelOperation: () => {},
  undoOperation: async () => {},
};

function FrenchReaderInner(_props: BaseToolProps) {
  const { t } = useTranslation();
  const { files: allFiles } = useAllFiles();
  const scopedFiles = useViewScopedFiles();
  const { workbench, selectedTool } = useNavigationState();
  const { actions: navActions } = useNavigationActions();
  const { setSidebarsVisible } = useToolWorkflow();
  const { setActiveFileIndex } = useViewer();
  const pageState = useFrenchReaderPageState();
  const openedViewer = useRef(false);

  const activeFile = scopedFiles[0] ?? allFiles[0] ?? null;
  const hasFiles = allFiles.length > 0;
  const isFrenchReaderActive =
    selectedTool === "frenchReader" && workbench === "viewer";

  useEffect(() => {
    if (!hasFiles || selectedTool !== "frenchReader") {
      openedViewer.current = false;
      return;
    }

    if (!openedViewer.current) {
      if (allFiles.length === 1) {
        setActiveFileIndex(0);
      }
      navActions.setWorkbench("viewer");
      setSidebarsVisible(true);
      openedViewer.current = true;
    }
  }, [
    hasFiles,
    selectedTool,
    allFiles.length,
    navActions,
    setSidebarsVisible,
    setActiveFileIndex,
  ]);

  const steps = useMemo(() => {
    if (!hasFiles || !isFrenchReaderActive) {
      return [];
    }

    return [
      {
        title: t("frenchReader.panel.title", "Reading assistant"),
        isCollapsed: false,
        content: <AiSidePanel activeFile={activeFile} currentPage={pageState.currentPage} />,
      },
    ];
  }, [hasFiles, isFrenchReaderActive, activeFile, pageState.currentPage, t]);

  return (
    <>
      {isFrenchReaderActive && (
        <FrenchReaderRegionPortal
          pageNumber={pageState.currentPage}
          pageIndex={Math.max(0, pageState.currentPage - 1)}
        />
      )}
      {createToolFlow({
        title: {
          title: t("frenchReader.title", "French Reading Assistant"),
          description: t(
            "frenchReader.subtitle",
            "Read French PDFs with OCR and TTS assistance",
          ),
        },
        files: {
          selectedFiles: activeFile ? [activeFile] : [],
          isVisible: false,
          minFiles: 1,
        },
        steps,
        review: {
          isVisible: false,
          operation: EMPTY_OPERATION,
          title: "",
          onFileClick: () => {},
        },
      })}
    </>
  );
}

export default function FrenchReader(props: BaseToolProps) {
  return (
    <FrenchReaderProvider>
      <FrenchReaderInner {...props} />
    </FrenchReaderProvider>
  );
}
