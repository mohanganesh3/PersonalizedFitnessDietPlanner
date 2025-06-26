import React from 'react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { FaDumbbell, FaBullseye, FaCalendarAlt, FaInfoCircle, FaRunning } from 'react-icons/fa';

const PlanContainer = styled(motion.div)`
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  width: 100%;
`;

const Title = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-md) 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-heading);
  
  svg {
    color: var(--secondary-color);
  }
`;

const SectionDescription = styled.p`
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: 1.7;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  font-size: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-primary);
  
  svg {
    color: var(--primary-light);
  }
  
  strong {
    font-weight: 600;
  }
`;

const DayCard = styled.div`
  background-color: var(--background-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
`;

const DayHeader = styled.h4`
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-sm) 0;
  font-family: var(--font-heading);
  display: flex;
  align-items: center;
  
  &:after {
    content: "";
    display: block;
    height: 3px;
    width: 40px;
    background: var(--secondary-color);
    margin-left: var(--spacing-sm);
    border-radius: 2px;
  }
`;

const ExerciseTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  margin-bottom: var(--spacing-md);
  
  th, td {
    padding: var(--spacing-sm);
    text-align: left;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
  }
  
  th {
    color: var(--text-primary);
    font-weight: 600;
    background-color: rgba(0, 0, 0, 0.02);
  }
  
  td {
    color: var(--text-secondary);
  }
  
  tr:last-child td {
    border-bottom: none;
  }
  
  tr:hover td {
    background-color: rgba(0, 0, 0, 0.01);
  }
`;

const Notes = styled.p`
  font-style: italic;
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(0, 0, 0, 0.02);
  border-left: 3px solid var(--primary-light);
  border-radius: var(--radius-sm);
`;

const SubHeader = styled.h5`
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: var(--spacing-md) 0 var(--spacing-xs) 0;
  font-family: var(--font-heading);
`;

const BulletList = styled.ul`
  margin: 0 0 var(--spacing-md) var(--spacing-md);
  padding-left: var(--spacing-sm);
  list-style-position: outside;
  color: var(--text-secondary);
  font-size: 0.95rem;
  
  li {
    margin-bottom: var(--spacing-xs);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
`;

const ProgressionSection = styled.div`
  margin-top: var(--spacing-lg);
  background-color: rgba(66, 153, 225, 0.05);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  border: 1px solid rgba(66, 153, 225, 0.2);
`;

const ProgressionTitle = styled.h4`
  font-size: 1.1rem;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-sm) 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-heading);
  
  svg {
    color: var(--primary-light);
  }
`;

const getDayName = (dayString) => {
  // Extracts the day name from strings like 'Day 1 (e.g., Monday)'
  if (!dayString) return '';
  const match = dayString.match(/\(e\.g\.,\s*([^)]+)\)/i);
  if (match && match[1]) return match[1].trim();
  // fallback: if not found, just return the original string
  return dayString;
};

const FitnessPlan = ({ data }) => {
  if (!data) return null;

  console.log('FULL FITNESS PLAN DATA:', JSON.stringify(data, null, 2));

  // Handle both array and object formats for workout_schedule
  // The backend model has multiple fields that could contain the schedule data
  let scheduleToDisplay = null;
  
  // Check all possible fields that might contain the workout schedule
  const possibleScheduleFields = [
    'workout_schedule', 'schedule', 'structure', 'workout_structure', 
    'workout_details', 'workouts', 'weekly_schedule'
  ];
  
  // Find the first field that contains valid schedule data
  for (const field of possibleScheduleFields) {
    if (data[field]) {
      if (Array.isArray(data[field]) && data[field].length > 0) {
        scheduleToDisplay = data[field];
        console.log(`Using ${field} array directly`);
        break;
      } else if (typeof data[field] === 'object' && !Array.isArray(data[field])) {
        scheduleToDisplay = Object.keys(data[field]).map(dayKey => ({
          day: dayKey,
          ...data[field][dayKey],
        }));
        console.log(`Converted ${field} object to array`);
        break;
      }
    }
  }

  // Force schedule to be available if any schedule data exists
  const hasSchedule = Boolean(scheduleToDisplay && scheduleToDisplay.length > 0);
  
  // Debug logging
  console.log('Schedule Fields Found:', possibleScheduleFields.filter(field => data[field]));
  console.log('Schedule to Display:', scheduleToDisplay);
  console.log('Has Schedule:', hasSchedule);
  
  // If we have workout_schedule but scheduleToDisplay is null, try to fix it
  if (!scheduleToDisplay || scheduleToDisplay.length === 0) {
    // Use the raw workout_schedule as a last resort
    for (const field of possibleScheduleFields) {
      if (data[field]) {
        if (Array.isArray(data[field])) {
          scheduleToDisplay = [...data[field]];
          console.log(`EMERGENCY: Using ${field} array directly`);
          break;
        } else if (typeof data[field] === 'object') {
          scheduleToDisplay = [];
          for (const key in data[field]) {
            if (Object.prototype.hasOwnProperty.call(data[field], key)) {
              scheduleToDisplay.push({
                day: key,
                ...data[field][key]
              });
            }
          }
          console.log(`EMERGENCY: Converted ${field} object to array`);
          break;
        }
      }
    }
  }
  
  // Final check - ensure scheduleToDisplay is an array
  if (scheduleToDisplay && !Array.isArray(scheduleToDisplay)) {
    scheduleToDisplay = [scheduleToDisplay];
  }
  
  console.log('FINAL scheduleToDisplay:', scheduleToDisplay);
  console.log('FINAL hasSchedule:', Boolean(scheduleToDisplay && scheduleToDisplay.length > 0));

  return (
    <PlanContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Title><FaDumbbell /> Your Fitness Plan</Title>
      <InfoGrid>
        {data.goal && <InfoItem><FaBullseye /> <strong>Goal:</strong> {data.goal}</InfoItem>}
        {data.frequency_per_week && (
          <InfoItem><FaCalendarAlt /> <strong>Frequency:</strong> {data.frequency_per_week} times/week</InfoItem>
        )}
        {data.session_duration_minutes && (
          <InfoItem><FaCalendarAlt /> <strong>Session Duration:</strong> {data.session_duration_minutes} min</InfoItem>
        )}
        {data.duration_weeks && (
          <InfoItem><FaCalendarAlt /> <strong>Program Length:</strong> {data.duration_weeks} weeks</InfoItem>
        )}
      </InfoGrid>
      {data.description && <SectionDescription>{data.description}</SectionDescription>}

      {data.equipment_needed && Array.isArray(data.equipment_needed) && data.equipment_needed.length > 0 && (
        <>
          <SubHeader>Equipment Needed</SubHeader>
          <BulletList>
            {data.equipment_needed.map((item, i) => <li key={i}>{item}</li>)}
          </BulletList>
        </>
      )}

      {scheduleToDisplay && scheduleToDisplay.length > 0 ? (
        <>
          {scheduleToDisplay.map((day, index) => {
            if (!day) return null;
            const exercises = day.exercises || [];
            const warmUp = day.warm_up;
            const coolDown = day.cool_down;
            // Extract a clean day name for the header
            const dayName = getDayName(day.day) || `Day ${index + 1}`;
            return (
              <DayCard key={index}>
                <DayHeader>{dayName}</DayHeader>
                {day.focus && <div style={{marginBottom: '8px'}}><strong>Focus:</strong> {day.focus}</div>}
                {/* Warm-up */}
                {warmUp && (
                  <>
                    <SubHeader>Warm-up {warmUp.duration && `(${warmUp.duration})`}</SubHeader>
                    {Array.isArray(warmUp.exercises) ? (
                      <BulletList>
                        {warmUp.exercises.map((ex, i) => (
                          <li key={i}>
                            {ex.name}
                            {ex.duration && ` – ${ex.duration}`}
                            {ex.reps && ` – ${ex.reps}`}
                          </li>
                        ))}
                      </BulletList>
                    ) : (
                      <Notes>{typeof warmUp === 'string' ? warmUp : JSON.stringify(warmUp)}</Notes>
                    )}
                  </>
                )}
                {/* Main exercises */}
                {Array.isArray(exercises) && exercises.length > 0 && (
                  <>
                    <SubHeader>Main Workout</SubHeader>
                    <ExerciseTable>
                      <thead>
                        <tr>
                          <th>Exercise</th>
                          <th>Sets</th>
                          <th>Reps / Duration</th>
                          <th>Rest</th>
                          <th>Target Areas</th>
                        </tr>
                      </thead>
                      <tbody>
                        {exercises.map((ex, i) => (
                          <tr key={i}>
                            <td>
                              {ex.name}
                              {ex.notes && <Notes style={{ fontStyle: 'normal', marginTop: '5px', padding: 'var(--spacing-sm)', fontSize: '0.85rem' }}>{ex.notes}</Notes>}
                            </td>
                            <td>{ex.sets || '-'}</td>
                            <td>{ex.reps || ex.duration || '-'}</td>
                            <td>{ex.rest_seconds ? `${ex.rest_seconds}s` : (ex.rest || '-')}</td>
                            <td>{ex.target_areas ? ex.target_areas.join(', ') : '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </ExerciseTable>
                  </>
                )}
                {/* Circuit exercises */}
                {Array.isArray(day.circuit_exercises) && day.circuit_exercises.length > 0 && (
                  <>
                    <SubHeader>Circuit</SubHeader>
                    {day.notes && <Notes>{day.notes}</Notes>}
                    <BulletList>
                      {day.circuit_exercises.map((ex, i) => (
                        <li key={i}>
                          {ex.name}
                          {ex.target_areas && ` (${ex.target_areas.join(', ')})`}
                        </li>
                      ))}
                    </BulletList>
                  </>
                )}
                {/* Cool-down (handle string or object) */}
                {coolDown && (typeof coolDown === 'string' ? (
                  <>
                    <SubHeader>Cool-down</SubHeader>
                    <Notes>{coolDown}</Notes>
                  </>
                ) : coolDown.exercises && Array.isArray(coolDown.exercises) ? (
                  <>
                    <SubHeader>Cool-down {coolDown.duration && `(${coolDown.duration})`}</SubHeader>
                    <BulletList>
                      {coolDown.exercises.map((ex, i) => (
                        <li key={i}>
                          {ex.name}
                          {ex.duration && ` – ${ex.duration}`}
                        </li>
                      ))}
                    </BulletList>
                  </>
                ) : (
                  <>
                    <SubHeader>Cool-down</SubHeader>
                    <Notes>{typeof coolDown === 'object' ? JSON.stringify(coolDown) : coolDown}</Notes>
                  </>
                ))}
                {day.notes && <Notes>{day.notes}</Notes>}
              </DayCard>
            );
          })}
        </>
      ) : (
        <Notes>No detailed weekly schedule found in the plan data.</Notes>
      )}

      {/* Progression guidelines */}
      {data.progression_guidelines && Array.isArray(data.progression_guidelines) && (
        <ProgressionSection>
          <ProgressionTitle><FaRunning /> Progression Guidelines</ProgressionTitle>
          <BulletList>
            {data.progression_guidelines.map((guideline, i) => (
              <li key={i}>{guideline}</li>
            ))}
          </BulletList>
        </ProgressionSection>
      )}
      {data.rest_days_recommendation && (
        <Notes><FaInfoCircle /> <strong>Rest Days:</strong> {data.rest_days_recommendation}</Notes>
      )}
      {data.notes && <Notes>{data.notes}</Notes>}
    </PlanContainer>
  );
};

export default FitnessPlan; 