import React from 'react';
import './ChatMessage.css';
import MentalWellnessResponse from './MentalWellnessResponse';

// Helper function to detect mental wellness content
const isMentalWellnessResponse = (text) => {
  if (!text) return false;
  
  // Check for common mental wellness keywords and formatting patterns
  const mentalWellnessPatterns = [
    /\*\*Deep Breathing Exercise\*\*/i,
    /\*\*Progressive Muscle Relaxation\*\*/i,
    /\*\*Quick Mindfulness Break\*\*/i,
    /\*\*Meditation\*\*/i,
    /stress relief/i,
    /anxiety management/i,
    /mindfulness/i
  ];
  
  return mentalWellnessPatterns.some(pattern => pattern.test(text));
};

const ChatMessage = ({ message, isUser, timestamp }) => {
  const messageClass = isUser ? 'user-message' : 'assistant-message';
  
  // Check if this is a mental wellness response
  const isMentalWellness = !isUser && isMentalWellnessResponse(message);
  
  return (
    <div className={`chat-message ${messageClass}`}>
      <div className="message-content">
        {isUser ? (
          <p>{message}</p>
        ) : (
          isMentalWellness ? (
            <MentalWellnessResponse response={message} />
          ) : (
            <p>{message}</p>
          )
        )}
      </div>
      <div className="message-timestamp">{timestamp}</div>
    </div>
  );
};

export default ChatMessage; 