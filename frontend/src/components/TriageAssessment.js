import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Alert,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';
import EmergencyInfo from './EmergencyInfo';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const steps = ['Patient Information', 'Symptoms', 'Assessment'];

const TriageAssessment = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [mechanismOfInjury, setMechanismOfInjury] = useState('');
  const [assessment, setAssessment] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch common symptoms from the API
    const fetchSymptoms = async () => {
      try {
        const response = await axios.get(`${API_URL}/triage/symptoms`);
        setSymptoms(response.data.symptoms);
      } catch (err) {
        setError('Failed to fetch symptoms');
      }
    };
    fetchSymptoms();
  }, []);

  const handleSymptomSelect = (symptom) => {
    if (!selectedSymptoms.find(s => s.name === symptom.name)) {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  const handleSymptomRemove = (symptomName) => {
    setSelectedSymptoms(selectedSymptoms.filter(s => s.name !== symptomName));
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/triage/assess`, {
        symptoms: selectedSymptoms,
        patient_age: parseInt(patientAge),
        patient_gender: patientGender,
        mechanism_of_injury: mechanismOfInjury,
      });
      setAssessment(response.data);
      setError(null);
      handleNext();
    } catch (err) {
      setError('Failed to assess triage');
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Patient Age"
                type="number"
                value={patientAge}
                onChange={(e) => setPatientAge(e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>Patient Gender</InputLabel>
                <Select
                  value={patientGender}
                  onChange={(e) => setPatientGender(e.target.value)}
                  label="Patient Gender"
                >
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Mechanism of Injury"
                value={mechanismOfInjury}
                onChange={(e) => setMechanismOfInjury(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
                disabled={!patientAge || !patientGender}
              >
                Next
              </Button>
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Select Symptoms
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {symptoms.map((symptom) => (
                  <Chip
                    key={symptom.name}
                    label={symptom.name}
                    onClick={() => handleSymptomSelect(symptom)}
                    color={selectedSymptoms.find(s => s.name === symptom.name) ? 'primary' : 'default'}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedSymptoms.map((symptom) => (
                  <Chip
                    key={symptom.name}
                    label={symptom.name}
                    onDelete={() => handleSymptomRemove(symptom.name)}
                    color="primary"
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={selectedSymptoms.length === 0 || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Assess Triage'}
              </Button>
            </Grid>
          </Grid>
        );
      case 2:
        return (
          <>
            {assessment && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Assessment Results
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography variant="subtitle1">
                    Severity Level: {assessment.severity_level}
                  </Typography>
                  <Typography variant="subtitle1">
                    Time to Treatment: {assessment.estimated_time_to_treatment}
                  </Typography>
                  <Typography variant="subtitle1" gutterBottom>
                    Recommended Actions:
                  </Typography>
                  <ul>
                    {assessment.recommended_actions.map((action, index) => (
                      <li key={index}>{action}</li>
                    ))}
                  </ul>
                </Paper>
              </Box>
            )}
            <EmergencyInfo assessment={assessment} />
          </>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Triage Assessment
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <form onSubmit={handleSubmit}>
          {getStepContent(activeStep)}
        </form>
      </Paper>
    </Box>
  );
};

export default TriageAssessment; 