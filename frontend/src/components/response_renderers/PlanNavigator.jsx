import React, { useState } from 'react';
import styled from '@emotion/styled';
import { FaBullseye, FaClipboardList, FaDumbbell, FaUtensils, FaList, FaArrowLeft } from 'react-icons/fa';
import DietPlan from './DietPlan';
import FitnessPlan from './FitnessPlan';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const Card = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
`;

const Title = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const SummaryList = styled.ul`
  margin: 0 0 15px 18px;
  padding: 0;
  list-style-type: disc;
  font-size: 0.9rem;
  color: #7f8c8d;
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const NavButton = styled.button`
  background: #0084ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  &:hover {
    opacity: 0.9;
  }
`;

const PlanNavigator = ({ dietPlan, fitnessPlan }) => {
  const [view, setView] = useState('overview'); // 'overview' | 'diet' | 'fitness' | 'quick'

  const mealsPerDay = dietPlan?.daily_structure?.meals_per_day || 5;
  const hasWeeklyFitness = fitnessPlan?.weekly_schedule && (Array.isArray(fitnessPlan.weekly_schedule) ? fitnessPlan.weekly_schedule.length : Object.keys(fitnessPlan.weekly_schedule || {}).length);

  // Quick derived summary for quick overview view
  const dietSummary = `Detailed Diet Plan (${mealsPerDay} meals/day)`;
  const fitnessSummary = `Weekly Fitness Schedule (${hasWeeklyFitness || 0} days)`;

  const renderOverview = () => (
    <Card>
      <Title><FaBullseye/> Belly Fat Reduction Plan</Title>
      <p style={{ fontSize: '0.95rem', marginTop: 0 }}>I've created a comprehensive plan with:</p>
      <SummaryList>
        <li>📋 {dietSummary}</li>
        <li>💪 {fitnessSummary}</li>
        <li>📊 Sample meals & workout circuits</li>
      </SummaryList>
      <p style={{ fontSize: '0.9rem' }}>Would you like to see:</p>
      <ButtonGroup>
        {dietPlan && <NavButton onClick={()=>setView('diet')}><FaUtensils/> Diet Plan First</NavButton>}
        {fitnessPlan && <NavButton onClick={()=>setView('fitness')}><FaDumbbell/> Fitness Plan First</NavButton>}
        {dietPlan && fitnessPlan && <NavButton onClick={()=>setView('quick')}><FaList/> Quick Overview</NavButton>}
      </ButtonGroup>
    </Card>
  );

  const renderQuick = () => (
    <Card>
      <Title><FaClipboardList/> Quick Overview</Title>
      {dietPlan && (
        <>
          <p><strong>Diet:</strong> {dietSummary}</p>
        </>
      )}
      {fitnessPlan && (
        <>
          <p><strong>Fitness:</strong> {fitnessSummary}</p>
        </>
      )}
      <ButtonGroup style={{ marginTop: '10px' }}>
        {dietPlan && <NavButton onClick={()=>setView('diet')}><FaUtensils/> Diet Details</NavButton>}
        {fitnessPlan && <NavButton onClick={()=>setView('fitness')}><FaDumbbell/> Fitness Details</NavButton>}
        <NavButton onClick={()=>setView('overview')}><FaArrowLeft/> Back</NavButton>
      </ButtonGroup>
    </Card>
  );

  const renderDiet = () => (
    <>
      <DietPlan data={dietPlan} />
      <ButtonGroup>
        {fitnessPlan && <NavButton onClick={()=>setView('fitness')}><FaDumbbell/> Switch to Fitness</NavButton>}
        <NavButton onClick={()=>setView('overview')}><FaArrowLeft/> Back to Overview</NavButton>
      </ButtonGroup>
    </>
  );

  const renderFitness = () => (
    <>
      <FitnessPlan data={fitnessPlan} />
      <ButtonGroup>
        {dietPlan && <NavButton onClick={()=>setView('diet')}><FaUtensils/> Switch to Diet</NavButton>}
        <NavButton onClick={()=>setView('overview')}><FaArrowLeft/> Back to Overview</NavButton>
      </ButtonGroup>
    </>
  );

  return (
    <Container>
      {view === 'overview' && renderOverview()}
      {view === 'quick' && renderQuick()}
      {view === 'diet' && renderDiet()}
      {view === 'fitness' && renderFitness()}
    </Container>
  );
};

export default PlanNavigator; 