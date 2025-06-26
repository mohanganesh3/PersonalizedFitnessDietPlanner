import React, { useState, useRef, useEffect } from 'react';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import { FaPaperPlane } from 'react-icons/fa';

const InputContainer = styled.div`
  display: flex;
  padding: var(--spacing-md) var(--spacing-md);
  background-color: white;
  border-top: 1px solid var(--border-color);
  align-items: center;
  position: relative;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.03);
`;

const TextArea = styled.textarea`
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-sm) calc(var(--spacing-lg) + 35px) var(--spacing-sm) var(--spacing-md);
  font-size: 0.95rem;
  line-height: 1.5;
  resize: none;
  height: 48px;
  max-height: 140px;
  outline: none;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
  color: var(--text-primary);
  background-color: var(--background-light);
  
  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(44, 82, 130, 0.2);
    background-color: white;
  }
  
  &::placeholder {
    color: var(--text-light);
  }
`;

const SendButton = styled(motion.button)`
  position: absolute;
  right: calc(var(--spacing-md) + 8px);
  bottom: calc(var(--spacing-md) + 6px);
  background: linear-gradient(135deg, var(--primary-color) 0%, #4834d4 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  &:disabled {
    background: var(--text-light);
    cursor: not-allowed;
    opacity: 0.7;
  }
`;

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 140);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  return (
    <InputContainer>
      <TextArea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={isLoading}
      />
      <SendButton
        onClick={handleSubmit}
        disabled={!message.trim() || isLoading}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Send message"
      >
        <FaPaperPlane size={14} />
      </SendButton>
    </InputContainer>
  );
};

export default ChatInput; 