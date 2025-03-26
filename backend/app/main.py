from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from sqlalchemy.orm import Session
from models.triage_model import TriageModel
from models.database import get_db, Patient, Assessment
from utils.logging import logger
from utils.health import router as health_router
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import logging
import models

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('triage_ai')

app = FastAPI(
    title="TriageAI API",
    description="AI-powered triage assistant for emergency responders",
    version="1.0.0"
)

# Initialize the triage model
triage_model = TriageModel()

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include health check routes
app.include_router(health_router, prefix="/api/v1", tags=["health"])

# Data models
class Symptom(BaseModel):
    name: str
    severity: int  # 1-5 scale
    description: Optional[str] = None

class TriageRequest(BaseModel):
    symptoms: List[Symptom]
    patient_age: int
    patient_gender: str
    mechanism_of_injury: str
    location: Optional[Dict[str, float]] = None

class TriageResponse(BaseModel):
    severity_level: str  # Critical, Urgent, Semi-urgent, Non-urgent
    recommended_actions: List[str]
    estimated_time_to_treatment: str
    confidence_score: float
    assessment_factors: dict

class AssessmentHistory(BaseModel):
    id: int
    patient_age: int
    patient_gender: str
    severity_level: str
    created_at: datetime
    symptoms: List[dict]

@app.get("/")
async def root():
    return {"message": "Welcome to TriageAI API"}

@app.get("/triage/symptoms")
async def get_common_symptoms():
    try:
        symptoms = [
            # Critical Symptoms
            {"name": "Unconsciousness", "severity": 5, "description": "Patient is unresponsive or not alert"},
            {"name": "Severe Bleeding", "severity": 5, "description": "Uncontrolled or significant bleeding"},
            {"name": "Chest Pain", "severity": 5, "description": "Severe chest pain or pressure, especially with shortness of breath"},
            {"name": "Difficulty Breathing", "severity": 5, "description": "Severe shortness of breath or respiratory distress"},
            {"name": "Stroke Symptoms", "severity": 5, "description": "Sudden weakness, numbness, speech difficulty, or facial drooping"},
            {"name": "Cardiac Arrest", "severity": 5, "description": "No pulse or breathing"},
            {"name": "Severe Burns", "severity": 5, "description": "Large or deep burns, especially on face, hands, or genitals"},
            {"name": "Severe Allergic Reaction", "severity": 5, "description": "Anaphylaxis with breathing difficulty or swelling"},
            {"name": "Severe Head Injury", "severity": 5, "description": "Head trauma with loss of consciousness or confusion"},
            {"name": "Multiple Injuries", "severity": 5, "description": "Multiple significant injuries from trauma"},

            # Urgent Symptoms
            {"name": "Moderate Bleeding", "severity": 4, "description": "Controlled but significant bleeding"},
            {"name": "Severe Pain", "severity": 4, "description": "Intense pain in any part of the body"},
            {"name": "Severe Abdominal Pain", "severity": 4, "description": "Intense abdominal pain with nausea or vomiting"},
            {"name": "Moderate Burns", "severity": 4, "description": "Moderate burns on body parts"},
            {"name": "Moderate Allergic Reaction", "severity": 4, "description": "Significant allergic reaction with swelling or rash"},
            {"name": "Moderate Head Injury", "severity": 4, "description": "Head injury with confusion or memory loss"},
            {"name": "Severe Dehydration", "severity": 4, "description": "Significant dehydration with dizziness or confusion"},
            {"name": "Severe Nausea/Vomiting", "severity": 4, "description": "Persistent vomiting with dehydration risk"},
            {"name": "Severe Dizziness", "severity": 4, "description": "Severe dizziness with difficulty standing"},
            {"name": "Severe Anxiety/Panic", "severity": 4, "description": "Severe anxiety with physical symptoms"},

            # Semi-urgent Symptoms
            {"name": "Mild Bleeding", "severity": 3, "description": "Minor bleeding that can be controlled"},
            {"name": "Moderate Pain", "severity": 3, "description": "Significant but manageable pain"},
            {"name": "Moderate Abdominal Pain", "severity": 3, "description": "Significant abdominal discomfort"},
            {"name": "Mild Burns", "severity": 3, "description": "Minor burns or sunburns"},
            {"name": "Mild Allergic Reaction", "severity": 3, "description": "Minor allergic reaction with rash"},
            {"name": "Mild Head Injury", "severity": 3, "description": "Minor head injury without loss of consciousness"},
            {"name": "Moderate Dehydration", "severity": 3, "description": "Significant thirst with mild dizziness"},
            {"name": "Moderate Nausea", "severity": 3, "description": "Persistent nausea without severe vomiting"},
            {"name": "Moderate Dizziness", "severity": 3, "description": "Significant dizziness but can stand"},
            {"name": "Moderate Anxiety", "severity": 3, "description": "Significant anxiety with some physical symptoms"},

            # Non-urgent Symptoms
            {"name": "Minor Pain", "severity": 2, "description": "Mild pain that doesn't interfere with daily activities"},
            {"name": "Minor Cuts/Scrapes", "severity": 2, "description": "Small cuts or scrapes that can be cleaned at home"},
            {"name": "Mild Fever", "severity": 2, "description": "Low-grade fever without other severe symptoms"},
            {"name": "Mild Cough", "severity": 2, "description": "Minor cough without breathing difficulty"},
            {"name": "Mild Rash", "severity": 2, "description": "Minor skin irritation or rash"},
            {"name": "Mild Headache", "severity": 2, "description": "Minor headache without other symptoms"},
            {"name": "Mild Dehydration", "severity": 2, "description": "Slight thirst without dizziness"},
            {"name": "Mild Nausea", "severity": 2, "description": "Slight nausea without vomiting"},
            {"name": "Mild Dizziness", "severity": 2, "description": "Slight dizziness without falling risk"},
            {"name": "Mild Anxiety", "severity": 2, "description": "Minor anxiety without physical symptoms"}
        ]
        logger.info("Successfully retrieved symptoms list")
        return {"symptoms": symptoms}
    except Exception as e:
        logger.error(f"Error retrieving symptoms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage/validate-cause")
async def validate_injury_cause(request: Dict[str, str]):
    """Validate the cause of injury/illness"""
    try:
        cause = request.get("cause", "")
        validation_result = triage_model.validate_injury_cause(cause)
        return validation_result
    except Exception as e:
        logger.error(f"Error validating cause: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate cause")

@app.post("/triage/assess")
async def assess_triage(request: TriageRequest, db: Session = Depends(get_db)):
    """Perform a comprehensive triage assessment"""
    try:
        logger.info(f"Processing triage assessment for patient age {request.patient_age}")
        
        # Get base assessment
        assessment = triage_model.predict(
            request.symptoms,
            request.patient_age,
            request.patient_gender
        )
        
        # Add location-based recommendations if available
        if request.location:
            location_recommendations = get_location_recommendations(request.location)
            assessment["location_recommendations"] = location_recommendations
        
        # Create patient first
        patient = Patient(
            age=request.patient_age,
            gender=request.patient_gender
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        # Save assessment to database
        db_assessment = Assessment(
            patient_id=patient.id,
            mechanism_of_injury=request.mechanism_of_injury,
            symptoms=json.dumps([s.dict() for s in request.symptoms]),
            severity_level=assessment["severity_level"],
            recommended_actions=json.dumps(assessment["recommended_actions"]),
            estimated_time_to_treatment=assessment["estimated_time_to_treatment"],
            confidence_score=int(assessment["confidence_score"] * 100),
            created_at=datetime.utcnow()
        )
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        
        logger.info(f"Assessment saved to database with severity level: {assessment['severity_level']}")
        return assessment
    except Exception as e:
        logger.error(f"Error processing assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process assessment")

def get_location_recommendations(location: Dict[str, float]) -> Dict[str, Any]:
    """Get location-based recommendations"""
    recommendations = {
        "nearest_hospitals": [],
        "estimated_travel_time": None,
        "transport_recommendations": []
    }
    
    # In a real implementation, this would integrate with a mapping service
    # to find nearby hospitals and calculate travel times
    recommendations["nearest_hospitals"] = [
        {"name": "City Hospital", "distance": "2.5 km", "travel_time": "5 minutes"},
        {"name": "Medical Center", "distance": "3.8 km", "travel_time": "8 minutes"}
    ]
    
    recommendations["transport_recommendations"] = [
        "Consider ambulance transport for critical cases",
        "Ensure patient is properly secured during transport",
        "Have emergency contact information readily available"
    ]
    
    return recommendations

@app.get("/triage/history", response_model=List[AssessmentHistory])
async def get_assessment_history(db: Session = Depends(get_db)):
    try:
        assessments = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(10).all()
        return [
            AssessmentHistory(
                id=assessment.id,
                patient_age=assessment.patient.age,
                patient_gender=assessment.patient.gender,
                severity_level=assessment.severity_level,
                created_at=assessment.created_at,
                symptoms=assessment.symptoms
            )
            for assessment in assessments
        ]
    except Exception as e:
        logger.error(f"Error fetching assessment history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 