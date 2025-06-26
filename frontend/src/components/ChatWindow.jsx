import React from 'react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { FaTimes, FaTrash, FaRobot } from 'react-icons/fa';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

const ChatContainer = styled(motion.div)`
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 60vw;
  max-width: 800px;
  height: 80vh;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
  border: 1px solid var(--border-color);

  @media (max-width: 768px) {
    width: 85vw;
    height: 85vh;
    bottom: 80px;
  }
`;

const Header = styled.div`
  background: linear-gradient(135deg, var(--primary-color) 0%, #4834d4 100%);
  color: white;
  padding: var(--spacing-md) var(--spacing-lg);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.2rem;
  box-shadow: var(--shadow-sm);
  font-family: var(--font-heading);
  letter-spacing: 0.01em;
`;

const HeaderTitle = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  
  svg {
    color: var(--secondary-color);
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs);
  border-radius: 50%;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-right: var(--spacing-sm);
  transition: all var(--transition-fast);
  font-family: var(--font-body);
  font-weight: 500;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  align-items: center;
`;

const ChatWindow = ({ messages, isLoading, onSendMessage, onClose, onClearChat }) => {
  return (
    <ChatContainer
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.3 }}
    >
      <Header>
        <HeaderTitle>
          <FaRobot size={22} />
          AI Health & Fitness Assistant
        </HeaderTitle>
        <ButtonContainer>
          <ActionButton onClick={onClearChat} style={{ background: 'rgba(255, 100, 100, 0.2)' }}>
            <FaTrash /> Clear Chat
          </ActionButton>
          <CloseButton onClick={onClose}>
            <FaTimes size={20} />
          </CloseButton>
        </ButtonContainer>
      </Header>
      
      <>
        <MessageList 
          messages={messages} 
          isLoading={isLoading} 
        />
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </>
    </ChatContainer>
  );
};

export default ChatWindow; 