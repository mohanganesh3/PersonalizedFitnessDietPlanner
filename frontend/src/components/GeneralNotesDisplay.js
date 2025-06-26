import React from 'react';
import { formatGeneralNotes, parseListToStructured } from '../utils/formatHelpers';
import './NoteFormatter.css';

/**
 * Component to display properly formatted general notes
 */
const GeneralNotesDisplay = ({ notes }) => {
  // First, format the raw notes text
  const formattedText = formatGeneralNotes(notes);
  
  // Then parse it into structured data
  const structuredNotes = parseListToStructured(formattedText);
  
  if (!structuredNotes.length) {
    return null;
  }
  
  return (
    <div className="notes-container">
      <h3>General Notes</h3>
      <div className="notes-content">
        {structuredNotes.map((note, index) => (
          <div key={index} className="note-point">
            {note.number && (
              <div className="note-number">{note.number}</div>
            )}
            <div className="note-text">
              {note.title && <strong>{note.title}: </strong>}
              {note.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeneralNotesDisplay; 