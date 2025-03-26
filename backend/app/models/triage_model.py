import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TriageModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.severity_levels = ["Non-urgent", "Semi-urgent", "Urgent", "Critical"]
        self.symptom_categories = {
            'vital_signs': ['Heart Rate', 'Blood Pressure', 'Temperature', 'Oxygen Saturation'],
            'neurological': ['Unconsciousness', 'Confusion', 'Seizure', 'Stroke Symptoms'],
            'respiratory': ['Difficulty Breathing', 'Chest Pain', 'Cough', 'Wheezing'],
            'cardiovascular': ['Chest Pain', 'Heart Attack', 'Cardiac Arrest', 'Irregular Heartbeat'],
            'trauma': ['Bleeding', 'Fracture', 'Burn', 'Head Injury'],
            'gastrointestinal': ['Abdominal Pain', 'Nausea', 'Vomiting', 'Diarrhea'],
            'allergic': ['Allergic Reaction', 'Anaphylaxis', 'Swelling', 'Rash'],
            'mental_health': ['Anxiety', 'Panic Attack', 'Depression', 'Suicidal Thoughts']
        }
        self.symptom_correlations = {
            'chest_pain': ['difficulty_breathing', 'heart_attack', 'anxiety'],
            'difficulty_breathing': ['chest_pain', 'asthma', 'allergic_reaction'],
            'head_injury': ['unconsciousness', 'confusion', 'nausea'],
            'abdominal_pain': ['nausea', 'vomiting', 'fever']
        }
        self.risk_factors = {
            'age': {
                'infant': {'weight': 1.5, 'conditions': ['dehydration', 'fever']},
                'elderly': {'weight': 1.3, 'conditions': ['falls', 'medication_interactions']},
                'pregnant': {'weight': 1.4, 'conditions': ['pregnancy_complications']}
            },
            'medical_history': {
                'diabetes': {'weight': 1.2, 'conditions': ['diabetic_emergency']},
                'heart_disease': {'weight': 1.3, 'conditions': ['heart_attack', 'cardiac_arrest']},
                'asthma': {'weight': 1.2, 'conditions': ['asthma_attack']}
            }
        }
        self.common_injury_causes = {
            'accidents': [
                'car accident', 'motor vehicle accident', 'mva', 'road accident',
                'fall', 'slip and fall', 'trip and fall', 'falling down',
                'sports injury', 'athletic injury', 'sports accident',
                'workplace accident', 'industrial accident', 'work injury',
                'bicycle accident', 'motorcycle accident', 'pedestrian accident',
                'burn', 'scald', 'chemical burn', 'electrical burn',
                'drowning', 'near drowning', 'water accident',
                'poisoning', 'overdose', 'drug overdose', 'chemical exposure',
                'assault', 'physical assault', 'violence', 'fight',
                'gunshot', 'stabbing', 'penetrating injury',
                'animal bite', 'dog bite', 'insect bite', 'snake bite',
                'natural disaster', 'earthquake', 'flood', 'storm',
                'explosion', 'blast injury', 'fire',
                'crush injury', 'trauma', 'blunt force trauma'
            ],
            'medical_conditions': [
                'heart attack', 'myocardial infarction', 'cardiac arrest',
                'stroke', 'cerebrovascular accident', 'brain attack',
                'diabetic emergency', 'hypoglycemia', 'hyperglycemia',
                'seizure', 'epileptic seizure', 'convulsion',
                'allergic reaction', 'anaphylaxis', 'allergy',
                'asthma attack', 'breathing difficulty', 'respiratory distress',
                'infection', 'bacterial infection', 'viral infection',
                'pregnancy complication', 'labor', 'delivery',
                'mental health crisis', 'psychiatric emergency',
                'overdose', 'drug overdose', 'substance abuse'
            ]
        }
        
    def _prepare_features(self, symptoms, patient_age, patient_gender):
        # Convert gender to numeric
        gender_map = {"male": 0, "female": 1, "other": 2}
        gender_encoded = gender_map.get(patient_gender.lower(), 2)
        
        # Create feature vector
        features = [patient_age, gender_encoded]
        
        # Add symptom severities
        symptom_severities = [0] * 5  # Initialize with zeros for 5 possible symptoms
        for i, symptom in enumerate(symptoms[:5]):  # Take up to 5 symptoms
            symptom_severities[i] = symptom.severity
            
        features.extend(symptom_severities)
        return np.array(features).reshape(1, -1)
    
    def validate_injury_cause(self, cause: str) -> Dict[str, Any]:
        """
        Validate and categorize the injury cause.
        Returns a dictionary with validation results and suggestions.
        """
        if not cause:
            return {
                'is_valid': False,
                'message': 'Please describe what happened.',
                'suggestions': ['Tell us what happened', 'What caused the injury or illness?']
            }

        cause = cause.lower().strip()
        
        # Check if the cause is too short
        if len(cause) < 3:
            return {
                'is_valid': False,
                'message': 'Please provide more details about what happened.',
                'suggestions': ['Tell us more about what happened', 'What caused the injury or illness?']
            }

        # Check for common injury causes with fuzzy matching
        found_causes = []
        for category, causes in self.common_injury_causes.items():
            for valid_cause in causes:
                # Check if any word from the valid cause is in the user's input
                valid_words = valid_cause.split()
                if any(word in cause for word in valid_words):
                    found_causes.append(valid_cause)

        if not found_causes:
            # If no exact matches found, try to categorize based on keywords
            keywords = {
                'accidents': ['accident', 'fell', 'fall', 'hit', 'struck', 'crash', 'collision', 'burn', 'cut', 'wound'],
                'medical_conditions': ['pain', 'ache', 'fever', 'sick', 'illness', 'infection', 'attack', 'seizure', 'allergy']
            }
            
            matched_category = None
            for category, words in keywords.items():
                if any(word in cause for word in words):
                    matched_category = category
                    break

            if matched_category:
                return {
                    'is_valid': True,
                    'message': 'Valid cause of injury/illness identified.',
                    'causes': [cause],
                    'category': matched_category
                }

            # If no category matches, check for invalid or nonsensical input
            invalid_patterns = [
                r'^[0-9]+$',  # Just numbers
                r'^[a-z]{1,2}$',  # Single or double letters
                r'^[^a-z0-9\s]+$',  # No letters or numbers
                r'^test|testing|asdf|qwerty|123|abc$',  # Common test inputs
            ]
            
            import re
            if any(re.match(pattern, cause) for pattern in invalid_patterns):
                return {
                    'is_valid': False,
                    'message': 'Please provide a meaningful description of what happened.',
                    'suggestions': [
                        'Describe the injury or illness',
                        'What caused the problem?',
                        'How did it happen?'
                    ]
                }

            # If we get here, the input is reasonable but not matching our categories
            return {
                'is_valid': True,
                'message': 'Cause of injury/illness recorded.',
                'causes': [cause],
                'category': 'other'
            }

        return {
            'is_valid': True,
            'message': 'Valid cause of injury/illness identified.',
            'causes': found_causes,
            'category': 'accidents' if any(cause in self.common_injury_causes['accidents'] for cause in found_causes) else 'medical_conditions'
        }
    
    def analyze_symptom_patterns(self, symptoms, patient_age, patient_gender):
        """Analyze symptom patterns and correlations"""
        patterns = {
            'category_distribution': {},
            'correlated_symptoms': [],
            'risk_factors': [],
            'progression_indicators': []
        }
        
        # Analyze symptom categories
        for symptom in symptoms:
            for category, category_symptoms in self.symptom_categories.items():
                if symptom.name in category_symptoms:
                    patterns['category_distribution'][category] = patterns['category_distribution'].get(category, 0) + 1
        
        # Find correlated symptoms
        for symptom in symptoms:
            symptom_key = symptom.name.lower().replace(' ', '_')
            if symptom_key in self.symptom_correlations:
                patterns['correlated_symptoms'].extend(self.symptom_correlations[symptom_key])
        
        # Analyze risk factors
        if patient_age < 1:
            patterns['risk_factors'].append(('age', 'infant'))
        elif patient_age > 65:
            patterns['risk_factors'].append(('age', 'elderly'))
        
        return patterns
    
    def predict(self, symptoms, patient_age, patient_gender):
        features = self._prepare_features(symptoms, patient_age, patient_gender)
        
        # Calculate total severity and average severity
        total_severity = sum(s.severity for s in symptoms)
        avg_severity = total_severity / len(symptoms)
        
        # Analyze symptom patterns
        patterns = self.analyze_symptom_patterns(symptoms, patient_age, patient_gender)
        
        # Calculate severity adjustments based on patterns
        pattern_adjustment = 1.0
        if len(patterns['correlated_symptoms']) > 0:
            pattern_adjustment *= 1.2  # Increase severity for correlated symptoms
        
        # Apply risk factor adjustments
        risk_adjustment = 1.0
        for risk_type, risk_value in patterns['risk_factors']:
            if risk_type in self.risk_factors:
                risk_adjustment *= self.risk_factors[risk_type][risk_value]['weight']
        
        # Calculate final severity
        adjusted_severity = avg_severity * pattern_adjustment * risk_adjustment
        
        # Determine severity level
        if adjusted_severity >= 4.5 or any(s.severity == 5 for s in symptoms):
            severity_idx = 3  # Critical
        elif adjusted_severity >= 3.5 or (adjusted_severity >= 3.0 and len(symptoms) >= 2):
            severity_idx = 2  # Urgent
        elif adjusted_severity >= 2.5 or (adjusted_severity >= 2.0 and len(symptoms) >= 2):
            severity_idx = 1  # Semi-urgent
        else:
            severity_idx = 0  # Non-urgent
        
        # Calculate confidence score
        severity_variance = np.var([s.severity for s in symptoms])
        base_confidence = 1.0 - (severity_variance / 4.0)
        symptom_count_factor = min(len(symptoms) / 3.0, 1.0)
        pattern_confidence = len(patterns['correlated_symptoms']) / 5.0 if patterns['correlated_symptoms'] else 0.5
        confidence_score = base_confidence * (0.6 + 0.2 * symptom_count_factor + 0.2 * pattern_confidence)
        
        return {
            "severity_level": self.severity_levels[severity_idx],
            "confidence_score": float(confidence_score),
            "recommended_actions": [
                "Call emergency services immediately" if severity_idx == 3 else
                "Seek immediate medical attention" if severity_idx == 2 else
                "Seek medical attention within 2 hours" if severity_idx == 1 else
                "Monitor symptoms and seek care if needed"
            ],
            "estimated_time_to_treatment": (
                "Immediate (within 15 minutes)" if severity_idx == 3 else
                "Urgent (within 30 minutes)" if severity_idx == 2 else
                "Semi-urgent (within 2 hours)" if severity_idx == 1 else
                "Non-urgent (within 24 hours)"
            ),
            "factors": {
                "average_severity": float(avg_severity),
                "pattern_adjustment": float(pattern_adjustment),
                "risk_adjustment": float(risk_adjustment),
                "final_severity": float(adjusted_severity),
                "patterns": patterns
            }
        }
    
    def get_recommended_actions(self, severity_level, patient_age=None, patterns=None):
        base_actions = {
            "Critical": [
                "Immediate life support measures",
                "Prepare for emergency transport",
                "Alert receiving facility",
                "Continuous vital signs monitoring",
                "Establish IV access",
                "Prepare emergency medications",
                "Document all interventions"
            ],
            "Urgent": [
                "Rapid assessment and stabilization",
                "Prepare for urgent transport",
                "Monitor vital signs every 5 minutes",
                "Establish IV access",
                "Administer oxygen if needed",
                "Prepare emergency medications",
                "Document all interventions"
            ],
            "Semi-urgent": [
                "Comprehensive assessment",
                "Prepare for non-emergency transport",
                "Monitor vital signs every 15 minutes",
                "Administer medications as needed",
                "Provide comfort measures",
                "Document all interventions"
            ],
            "Non-urgent": [
                "Complete assessment",
                "Schedule follow-up care",
                "Provide self-care instructions",
                "Monitor for changes",
                "Document assessment"
            ]
        }
        
        actions = base_actions.get(severity_level, [])
        
        # Add pattern-specific actions
        if patterns:
            for category, count in patterns['category_distribution'].items():
                if count >= 2:  # Multiple symptoms in same category
                    actions.append(f"Focus on {category} assessment and monitoring")
            
            for risk_type, risk_value in patterns['risk_factors']:
                if risk_type in self.risk_factors:
                    risk_info = self.risk_factors[risk_type][risk_value]
                    for condition in risk_info['conditions']:
                        actions.append(f"Monitor for {condition.replace('_', ' ')}")
        
        # Add age-specific recommendations
        if patient_age is not None:
            if patient_age < 5:
                actions.append("Ensure pediatric equipment is available")
                actions.append("Monitor for signs of dehydration")
            elif patient_age > 65:
                actions.append("Monitor for signs of confusion")
                actions.append("Check for medication interactions")
            elif patient_age < 18:
                actions.append("Ensure parent/guardian is informed")
                actions.append("Use age-appropriate equipment")
        
        return actions
    
    def get_time_to_treatment(self, severity_level, patient_age=None):
        base_times = {
            "Critical": "Immediate (within 5 minutes)",
            "Urgent": "Within 15 minutes",
            "Semi-urgent": "Within 30 minutes",
            "Non-urgent": "Within 2 hours"
        }
        
        time = base_times.get(severity_level, "As soon as possible")
        
        # Adjust time based on age
        if patient_age is not None:
            if patient_age < 5 or patient_age > 65:
                if severity_level in ["Semi-urgent", "Non-urgent"]:
                    time = "Within 15 minutes"  # Faster for vulnerable populations
            elif patient_age < 18:
                if severity_level == "Non-urgent":
                    time = "Within 1 hour"  # Slightly faster for children
        
        return time 