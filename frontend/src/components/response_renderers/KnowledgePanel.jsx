import React from 'react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { FaBookMedical, FaAppleAlt, FaRunning, FaBrain } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const PanelContainer = styled(motion.div)`
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
`;

const Title = styled.h3`
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid #e9ecef;
  margin-bottom: 15px;
  overflow-x: auto;
  scrollbar-width: none;
  
  &::-webkit-scrollbar {
    display: none;
  }
`;

const Tab = styled.button`
  padding: 10px 15px;
  background: none;
  border: none;
  font-size: 0.9rem;
  font-weight: ${props => props.active ? '600' : '400'};
  color: ${props => props.active ? '#0084ff' : '#7f8c8d'};
  border-bottom: ${props => props.active ? '2px solid #0084ff' : 'none'};
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    color: #0084ff;
  }
`;

const ContentSection = styled.div`
  color: #34495e;
  line-height: 1.6;
`;

const SubtopicTitle = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 15px 0 8px 0;
`;

const References = styled.div`
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #e9ecef;
  font-size: 0.8rem;
  color: #7f8c8d;
`;

const KnowledgePanel = ({ data }) => {
  const [activeTab, setActiveTab] = React.useState('');
  
  if (!data) return null;
  
  // Define all possible tabs and their icons
  const allTabs = [
    { id: 'general_health', label: 'General Health', icon: <FaBookMedical /> },
    { id: 'nutrition', label: 'Nutrition', icon: <FaAppleAlt /> },
    { id: 'fitness', label: 'Fitness', icon: <FaRunning /> },
    { id: 'mental_wellness', label: 'Mental Wellness', icon: <FaBrain /> }
  ];

  // Exclude keys that should be rendered by other, dedicated components
  const excludedKeys = new Set(['fitness_plan', 'diet_plan']);
  
  // Filter tabs to only show those that have content in the data and are not in the exclusion list
  const availableTabs = allTabs.filter(tab => data[tab.id] && !excludedKeys.has(tab.id));
  
  // Set the first available tab as active by default
  React.useEffect(() => {
    if (availableTabs.length > 0 && !availableTabs.some(t => t.id === activeTab)) {
      setActiveTab(availableTabs[0].id);
    }
  }, [data, activeTab, availableTabs]);
  
  // Get current content based on the active tab
  const currentContent = data[activeTab];
  
  // Handle different content formats (string or object)
  const renderContent = () => {
    if (!currentContent) return <p>No information available for this topic.</p>;
    
    if (typeof currentContent === 'string') {
      return <ReactMarkdown remarkPlugins={[remarkGfm]}>{currentContent}</ReactMarkdown>;
    }
    
    // Handle object format with title/content structure
    if (typeof currentContent === 'object') {
      return (
        <>
          {currentContent.title && <Title>{currentContent.title}</Title>}
          {currentContent.content && (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{currentContent.content}</ReactMarkdown>
          )}
          {currentContent.subtopics && currentContent.subtopics.length > 0 && (
            <>
              {currentContent.subtopics.map((subtopic, index) => (
                <div key={index}>
                  <SubtopicTitle>{subtopic.title}</SubtopicTitle>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{subtopic.content}</ReactMarkdown>
                </div>
              ))}
            </>
          )}
        </>
      );
    }
    
    return <p>Information format not supported.</p>;
  };
  
  if (availableTabs.length === 0) {
    return null; // Don't render the panel if there's no valid knowledge content to show
  }
  
  return (
    <PanelContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Title><FaBookMedical /> Health Knowledge</Title>
      
      {availableTabs.length > 1 && (
        <TabsContainer>
          {availableTabs.map(tab => (
            <Tab 
              key={tab.id}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon} {tab.label}
            </Tab>
          ))}
        </TabsContainer>
      )}
      
      <ContentSection>
        {renderContent()}
      </ContentSection>
      
      {data.references && data.references.length > 0 && (
        <References>
          <strong>References:</strong>
          <ul>
            {data.references.map((ref, index) => (
              <li key={index}>{ref}</li>
            ))}
          </ul>
        </References>
      )}
    </PanelContainer>
  );
};

export default KnowledgePanel; 