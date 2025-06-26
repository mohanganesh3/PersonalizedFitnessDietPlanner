import React, { useRef, useEffect } from 'react';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import Message from './Message';

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background-color: var(--background-main);
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 20px;
    border: 2px solid transparent;
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-sm);
  }
`;

const TypingIndicator = styled(motion.div)`
  align-self: flex-start;
  background: white;
  color: var(--text-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: var(--radius-sm);
  font-style: italic;
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 0.9rem;
  
  &:after {
    content: "";
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--primary-color);
    animation: dotPulse 1.5s infinite ease-in-out;
  }
  
  &:before {
    content: "";
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--primary-color);
    animation: dotPulse 1.5s infinite ease-in-out 0.5s;
  }
  
  @keyframes dotPulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.5); opacity: 0.5; }
    100% { transform: scale(1); opacity: 1; }
  }
`;

const EmptyStateMessage = styled.div`
  text-align: center;
  color: var(--text-light);
  margin: var(--spacing-xl) 0;
  font-style: italic;
  font-size: 1rem;
`;

const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <MessagesContainer>
      {messages.length === 0 && (
        <EmptyStateMessage>
          Ask me anything about health, fitness, or nutrition!
        </EmptyStateMessage>
      )}
      
      {messages.map((msg) => (
        <Message 
          key={msg.id} 
          message={msg} 
        />
      ))}
      
      {isLoading && (
        <TypingIndicator
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Thinking
        </TypingIndicator>
      )}
      
      <div ref={messagesEndRef} />
    </MessagesContainer>
  );
};

export default MessageList; 