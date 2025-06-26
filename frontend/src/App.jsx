import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styled from '@emotion/styled';
import { FaRobot, FaTimes } from 'react-icons/fa';
import ChatWindow from './components/ChatWindow';
import { useChat } from './hooks/useChat';

const ChatbotContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
`;

const ChatButton = styled(motion.button)`
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4834d4 100%);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-fast);
  border: 3px solid rgba(255, 255, 255, 0.8);
  
  &:hover {
    transform: translateY(-2px);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  svg {
    filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.2));
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f4f7f6 100%);
`;

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { 
    messages, 
    isLoading, 
    sendMessage,
    clearChat
  } = useChat();

  return (
    <AppContainer>
      <ChatbotContainer>
        <AnimatePresence>
          {isChatOpen && (
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              onSendMessage={sendMessage}
              onClose={() => setIsChatOpen(false)}
              onClearChat={clearChat}
            />
          )}
        </AnimatePresence>
        
        <ChatButton
          onClick={() => setIsChatOpen(!isChatOpen)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={isChatOpen ? "Close chat" : "Open chat"}
        >
          {isChatOpen ? <FaTimes size={25} /> : <FaRobot size={30} />}
        </ChatButton>
      </ChatbotContainer>
    </AppContainer>
  );
}

export default App; 