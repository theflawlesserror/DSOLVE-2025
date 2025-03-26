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
import { styled, alpha } from '@mui/material/styles';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const steps = ['Patient Information', 'Symptoms', 'Assessment'];

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  borderRadius: theme.spacing(2),
  background: alpha(theme.palette.background.paper, 0.9),
  backdropFilter: 'blur(10px)',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(1),
  },
}));

const TriageAssessment = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [formData, setFormData] = useState({
    patient_age: '',
    patient_gender: '',
    mechanism_of_injury: '',
  });

  useEffect(() => {
    fetchSymptoms();
  }, []);

    const fetchSymptoms = async () => {
      try {
        const response = await axios.get(`${API_URL}/triage/symptoms`);
      setAvailableSymptoms(response.data.symptoms);
      } catch (err) {
        setError('Failed to fetch symptoms');
      console.error('Error fetching symptoms:', err);
      }
    };

  const handleSymptomSelect = (symptom) => {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    setAvailableSymptoms(availableSymptoms.filter(s => s.name !== symptom.name));
  };

  const handleSymptomRemove = (symptomName) => {
    const symptom = selectedSymptoms.find(s => s.name === symptomName);
    setSelectedSymptoms(selectedSymptoms.filter(s => s.name !== symptomName));
    setAvailableSymptoms([...availableSymptoms, symptom]);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNext = () => {
    if (activeStep === 0) {
      if (!formData.patient_age || !formData.patient_gender || !formData.mechanism_of_injury) {
        setError('Please fill in all required fields');
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
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/triage/assess`, {
        ...formData,
        symptoms: selectedSymptoms,
      });
      setAssessment(response.data);
      setActiveStep(2);
    } catch (err) {
      setError('Failed to process assessment');
      console.error('Error submitting assessment:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <StyledTextField
                fullWidth
                label="Patient Age"
                type="number"
                value={formData.patient_age}
                onChange={(e) => handleInputChange('patient_age', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Patient Gender</InputLabel>
                <Select
                  value={formData.patient_gender}
                  onChange={(e) => handleInputChange('patient_gender', e.target.value)}
                  label="Patient Gender"
                >
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
                  <StyledTextField
                    fullWidth
                label="Mechanism of Injury/Illness"
                value={formData.mechanism_of_injury}
                onChange={(e) => handleInputChange('mechanism_of_injury', e.target.value)}
                required
              />
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Select Symptoms
            </Typography>
            <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                Selected Symptoms:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedSymptoms.map((symptom) => (
                  <Chip
                    key={symptom.name}
                    label={`${symptom.name} (Severity: ${symptom.severity})`}
                    onDelete={() => handleSymptomRemove(symptom.name)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
            <Typography variant="subtitle1" gutterBottom>
              Available Symptoms:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {availableSymptoms.map((symptom) => (
                <Chip
                  key={symptom.name}
                  label={`${symptom.name} (Severity: ${symptom.severity})`}
                  onClick={() => handleSymptomSelect(symptom)}
                  color="secondary"
                  variant="outlined"
                />
              ))}
            </Box>
              </Box>
        );
      case 2:
        return (
          <Box>
            {assessment && (
              <>
                <Typography variant="h6" gutterBottom>
                  Assessment Results
                </Typography>
                <Alert severity={assessment.severity_level === 'Critical' ? 'error' : 
                              assessment.severity_level === 'Urgent' ? 'warning' : 
                              assessment.severity_level === 'Semi-urgent' ? 'info' : 'success'} 
                       sx={{ mb: 2 }}>
                  Severity Level: {assessment.severity_level}
              </Alert>
                <Typography variant="subtitle1" gutterBottom>
                  Recommended Actions:
              </Typography>
              <List>
                {assessment.recommended_actions.map((action, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={action} />
                  </ListItem>
                ))}
              </List>
                <Typography variant="subtitle1" gutterBottom>
                  Estimated Time to Treatment: {assessment.estimated_time_to_treatment}
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                  Confidence Score: {(assessment.confidence_score * 100).toFixed(1)}%
                </Typography>
              </>
            )}
              </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <StyledPaper>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
      </Stepper>

        {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

      <form onSubmit={handleSubmit}>
          {getStepContent(activeStep)}
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
          {activeStep > 0 && (
            <Button onClick={handleBack} sx={{ mr: 1 }}>
              Back
            </Button>
          )}
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              color="primary"
              type="submit"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Assessment'}
            </Button>
          ) : (
            <Button
            variant="contained"
              color="primary"
              onClick={handleNext}
            >
              Next
            </Button>
          )}
    </Box>
      </form>
    </StyledPaper>
  );
};

export default TriageAssessment; 