import { useState, type ReactNode } from "react";
import { ActionIcon, Box, CopyButton, Group, Tooltip } from "@mantine/core";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CloseIcon from "@mui/icons-material/Close";

interface CopyHoverPanelProps {
  copyValue: string;
  copyTooltip: string;
  copiedTooltip: string;
  onClear?: () => void;
  clearTooltip?: string;
  children: ReactNode;
}

export function CopyHoverPanel({
  copyValue,
  copyTooltip,
  copiedTooltip,
  onClear,
  clearTooltip,
  children,
}: CopyHoverPanelProps) {
  const [hovered, setHovered] = useState(false);
  const canCopy = copyValue.trim().length > 0;

  return (
    <Box
      pos="relative"
      pr={canCopy || onClear ? 28 : 0}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {(canCopy || onClear) && (
        <Group
          gap={2}
          wrap="nowrap"
          pos="absolute"
          top={0}
          right={0}
          style={{
            opacity: hovered ? 1 : 0.45,
            transition: "opacity 120ms ease",
            zIndex: 1,
          }}
        >
          {canCopy && (
            <CopyButton value={copyValue}>
              {({ copied, copy }) => (
                <Tooltip label={copied ? copiedTooltip : copyTooltip}>
                  <ActionIcon
                    variant="subtle"
                    size="sm"
                    color={copied ? "teal" : "gray"}
                    onClick={copy}
                    aria-label={copyTooltip}
                  >
                    <ContentCopyIcon sx={{ fontSize: 16 }} />
                  </ActionIcon>
                </Tooltip>
              )}
            </CopyButton>
          )}
          {onClear && (
            <Tooltip label={clearTooltip ?? "Clear"}>
              <ActionIcon
                variant="subtle"
                size="sm"
                color="gray"
                onClick={onClear}
                aria-label={clearTooltip ?? "Clear"}
              >
                <CloseIcon sx={{ fontSize: 16 }} />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      )}
      {children}
    </Box>
  );
}
