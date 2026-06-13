import type { ToolOperationConfig } from "@app/hooks/tools/shared/toolOperationTypes";
import { ToolType } from "@app/hooks/tools/shared/toolOperationTypes";

/** M0 placeholder — custom operation wired in M1. */
export const frenchReaderOperationConfig: ToolOperationConfig<Record<string, never>> = {
  toolType: ToolType.custom,
  customProcessor: async () => {
    throw new Error("French Reader operation not implemented yet (M1).");
  },
};
