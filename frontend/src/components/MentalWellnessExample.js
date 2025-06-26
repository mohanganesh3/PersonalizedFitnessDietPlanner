import React from 'react';
import MentalWellnessResponse from './MentalWellnessResponse';
import ChatMessage from './ChatMessage';

const MentalWellnessExample = () => {
  // Example mental wellness response with proper markdown formatting
  const exampleResponse = `
I understand how stressful studying can be, especially during exam periods. Taking short breaks for stress relief exercises can make a significant difference in your focus and wellbeing.

**Deep Breathing Exercise (4-7-8 Technique)**
This simple breathing pattern helps activate your parasympathetic nervous system, reducing stress quickly.
1. Sit comfortably with your back straight
2. Inhale quietly through your nose for 4 seconds
3. Hold your breath for 7 seconds
4. Exhale completely through your mouth for 8 seconds
5. Repeat 3-5 times
Duration: 2-3 minutes
Benefits: Reduces anxiety, improves focus, and helps regulate emotional responses

**Progressive Muscle Relaxation**
This technique helps release physical tension that accumulates during studying.
1. Start with your feet and focus on that muscle group
2. Tense the muscles tightly for 5 seconds
3. Release and relax for 10 seconds, noticing the difference
4. Move upward through each muscle group to your face
Duration: 5-10 minutes
Benefits: Releases physical tension, increases body awareness, and promotes mental relaxation

**Quick Mindfulness Break**
This grounding exercise brings you back to the present moment.
1. Pause and take a deep breath
2. Notice 5 things you can see around you
3. Acknowledge 4 things you can touch or feel
4. Listen for 3 things you can hear
5. Identify 2 things you can smell
6. Notice 1 thing you can taste
Duration: 2-3 minutes
Benefits: Reduces rumination, improves present-moment awareness, and resets mental focus

Remember that even short breaks using these techniques can significantly improve your study effectiveness and mental wellbeing.
  `;

  return (
    <div className="mental-wellness-example">
      <h2>Mental Wellness Response Example</h2>
      
      {/* Example of user query */}
      <ChatMessage 
        message="I am very stressed due to studies, can you suggest some relief exercises?" 
        isUser={true} 
        timestamp="10:30 AM" 
      />
      
      {/* Example of mental wellness response */}
      <ChatMessage 
        message={exampleResponse} 
        isUser={false} 
        timestamp="10:31 AM" 
      />
      
      <div className="example-explanation">
        <h3>About This Component</h3>
        <p>The mental wellness response above is rendered using the MentalWellnessResponse component, 
        which properly formats markdown content with appropriate styling for:</p>
        <ul>
          <li>Technique names in bold</li>
          <li>Numbered instructions</li>
          <li>Proper spacing between sections</li>
          <li>Responsive design for different screen sizes</li>
        </ul>
      </div>
    </div>
  );
};

export default MentalWellnessExample; 