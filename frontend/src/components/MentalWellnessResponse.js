import React from 'react';
import ReactMarkdown from 'react-markdown';
import './MentalWellnessResponse.css';

/**
 * Component to properly format mental wellness responses
 * @param {Object} props - Component props
 * @param {string} props.response - The mental wellness response text
 */
const MentalWellnessResponse = ({ response }) => {
  if (!response) return null;
  
  return (
    <div className="mental-wellness-container">
      <div className="mental-wellness-content">
        <ReactMarkdown 
          children={response}
          components={{
            // Custom rendering for headers
            h1: ({ node, ...props }) => <h2 className="wellness-heading" {...props} />,
            h2: ({ node, ...props }) => <h3 className="wellness-heading" {...props} />,
            h3: ({ node, ...props }) => <h4 className="wellness-heading" {...props} />,
            
            // Custom rendering for lists
            ol: ({ node, ...props }) => <ol className="wellness-ordered-list" {...props} />,
            ul: ({ node, ...props }) => <ul className="wellness-unordered-list" {...props} />,
            li: ({ node, ...props }) => <li className="wellness-list-item" {...props} />,
            
            // Custom rendering for paragraphs
            p: ({ node, ...props }) => <p className="wellness-paragraph" {...props} />,
            
            // Custom rendering for bold text (technique names)
            strong: ({ node, ...props }) => <strong className="wellness-technique-name" {...props} />
          }}
        />
      </div>
    </div>
  );
};

export default MentalWellnessResponse; 