import {
  ToolType,
  type ToolOperationConfig,
} from "@app/hooks/tools/shared/toolOperationTypes";

/** Viewer-only tool — no batch PDF processing in M1. */
export const frenchReaderOperationConfig: ToolOperationConfig<
  Record<string, never>
> = {
  toolType: ToolType.custom,
  customProcessor: async () => ({ files: [] }),
};
