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
  List,
  ListItem,
  ListItemText,
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
  const [causeValidation, setCauseValidation] = useState(null);
  const [validatingCause, setValidatingCause] = useState(false);

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
    // Validate current step before proceeding
    if (activeStep === 0) {
      if (!patientAge || !patientGender || (causeValidation && !causeValidation.is_valid)) {
        setError('Please complete all required fields before proceeding');
        return;
      }
    } else if (activeStep === 1) {
      if (selectedSymptoms.length === 0) {
        setError('Please select at least one symptom');
        return;
      }
    }
    setError(null);
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setError(null);
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
      if (err.response?.data?.detail?.message) {
        setError(err.response.data.detail.message);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to assess triage. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const validateCause = async (cause) => {
    if (!cause || cause.length < 3) {
      setCauseValidation(null);
      return;
    }

    setValidatingCause(true);
    try {
      const response = await axios.post(`${API_URL}/triage/validate-cause`, {
        cause: cause
      });
      setCauseValidation(response.data);
    } catch (err) {
      setError('Failed to validate injury cause');
    } finally {
      setValidatingCause(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      validateCause(mechanismOfInjury);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [mechanismOfInjury]);

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
                onChange={(e) => {
                  const value = e.target.value;
                  // Only allow digits
                  if (value === '' || /^\d+$/.test(value)) {
                    const numValue = parseInt(value);
                    // Only allow positive numbers between 1 and 120
                    if (value === '' || (numValue > 0 && numValue <= 120)) {
                      setPatientAge(value);
                    }
                  }
                }}
                onKeyPress={(e) => {
                  // Only allow digits
                  if (!/[0-9]/.test(e.key)) {
                    e.preventDefault();
                  }
                }}
                inputProps={{
                  min: 1,
                  max: 120,
                  step: 1,
                  pattern: '[0-9]*',
                  inputMode: 'numeric'
                }}
                required
                error={patientAge && (parseInt(patientAge) <= 0 || parseInt(patientAge) > 120)}
                helperText={patientAge && (parseInt(patientAge) <= 0 || parseInt(patientAge) > 120) ? 'Please enter a valid age between 1 and 120' : ''}
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
                label="How did the injury/illness occur?"
                placeholder="e.g., car accident, fall, sports injury, etc."
                value={mechanismOfInjury}
                onChange={(e) => setMechanismOfInjury(e.target.value)}
                error={causeValidation && !causeValidation.is_valid}
                helperText={causeValidation?.message}
                disabled={validatingCause}
              />
              {causeValidation && !causeValidation.is_valid && causeValidation.suggestions && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Suggestions:
                  </Typography>
                  <List dense>
                    {causeValidation.suggestions.map((suggestion, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={suggestion} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleBack}
                  disabled={activeStep === 0}
                >
                  Back
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleNext}
                  disabled={!patientAge || !patientGender || (causeValidation && !causeValidation.is_valid)}
                >
                  Next
                </Button>
              </Box>
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
              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleBack}
                >
                  Back
                </Button>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSubmit}
                    disabled={selectedSymptoms.length === 0 || loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Assess Triage'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={handleNext}
                    disabled={selectedSymptoms.length === 0}
                  >
                    Next
                  </Button>
                </Box>
              </Box>
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
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={handleBack}
              >
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={() => {
                  // Reset form
                  setActiveStep(0);
                  setPatientAge('');
                  setPatientGender('');
                  setMechanismOfInjury('');
                  setSelectedSymptoms([]);
                  setAssessment(null);
                  setError(null);
                }}
              >
                Start New Assessment
              </Button>
            </Box>
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