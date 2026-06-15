import { useBaseParameters } from "@app/hooks/tools/shared/useBaseParameters";

export type FrenchReaderParameters = Record<string, never>;

export function useFrenchReaderParameters() {
  return useBaseParameters<FrenchReaderParameters>({
    defaultParameters: {},
    endpointName: "french-reader",
    validateFn: () => true,
  });
}
