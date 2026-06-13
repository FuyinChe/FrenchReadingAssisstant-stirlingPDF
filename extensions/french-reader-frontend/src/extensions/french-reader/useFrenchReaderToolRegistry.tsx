import { lazy, useMemo } from "react";
import { useTranslation } from "react-i18next";

import LocalIcon from "@app/components/shared/LocalIcon";
import {
  SubcategoryId,
  ToolCategoryId,
  type PrototypeToolRegistry,
} from "@app/data/toolsTaxonomy";
import { frenchReaderOperationConfig } from "@app/hooks/tools/frenchReader/useFrenchReaderOperation";
import { getSynonyms } from "@app/utils/toolSynonyms";

const ENABLED =
  import.meta.env.VITE_FRENCH_READER_ENABLED !== "false";

const FrenchReader = lazy(
  () => import("@app/tools/frenchReader/FrenchReader"),
);

export function useFrenchReaderToolRegistry(): PrototypeToolRegistry {
  const { t } = useTranslation();

  return useMemo(() => {
    if (!ENABLED) {
      return {} as PrototypeToolRegistry;
    }

    return {
      frenchReader: {
        icon: (
          <LocalIcon
            icon="translate-rounded"
            width="1.5rem"
            height="1.5rem"
          />
        ),
        name: t("home.frenchReader.title", "French Reader"),
        component: FrenchReader,
        description: t(
          "home.frenchReader.desc",
          "Select French text regions in PDFs for OCR, TTS, and AI assistance",
        ),
        categoryId: ToolCategoryId.ADVANCED_TOOLS,
        subcategoryId: SubcategoryId.DOCUMENT_REVIEW,
        maxFiles: 1,
        workbench: "viewer",
        endpoints: ["french-reader"],
        operationConfig: frenchReaderOperationConfig,
        automationSettings: null,
        supportsAutomate: false,
        synonyms: getSynonyms(t, "frenchReader"),
        versionStatus: "beta",
      },
    } as PrototypeToolRegistry;
  }, [t]);
}
