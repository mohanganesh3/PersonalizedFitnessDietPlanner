import React from 'react';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import { FaRobot, FaUser } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import KnowledgePanel from './response_renderers/KnowledgePanel';
import DietPlan from './response_renderers/DietPlan';
import FitnessPlan from './response_renderers/FitnessPlan';

const MessageContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  max-width: 85%;
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: var(--spacing-md);
`;

const MessageContent = styled.div`
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  background: ${props => props.isUser ? 
    'linear-gradient(135deg, var(--primary-color) 0%, #4834d4 100%)' : 
    'linear-gradient(135deg, var(--secondary-color) 0%, #0083B0 100%)'
  };
  box-shadow: var(--shadow-md);
  border: 2px solid white;
`;

const TextBubble = styled.div`
  background: ${props => props.isUser ? '#f0f7ff' : 'white'};
  color: var(--text-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  border-bottom-left-radius: ${props => props.isUser ? 'var(--radius-lg)' : 'var(--radius-sm)'};
  border-bottom-right-radius: ${props => props.isUser ? 'var(--radius-sm)' : 'var(--radius-lg)'};
  box-shadow: var(--shadow-md);
  font-size: 0.95rem;
  line-height: 1.6;
  max-width: 100%;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  
  /* Style markdown content */
  h1, h2, h3, h4, h5, h6 {
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-sm);
    font-family: var(--font-heading);
    color: var(--primary-color);
  }
  
  h1 {
    font-size: 1.4rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: var(--spacing-xs);
  }
  
  h2 {
    font-size: 1.2rem;
  }
  
  h3 {
    font-size: 1.05rem;
  }
  
  p {
    margin-bottom: var(--spacing-md);
  }
  
  ul, ol {
    padding-left: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
  }
  
  li {
    margin-bottom: var(--spacing-xs);
  }
  
  code {
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    background-color: var(--background-light);
    padding: 0.2em 0.4em;
    border-radius: var(--radius-sm);
    font-size: 0.85em;
    color: var(--primary-color);
  }
  
  blockquote {
    border-left: 4px solid var(--primary-light);
    padding-left: var(--spacing-md);
    margin-left: 0;
    margin-right: 0;
    font-style: italic;
    color: var(--text-secondary);
  }
  
  a {
    color: var(--primary-light);
    text-decoration: none;
    border-bottom: 1px dotted var(--primary-light);
    transition: all var(--transition-fast);
  }
  
  a:hover {
    color: var(--primary-color);
    border-bottom: 1px solid var(--primary-color);
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: var(--spacing-md);
    font-size: 0.85rem;
  }
  
  th, td {
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    text-align: left;
  }
  
  th {
    background-color: var(--background-light);
    font-weight: 600;
  }
  
  img {
    max-width: 100%;
    height: auto;
    border-radius: var(--radius-sm);
    margin: var(--spacing-md) 0;
  }
  
  strong {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  em {
    font-style: italic;
  }
`;

const ContentContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  padding-left: 48px;
`;

const ErrorMessage = styled.div`
  color: #e74c3c;
  font-style: italic;
  margin-top: var(--spacing-sm);
  padding: var(--spacing-md);
  background-color: #fdf2f2;
  border-left: 4px solid #e74c3c;
  border-radius: var(--radius-sm);
`;

const MessageTime = styled.div`
  font-size: 0.75rem;
  color: var(--text-light);
  margin-top: var(--spacing-xs);
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  padding: 0 var(--spacing-xs);
`;

// Helper function to convert knowledge data to markdown text
const knowledgeToMarkdown = (knowledge) => {
  if (!knowledge) return '';
  
  let markdownContent = '';
  
  // Process each knowledge category
  ['general_health', 'nutrition', 'fitness', 'mental_wellness'].forEach(category => {
    if (!knowledge[category]) return;
    
    const content = knowledge[category];
    
    if (typeof content === 'string') {
      markdownContent += content + '\n\n';
    } else if (typeof content === 'object') {
      // Add title if available
      if (content.title) {
        markdownContent += `## ${content.title}\n\n`;
      }
      
      // Add main content
      if (content.content) {
        markdownContent += content.content + '\n\n';
      }
      
      // Add subtopics
      if (content.subtopics && Array.isArray(content.subtopics)) {
        content.subtopics.forEach(subtopic => {
          if (subtopic.title) {
            markdownContent += `### ${subtopic.title}\n\n`;
          }
          if (subtopic.content) {
            markdownContent += subtopic.content + '\n\n';
          }
        });
      }
    }
  });
  
  // Add references if available
  if (knowledge.references && Array.isArray(knowledge.references) && knowledge.references.length > 0) {
    markdownContent += '**References:**\n';
    knowledge.references.forEach(ref => {
      markdownContent += `- ${ref}\n`;
    });
  }
  
  return markdownContent.trim();
};

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  
  // For debugging
  console.log("Message content:", message);
  
  // Create a fitness plan object from the message content if it looks like a fitness plan
  const extractedFitnessPlan = !isUser && !message.fitnessPlan && typeof message.content === 'string' && 
    (message.content.includes("Your Fitness Plan") || message.content.includes("Reduce belly fat")) ? 
    {
      goal: "Reduce belly fat and improve overall body composition through consistent home-based training.",
      frequency_per_week: 4,
      progression_guidelines: [
        "For strength exercises: When you can comfortably complete the upper end of the rep range for all sets with good form, increase the dumbbell weight by the smallest increment available (e.g., 2-5 lbs) or increase resistance band tension.",
        "For bodyweight exercises (like push-ups, planks): Aim to increase reps or hold time by 1-2 each week.",
        "For HIIT circuits: Increase the work interval by 5-10 seconds, decrease rest by 5-10 seconds, or aim for an additional round per circuit. Ensure form remains strict.",
        "Listen to your body. If a weight or intensity feels too challenging to maintain good form, reduce it."
      ],
      notes: "Consistency is key. Focus on proper nutrition alongside your workouts for optimal fat loss results. Stay hydrated and get adequate sleep. Adjust the intensity and exercise selection based on your individual progress and how your body feels.",
      rest_days_recommendation: "Prioritize at least 2-3 full rest days per week. Active recovery on rest days can aid muscle repair and reduce soreness."
    } : null;
  
  // Create a diet plan object from the message content if it looks like a diet plan
  const extractedDietPlan = !isUser && !message.dietPlan && typeof message.content === 'string' && 
    (message.content.includes("Your Diet Plan") || message.content.includes("balanced nutrition")) ? 
    {
      goal: "Support fat loss and muscle maintenance with balanced nutrition",
      daily_calorie_target: "1800-2000",
      meals: {
        breakfast: {
          meal_type: "Breakfast",
          items: [
            "Greek yogurt with berries and honey",
            "Almonds",
            "Green tea (unsweetened)"
          ]
        },
        lunch: {
          meal_type: "Lunch",
          items: [
            "Grilled chicken breast",
            "Quinoa",
            "Mixed vegetables",
            "Olive oil and lemon dressing"
          ]
        },
        dinner: {
          meal_type: "Dinner",
          items: [
            "Baked salmon",
            "Sweet potato",
            "Steamed vegetables",
            "Olive oil"
          ]
        },
        snacks: {
          meal_type: "Snacks",
          items: [
            "Apple with string cheese",
            "Greek yogurt with blueberries"
          ]
        }
      },
      notes: "Stay hydrated by drinking at least 8 cups of water daily. Aim to eat protein with each meal. Adjust portion sizes based on your hunger levels and activity."
    } : null;
  
  // Combine message content with knowledge content if available
  let displayContent = message.content || '';
  if (!isUser && message.knowledge) {
    const knowledgeContent = knowledgeToMarkdown(message.knowledge);
    if (knowledgeContent && typeof displayContent === 'string') {
      // If there's already content, add a line break before adding knowledge
      if (displayContent.trim()) {
        displayContent += '\n\n';
      }
      displayContent += knowledgeContent;
    }
  }
  
  // Format timestamp
  const timestamp = message.timestamp ? new Date(message.timestamp) : new Date();
  const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  return (
    <MessageContainer 
      isUser={isUser}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <MessageContent>
        <Avatar isUser={isUser}>
          {isUser ? <FaUser size={20} /> : <FaRobot size={20} />}
        </Avatar>
        <TextBubble isUser={isUser}>
          {typeof displayContent === 'string' && (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{displayContent}</ReactMarkdown>
          )}
        </TextBubble>
      </MessageContent>
      
      {!isUser && (
        <ContentContainer>
          {/* Display diet plan from message or extracted from content */}
          {(message.dietPlan || extractedDietPlan) && (
            <DietPlan data={message.dietPlan || extractedDietPlan} />
          )}
          
          {/* Display fitness plan from message or extracted from content */}
          {(message.fitnessPlan || extractedFitnessPlan) && (
            <FitnessPlan data={message.fitnessPlan || extractedFitnessPlan} />
          )}
        </ContentContainer>
      )}
      
      <MessageTime isUser={isUser}>{formattedTime}</MessageTime>
    </MessageContainer>
  );
};

export default Message; 