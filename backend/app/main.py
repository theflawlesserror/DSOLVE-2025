from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from sqlalchemy.orm import Session
from .models.triage_model import TriageModel
from .models.database import get_db, Patient, Assessment
from .utils.logging import logger
from .utils.health import router as health_router
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    mechanism_of_injury: Optional[str] = None

class TriageResponse(BaseModel):
    severity_level: str  # Critical, Urgent, Semi-urgent, Non-urgent
    recommended_actions: List[str]
    estimated_time_to_treatment: str
    confidence_score: float

class AssessmentHistory(BaseModel):
    id: int
    patient_age: int
    patient_gender: str
    severity_level: str
    created_at: datetime
    symptoms: List[dict]

class CauseValidationRequest(BaseModel):
    cause: str

@app.get("/")
async def root():
    return {"message": "Welcome to TriageAI API"}

@app.get("/triage/symptoms")
async def get_common_symptoms():
    try:
        symptoms = [
            {"name": "Chest Pain", "severity": 5, "description": "Severe chest pain or pressure"},
            {"name": "Difficulty Breathing", "severity": 4, "description": "Shortness of breath or respiratory distress"},
            {"name": "Unconsciousness", "severity": 5, "description": "Patient is unresponsive"},
            {"name": "Severe Bleeding", "severity": 4, "description": "Uncontrolled bleeding"},
            {"name": "Head Injury", "severity": 3, "description": "Trauma to the head"},
            {"name": "Abdominal Pain", "severity": 3, "description": "Severe abdominal pain"},
            {"name": "Burns", "severity": 4, "description": "Significant burns"},
            {"name": "Fracture", "severity": 3, "description": "Broken bone or suspected fracture"},
            {"name": "Allergic Reaction", "severity": 4, "description": "Severe allergic reaction"},
            {"name": "Stroke Symptoms", "severity": 5, "description": "Sudden weakness, numbness, or speech difficulty"}
        ]
        logger.info("Successfully retrieved symptoms list")
        return {"symptoms": symptoms}
    except Exception as e:
        logger.error(f"Error retrieving symptoms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage/validate-cause")
async def validate_injury_cause(request: CauseValidationRequest):
    try:
        validation_result = triage_model.validate_injury_cause(request.cause)
        return validation_result
    except Exception as e:
        logger.error(f"Error validating injury cause: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage/assess", response_model=TriageResponse)
async def assess_triage(request: TriageRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Processing triage assessment for patient age {request.patient_age}")
        
        # Validate injury cause first
        cause_validation = triage_model.validate_injury_cause(request.mechanism_of_injury)
        if not cause_validation['is_valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    'message': cause_validation['message'],
                    'suggestions': cause_validation['suggestions']
                }
            )
        
        # Get prediction from the model
        prediction = triage_model.predict(
            request.symptoms,
            request.patient_age,
            request.patient_gender
        )
        
        # Get recommended actions and time to treatment
        recommended_actions = triage_model.get_recommended_actions(prediction["severity_level"])
        time_to_treatment = triage_model.get_time_to_treatment(prediction["severity_level"])
        
        # Try to save to database, but don't fail if it doesn't work
        try:
            # Create patient record
            patient = Patient(
                age=request.patient_age,
                gender=request.patient_gender
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            
            # Create assessment record
            assessment = Assessment(
                patient_id=patient.id,
                symptoms=[s.dict() for s in request.symptoms],
                mechanism_of_injury=request.mechanism_of_injury,
                severity_level=prediction["severity_level"],
                recommended_actions=recommended_actions,
                estimated_time_to_treatment=time_to_treatment,
                confidence_score=int(prediction["confidence_score"] * 100)
            )
            db.add(assessment)
            db.commit()
            
            logger.info(f"Assessment saved to database with severity level: {prediction['severity_level']}")
        except Exception as db_error:
            logger.error(f"Failed to save assessment to database: {str(db_error)}")
            # Continue without saving to database
        
        return TriageResponse(
            severity_level=prediction["severity_level"],
            recommended_actions=recommended_actions,
            estimated_time_to_treatment=time_to_treatment,
            confidence_score=prediction["confidence_score"]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing triage assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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