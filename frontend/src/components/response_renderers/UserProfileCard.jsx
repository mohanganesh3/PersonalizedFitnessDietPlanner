import React from 'react';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import { FaUser, FaWeight, FaRulerVertical, FaRunning, FaUtensils, FaExclamationTriangle } from 'react-icons/fa';

const ProfileContainer = styled(motion.div)`
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
`;

const Title = styled.h3`
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const ProfileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
`;

const ProfileItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const ItemLabel = styled.div`
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const ItemValue = styled.div`
  font-size: 0.95rem;
  color: #34495e;
  font-weight: 500;
`;

const ListContainer = styled.div`
  margin-top: 10px;
`;

const ListTitle = styled.div`
  font-size: 0.9rem;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const ListItems = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-left: 24px;
`;

const ListItem = styled.div`
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #495057;
`;

const EmptyProfile = styled.div`
  color: #7f8c8d;
  font-style: italic;
  text-align: center;
  padding: 20px;
`;

const UserProfileCard = ({ profile }) => {
  if (!profile || Object.keys(profile).length === 0) {
    return (
      <ProfileContainer
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <EmptyProfile>
          No profile information available yet. Your profile will be built as you chat.
        </EmptyProfile>
      </ProfileContainer>
    );
  }

  // Calculate BMI if height and weight are available
  let bmi = null;
  if (profile.weight_lbs && profile.height_inches && profile.height_inches > 0) {
    bmi = ((profile.weight_lbs * 703) / (profile.height_inches * profile.height_inches)).toFixed(1);
  }

  // Format height to feet and inches
  const formatHeight = (inches) => {
    if (!inches) return null;
    const feet = Math.floor(inches / 12);
    const remainingInches = Math.round(inches % 12);
    return `${feet}'${remainingInches}"`;
  };

  return (
    <ProfileContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Title><FaUser /> Your Profile</Title>
      
      <ProfileGrid>
        {profile.age && (
          <ProfileItem>
            <ItemLabel><FaUser /> Age</ItemLabel>
            <ItemValue>{profile.age} years</ItemValue>
          </ProfileItem>
        )}
        
        {profile.weight_lbs && (
          <ProfileItem>
            <ItemLabel><FaWeight /> Weight</ItemLabel>
            <ItemValue>{profile.weight_lbs} lbs</ItemValue>
          </ProfileItem>
        )}
        
        {profile.height_inches && (
          <ProfileItem>
            <ItemLabel><FaRulerVertical /> Height</ItemLabel>
            <ItemValue>{formatHeight(profile.height_inches)}</ItemValue>
          </ProfileItem>
        )}
        
        {bmi && (
          <ProfileItem>
            <ItemLabel>BMI</ItemLabel>
            <ItemValue>{bmi}</ItemValue>
          </ProfileItem>
        )}
        
        {profile.activity_level && (
          <ProfileItem>
            <ItemLabel><FaRunning /> Activity Level</ItemLabel>
            <ItemValue>{profile.activity_level}</ItemValue>
          </ProfileItem>
        )}
        
        {profile.fitness_level && (
          <ProfileItem>
            <ItemLabel>Fitness Level</ItemLabel>
            <ItemValue>{profile.fitness_level}</ItemValue>
          </ProfileItem>
        )}
      </ProfileGrid>
      
      {profile.fitness_goals && profile.fitness_goals.length > 0 && (
        <ListContainer>
          <ListTitle><FaRunning /> Fitness Goals</ListTitle>
          <ListItems>
            {profile.fitness_goals.map((goal, index) => (
              <ListItem key={index}>{goal}</ListItem>
            ))}
          </ListItems>
        </ListContainer>
      )}
      
      {profile.dietary_preferences && profile.dietary_preferences.length > 0 && (
        <ListContainer>
          <ListTitle><FaUtensils /> Dietary Preferences</ListTitle>
          <ListItems>
            {profile.dietary_preferences.map((pref, index) => (
              <ListItem key={index}>{pref}</ListItem>
            ))}
          </ListItems>
        </ListContainer>
      )}
      
      {profile.dietary_restrictions && profile.dietary_restrictions.length > 0 && (
        <ListContainer>
          <ListTitle><FaExclamationTriangle /> Dietary Restrictions</ListTitle>
          <ListItems>
            {profile.dietary_restrictions.map((restriction, index) => (
              <ListItem key={index}>{restriction}</ListItem>
            ))}
          </ListItems>
        </ListContainer>
      )}
      
      {profile.health_conditions && profile.health_conditions.length > 0 && (
        <ListContainer>
          <ListTitle><FaExclamationTriangle /> Health Conditions</ListTitle>
          <ListItems>
            {profile.health_conditions.map((condition, index) => (
              <ListItem key={index}>{condition}</ListItem>
            ))}
          </ListItems>
        </ListContainer>
      )}
    </ProfileContainer>
  );
};

export default UserProfileCard; 