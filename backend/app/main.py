from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from .models.triage_model import TriageModel

app = FastAPI(
    title="TriageAI API",
    description="AI-powered triage assistant for emergency responders",
    version="1.0.0"
)

# Initialize the triage model
triage_model = TriageModel()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {"message": "Welcome to TriageAI API"}

@app.post("/triage/assess", response_model=TriageResponse)
async def assess_triage(request: TriageRequest):
    try:
        # Get prediction from the model
        prediction = triage_model.predict(
            request.symptoms,
            request.patient_age,
            request.patient_gender
        )
        
        # Get recommended actions and time to treatment
        recommended_actions = triage_model.get_recommended_actions(prediction["severity_level"])
        time_to_treatment = triage_model.get_time_to_treatment(prediction["severity_level"])
        
        return TriageResponse(
            severity_level=prediction["severity_level"],
            recommended_actions=recommended_actions,
            estimated_time_to_treatment=time_to_treatment,
            confidence_score=prediction["confidence_score"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/triage/symptoms")
async def get_common_symptoms():
    # TODO: Implement database integration
    return {
        "symptoms": [
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
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 