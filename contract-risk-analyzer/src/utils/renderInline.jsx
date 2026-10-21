/**
 * renderInline – converts **bold** markers in plain text to React <strong> nodes.
 * Strips any remaining lone asterisks. Never uses dangerouslySetInnerHTML.
 *
 * @param {string} text
 * @returns {React.ReactNode[]}
 */
export function renderInline(text) {
  if (!text) return null;
  // Split on **...**
  const parts = String(text).split(/\*\*(.+?)\*\*/g);
  return parts.map((part, i) => {
    // Even indices are plain text, odd indices are the captured bold content
    if (i % 2 === 1) {
      return <strong key={i}>{part.replace(/\*/g, "")}</strong>;
    }
    // Strip stray lone asterisks from plain segments
    const cleaned = part.replace(/\*/g, "");
    return cleaned || null;
  });
}
