import { Box, Text } from "@mantine/core";
import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

/** Single newlines become paragraphs so vocabulary lines render separately. */
export function normalizeAiMarkdown(text: string): string {
  return text
    .split(/\r?\n/)
    .map((line) => line.trimEnd())
    .join("\n\n");
}

const markdownComponents: Components = {
  p: ({ children }) => (
    <Text
      component="p"
      size="sm"
      c="teal.9"
      m={0}
      mb={6}
      style={{ lineHeight: 1.55, wordBreak: "break-word" }}
    >
      {children}
    </Text>
  ),
  strong: ({ children }) => (
    <Text component="strong" span fw={700} c="teal.9">
      {children}
    </Text>
  ),
  em: ({ children }) => (
    <Text component="em" span fs="italic" c="teal.9">
      {children}
    </Text>
  ),
  ul: ({ children }) => (
    <Box component="ul" m={0} mb={6} pl="1.25rem" c="teal.9" fz="sm" style={{ lineHeight: 1.55 }}>
      {children}
    </Box>
  ),
  ol: ({ children }) => (
    <Box component="ol" m={0} mb={6} pl="1.25rem" c="teal.9" fz="sm" style={{ lineHeight: 1.55 }}>
      {children}
    </Box>
  ),
  li: ({ children }) => (
    <Box component="li" mb={4}>
      {children}
    </Box>
  ),
  code: ({ children }) => (
    <Text component="code" span ff="monospace" fz="sm" c="teal.9">
      {children}
    </Text>
  ),
};

interface AiMarkdownContentProps {
  text: string;
}

export function AiMarkdownContent({ text }: AiMarkdownContentProps) {
  if (!text.trim()) {
    return null;
  }

  return (
    <Box style={{ wordBreak: "break-word" }}>
      <ReactMarkdown components={markdownComponents}>
        {normalizeAiMarkdown(text)}
      </ReactMarkdown>
    </Box>
  );
}
