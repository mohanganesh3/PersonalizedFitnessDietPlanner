import React from 'react';
import GeneralNotesDisplay from './GeneralNotesDisplay';

const NotesExample = () => {
  // This is your raw, unformatted notes text from the backend
  const rawNotes = `General Notes
1. **Portion Control:** Use smaller plates, measure portions initially, and be mindful of serving sizes, especially for carbohydrates and fats.
2. **Evening Snacking:** If hunger strikes, opt for a small portion of non-starchy vegetables (like cucumber slices or celery sticks), a small handful of nuts (about 15-20 almonds), or a cup of herbal tea. Avoid chips and crackers.
3. **Carbohydrate Weakness:** Distribute carbohydrate intake throughout the day, focusing on complex, high-fiber sources. Pair carbohydrates with protein and healthy fats to slow digestion and manage blood sugar.
4. **Exercise:** Incorporate regular physical activity. Aim for at least 150 minutes of moderate-intensity aerobic exercise per week (e.g., brisk walking, stationary biking) and strength training 2-3 times per week. Start with your current routine and gradually increase duration and intensity.
5. **Blood Sugar Management:** Monitor blood glucose levels as advised by your doctor. Consistency in meal timing and composition is crucial.
6. **Medication:** Continue taking all prescribed medications as directed by your physician. This diet plan is designed to complement your medical treatment.
7. **Flexibility:** This is a template. Adjust meals based on availability and preference, ensuring you adhere to the principles of portion control, balanced macros, and nutrient-dense foods. Consult with a registered dietitian or your doctor before making significant changes to your diet or exercise routine.`;

  return (
    <div className="notes-example-container">
      <h2>Health Plan Details</h2>
      
      {/* The GeneralNotesDisplay component will properly format the notes */}
      <GeneralNotesDisplay notes={rawNotes} />
      
      {/* You can add other components here */}
      <div className="other-content">
        <h3>Additional Information</h3>
        <p>Your other content can go here...</p>
      </div>
    </div>
  );
};

export default NotesExample; 