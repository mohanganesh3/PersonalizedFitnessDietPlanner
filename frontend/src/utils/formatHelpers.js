/**
 * Formats general notes text by adding proper markdown formatting
 * @param {string} notesText - The raw notes text
 * @returns {string} Formatted notes text with proper markdown
 */
export const formatGeneralNotes = (notesText) => {
  if (!notesText) return '';
  
  // First, ensure each numbered point is on a new line
  let formatted = notesText.replace(/(\d+\.\s*)/g, '\n$1');
  
  // Remove any extra newlines at the beginning
  formatted = formatted.trimStart();
  
  // Add bold formatting to titles if they exist
  formatted = formatted.replace(/(\d+\.\s*)([^:]+):/g, '$1**$2:**');
  
  // Ensure proper spacing between points
  formatted = formatted.replace(/\n(\d+\.)/g, '\n\n$1');
  
  return formatted;
};

/**
 * Converts a plain text list into an array of structured items
 * @param {string} listText - The text containing a list
 * @returns {Array} Array of list items with number and content properties
 */
export const parseListToStructured = (listText) => {
  if (!listText) return [];
  
  const lines = listText.split('\n').filter(line => line.trim());
  const result = [];
  
  lines.forEach(line => {
    // Check if this is a numbered point
    const match = line.match(/^(\d+\.\s*)(.+)$/);
    if (match) {
      // Extract title if it exists
      const contentMatch = match[2].match(/^\*\*([^:]+):\*\*\s*(.+)$/);
      if (contentMatch) {
        result.push({
          number: match[1].trim(),
          title: contentMatch[1],
          content: contentMatch[2].trim()
        });
      } else {
        result.push({
          number: match[1].trim(),
          content: match[2].trim()
        });
      }
    } else {
      // Handle non-numbered lines
      result.push({
        content: line.trim()
      });
    }
  });
  
  return result;
}; 