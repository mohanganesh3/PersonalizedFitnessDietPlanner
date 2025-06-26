import React from 'react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { FaUtensils, FaBullseye, FaCalendarDay, FaClipboardList, FaWineGlassAlt, FaAppleAlt, FaBan } from 'react-icons/fa';

const PlanContainer = styled(motion.div)`
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
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

const MealCard = styled.div`
  background-color: var(--background-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
`;

const MealHeader = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-sm) 0;
  font-family: var(--font-heading);
  display: flex;
  align-items: center;
  
  &:after {
    content: "";
    display: block;
    height: 2px;
    width: 30px;
    background: var(--secondary-color);
    margin-left: var(--spacing-sm);
    border-radius: 2px;
  }
`;

const FoodList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 0 0 var(--spacing-sm) 0;
`;

const FoodItem = styled.li`
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
  display: flex;
  align-items: flex-start;
  
  &:before {
    content: "•";
    color: var(--secondary-color);
    font-weight: bold;
    margin-right: var(--spacing-xs);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const Notes = styled.p`
  font-style: italic;
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: var(--spacing-sm) 0 0 0;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(0, 0, 0, 0.02);
  border-left: 3px solid var(--primary-light);
  border-radius: var(--radius-sm);
`;

const DayWrapper = styled.div`
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--border-color);
`;

const DayTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 var(--spacing-md) 0;
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid var(--border-color);
  font-family: var(--font-heading);
`;

const SectionTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-heading);
  
  svg {
    color: var(--primary-light);
  }
`;

const BulletList = styled.ul`
  margin: 0 0 var(--spacing-md) var(--spacing-md);
  padding: 0;
  list-style-type: disc;
  color: var(--text-secondary);
  font-size: 0.95rem;
  
  li {
    margin-bottom: var(--spacing-xs);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
`;

const DietPlan = ({ data }) => {
  if (!data) return null;

  return (
    <PlanContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Title><FaUtensils /> Your Diet Plan</Title>
      <InfoGrid>
        <InfoItem><FaBullseye /> <strong>Goal:</strong> {data.goal}</InfoItem>
        {data.daily_calorie_target && (
          <InfoItem><FaCalendarDay /> <strong>Calories:</strong> {data.daily_calorie_target} / day</InfoItem>
        )}
      </InfoGrid>

      {(() => {
        if (!data.meals && !data.sample_daily_menu && !data.weekly_meal_plan && !data.weekly_menu) return null;
        // Determine source object (meals or sample_daily_menu)
        const mealsSource = data.meals || data.sample_daily_menu || data.meal_plan || data.weekly_meal_plan || data.weekly_menu;

        const isWeekly =
          mealsSource && typeof mealsSource === 'object' &&
          !Array.isArray(mealsSource) &&
          Object.keys(mealsSource).some(k => /monday|tuesday|wednesday|thursday|friday|saturday|sunday|day_?\d+/i.test(k));

        if (isWeekly) {
          // Render weekly plan
          return Object.entries(mealsSource).map(([day, dayMeals], dayIdx) => {
            // Build meal array for that day (reuse logic)
            let dayMealArr;
            if (Array.isArray(dayMeals)) {
              dayMealArr = dayMeals;
            } else {
              // If all values are strings, treat as {Breakfast: "Eggs", Lunch: "Chicken"}
              const allStrings = Object.values(dayMeals).every(v => typeof v === 'string');
              if (allStrings) {
                dayMealArr = Object.entries(dayMeals).map(([key, value]) => ({
                  meal_type: key.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase()),
                  items: [value],
                }));
              } else {
                dayMealArr = Object.entries(dayMeals).map(([key, value]) => {
                  const itemsArr = [];
                  if (Array.isArray(value)) {
                    itemsArr.push(...value.map((v) => {
                      if (typeof v === 'string') return v;
                      return `${v.item || v.food || JSON.stringify(v)}${v.quantity ? ` (${v.quantity})` : ''}${v.preparation ? ` – ${v.preparation}` : ''}`;
                    }));
                  } else {
                    const opts = value.items || value.options || value.foods || [];
                    if (Array.isArray(opts)) {
                      itemsArr.push(...opts.map((v) => {
                        if (typeof v === 'string') return v;
                        return `${v.item || v.food || JSON.stringify(v)}${v.quantity ? ` (${v.quantity})` : ''}${v.preparation ? ` – ${v.preparation}` : ''}`;
                      }));
                    }
                  }
                  const readableTitle = key.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase());
                  return { meal_type: value.name || readableTitle, items: itemsArr, notes: value.notes||value.note };
                });
              }
            }

            return (
              <DayWrapper key={dayIdx}>
                <DayTitle>{day.replace(/\b\w/g,l=>l.toUpperCase())}</DayTitle>
                {dayMealArr.map((meal, index) => (
                  <MealCard key={index}>
                    <MealHeader>{meal.meal_type || `Meal ${index+1}`}</MealHeader>
                    {Array.isArray(meal.items) && (
                      <FoodList>
                        {meal.items.map((item,i)=><FoodItem key={i}>{item}</FoodItem>)}
                      </FoodList>
                    )}
                    {meal.notes && <Notes>{meal.notes}</Notes>}
                  </MealCard>
                ))}
              </DayWrapper>
            );
          });
        }

        // Convert object-form to array of {title, items, notes}
        const mealArray = Array.isArray(mealsSource)
          ? mealsSource
          : Object.entries(mealsSource).map(([key, value]) => {
              // Support different nested formats
              const itemsArr = [];
              if (Array.isArray(value)) {
                itemsArr.push(...value.map((v) => {
                  if (typeof v === 'string') return v;
                  return `${v.item || v.food || JSON.stringify(v)}${v.quantity ? ` (${v.quantity})` : ''}${v.preparation ? ` – ${v.preparation}` : ''}`;
                }));
              } else {
                // value could be object with items/options/food list
                const opts = value.items || value.options || value.foods || [];
                if (Array.isArray(opts)) {
                  itemsArr.push(...opts.map((v) => {
                    if (typeof v === 'string') return v;
                    return `${v.item || v.food || JSON.stringify(v)}${v.quantity ? ` (${v.quantity})` : ''}${v.preparation ? ` – ${v.preparation}` : ''}`;
                  }));
                }
              }

              // Build readable title from key or value.name
              const readableKey = key
                .replace(/meal_\d+_?/, '') // remove meal_1_ prefix etc
                .replace(/_/g, ' ')
                .replace(/\b\w/g, (l) => l.toUpperCase());
              const title = value.name || readableKey;

              return {
                meal_type: title,
                items: itemsArr,
                notes: value.notes || value.note,
                preparation_notes: value.preparation || value.preparation_notes,
              };
            });

        return mealArray.map((meal, index) => {
          const title = meal.meal_type || meal.meal_time || meal.type || `Meal ${index + 1}`;
          const items = meal.food_items || meal.items || meal.options || [];
          return (
            <MealCard key={index}>
              <MealHeader>{title}</MealHeader>
              {Array.isArray(items) && (
                <FoodList>
                  {items.map((item, i) => <FoodItem key={i}>{typeof item === 'string' ? item : item.item || JSON.stringify(item)}</FoodItem>)}
                </FoodList>
              )}
              {meal.preparation_notes && <Notes>{meal.preparation_notes}</Notes>}
              {meal.notes && <Notes>{meal.notes}</Notes>}
            </MealCard>
          );
        });
      })()}

      {data.notes && (
        <>
          <SectionTitle><FaClipboardList/> General Notes</SectionTitle>
          <Notes style={{ fontStyle: 'normal' }}>{data.notes}</Notes>
        </>
      )}

      {/* Additional sections */}
      {data.description && <Notes style={{ marginTop: 'var(--spacing-md)' }}>Description: {data.description}</Notes>}
      {data.hydration && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <SectionTitle><FaWineGlassAlt /> Hydration</SectionTitle>
          <Notes style={{ fontStyle: 'normal' }}>{typeof data.hydration === 'string' ? data.hydration : data.hydration.recommendation}</Notes>
        </div>
      )}
      {data.foods_to_emphasize && Array.isArray(data.foods_to_emphasize) && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <SectionTitle><FaAppleAlt /> Foods to Emphasize</SectionTitle>
          <FoodList>
            {data.foods_to_emphasize.map((f, i) => <FoodItem key={i}>{f}</FoodItem>)}
          </FoodList>
        </div>
      )}
      {data.foods_to_limit && Array.isArray(data.foods_to_limit) && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <SectionTitle><FaBan /> Foods to Limit</SectionTitle>
          <FoodList>
            {data.foods_to_limit.map((f, i) => <FoodItem key={i}>{f}</FoodItem>)}
          </FoodList>
        </div>
      )}
      
      {data.daily_structure && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <SectionTitle><FaCalendarDay /> Daily Structure</SectionTitle>
          {data.daily_structure.meals_per_day && <Notes style={{ fontStyle: 'normal' }}>Meals per day: {data.daily_structure.meals_per_day}</Notes>}
          {data.daily_structure.meal_timing && <Notes style={{ fontStyle: 'normal' }}>Meal timing: {data.daily_structure.meal_timing}</Notes>}
          {data.daily_structure.timing && <Notes style={{ fontStyle: 'normal' }}>{data.daily_structure.timing}</Notes>}
          {/* hydration could be string or object */}
          {data.daily_structure.hydration && (
            <Notes style={{ fontStyle: 'normal' }}>
              Hydration: {typeof data.daily_structure.hydration === 'string' ? data.daily_structure.hydration : `${data.daily_structure.hydration.target_liters_per_day || ''} L/day`}
            </Notes>
          )}
        </div>
      )}

      {data.general_recommendations && Array.isArray(data.general_recommendations) && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          <SectionTitle><FaClipboardList /> General Recommendations</SectionTitle>
          <BulletList>
            {data.general_recommendations.map((rec,i)=><li key={i}>{rec}</li>)}
          </BulletList>
        </div>
      )}
    </PlanContainer>
  );
};

export default DietPlan; 