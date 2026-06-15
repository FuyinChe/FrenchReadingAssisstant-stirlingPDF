/**
 * Prototype tool ID definitions.
 * French Reader extension adds frenchReader when installed.
 */

export const PROTOTYPE_REGULAR_TOOL_IDS = ["frenchReader"] as const;
export const PROTOTYPE_SUPER_TOOL_IDS = [] as const;
export const PROTOTYPE_LINK_TOOL_IDS = [] as const;

export type PrototypeRegularToolId =
  (typeof PROTOTYPE_REGULAR_TOOL_IDS)[number];
export type PrototypeSuperToolId = (typeof PROTOTYPE_SUPER_TOOL_IDS)[number];
export type PrototypeLinkToolId = (typeof PROTOTYPE_LINK_TOOL_IDS)[number];
export type PrototypeToolId =
  | PrototypeRegularToolId
  | PrototypeSuperToolId
  | PrototypeLinkToolId;
