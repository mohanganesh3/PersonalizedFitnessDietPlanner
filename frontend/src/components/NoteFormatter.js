import React from 'react';
import './NoteFormatter.css';

/**
 * Component to properly format general notes with appropriate spacing and styling
 * @param {Object} props - Component props
 * @param {string} props.notes - The notes text to format
 */
const NoteFormatter = ({ notes }) => {
  // Parse numbered or bulleted lists
  const formatNotes = (text) => {
    if (!text) return [];
    
    // Split by numbered points (e.g., "1. Text")
    const pointRegex = /(\d+\.\s*\*\*[^:]+:\*\*|\d+\.\s*)/;
    const points = text.split(pointRegex).filter(Boolean);
    
    const formattedPoints = [];
    
    for (let i = 0; i < points.length; i += 2) {
      // If this is a point number/title and there's content after it
      if (i + 1 < points.length) {
        const pointLabel = points[i].trim();
        const pointContent = points[i + 1].trim();
        
        // Extract title if it exists (e.g., "**Portion Control:**")
        const titleMatch = pointLabel.match(/\d+\.\s*\*\*([^:]+):\*\*/);
        const title = titleMatch ? titleMatch[1] : null;
        
        formattedPoints.push({
          number: pointLabel.replace(/\*\*[^:]+:\*\*/, '').trim(),
          title: title,
          content: pointContent
        });
      } else {
        // Handle case where there's text without a number
        formattedPoints.push({
          content: points[i].trim()
        });
      }
    }
    
    return formattedPoints;
  };
  
  const formattedPoints = formatNotes(notes);
  
  return (
    <div className="notes-container">
      <h3>General Notes</h3>
      <div className="notes-content">
        {formattedPoints.map((point, index) => (
          <div key={index} className="note-point">
            {point.number && (
              <div className="note-number">{point.number}</div>
            )}
            <div className="note-text">
              {point.title && <strong>{point.title}: </strong>}
              {point.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NoteFormatter; 