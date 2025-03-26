import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class TriageModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.severity_levels = ["Non-urgent", "Semi-urgent", "Urgent", "Critical"]
        
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
    
    def predict(self, symptoms, patient_age, patient_gender):
        features = self._prepare_features(symptoms, patient_age, patient_gender)
        
        # For now, use a rule-based approach since we don't have training data
        total_severity = sum(symptom.severity for symptom in symptoms)
        avg_severity = total_severity / len(symptoms)
        
        # Determine severity level based on average severity
        if avg_severity >= 4.5:
            severity_idx = 3  # Critical
        elif avg_severity >= 3.5:
            severity_idx = 2  # Urgent
        elif avg_severity >= 2.5:
            severity_idx = 1  # Semi-urgent
        else:
            severity_idx = 0  # Non-urgent
            
        # Calculate confidence score based on symptom consistency
        severity_variance = np.var([s.severity for s in symptoms])
        confidence_score = 1.0 - (severity_variance / 4.0)  # Normalize by max variance
        
        return {
            "severity_level": self.severity_levels[severity_idx],
            "confidence_score": float(confidence_score)
        }
    
    def get_recommended_actions(self, severity_level):
        actions = {
            "Critical": [
                "Immediate life support measures",
                "Prepare for emergency transport",
                "Alert receiving facility",
                "Continuous vital signs monitoring"
            ],
            "Urgent": [
                "Rapid assessment and stabilization",
                "Prepare for urgent transport",
                "Monitor vital signs every 5 minutes",
                "Establish IV access"
            ],
            "Semi-urgent": [
                "Comprehensive assessment",
                "Prepare for non-emergency transport",
                "Monitor vital signs every 15 minutes",
                "Provide comfort measures"
            ],
            "Non-urgent": [
                "Basic assessment",
                "Schedule routine transport",
                "Monitor vital signs every 30 minutes",
                "Provide basic care"
            ]
        }
        return actions.get(severity_level, [])
    
    def get_time_to_treatment(self, severity_level):
        times = {
            "Critical": "Immediate",
            "Urgent": "Within 10 minutes",
            "Semi-urgent": "Within 30 minutes",
            "Non-urgent": "Within 1 hour"
        }
        return times.get(severity_level, "Within 1 hour") 