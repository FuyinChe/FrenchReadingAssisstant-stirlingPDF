/** Plain text for clipboard from AI markdown output. */
export function stripMarkdownForCopy(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^[\-*•]\s+/gm, "")
    .trim();
}
