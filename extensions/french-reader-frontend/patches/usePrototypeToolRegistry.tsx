import { useMemo } from "react";
import { type PrototypeToolRegistry } from "@app/data/toolsTaxonomy";
import { useFrenchReaderToolRegistry } from "@app/extensions/french-reader/useFrenchReaderToolRegistry";

/**
 * Prototype tool registry extension.
 * French Reader extension merges tools here when installed.
 * Upstream stub is overridden in src/prototypes/data/ for prototypes build.
 */

export function usePrototypeToolRegistry(): PrototypeToolRegistry {
  const frenchReaderTools = useFrenchReaderToolRegistry();
  return useMemo(
    () => ({ ...frenchReaderTools }) as PrototypeToolRegistry,
    [frenchReaderTools],
  );
}
