import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  useTheme,
  alpha,
} from '@mui/material';
import { styled } from '@mui/material/styles';

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
    '&:hover fieldset': {
      borderColor: alpha(theme.palette.primary.main, 0.5),
    },
  },
}));

const StyledSelect = styled(Select)(({ theme }) => ({
  borderRadius: theme.spacing(1),
  '&:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: alpha(theme.palette.primary.main, 0.5),
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(2),
  padding: theme.spacing(1.5, 4),
  textTransform: 'none',
  fontWeight: 600,
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  '&:hover': {
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
  },
}));

const ISD_CODES = [
  { code: '+1', country: 'United States/Canada', length: 10 },
  { code: '+44', country: 'United Kingdom', length: 10 },
  { code: '+91', country: 'India', length: 10 },
  { code: '+86', country: 'China', length: 11 },
  { code: '+81', country: 'Japan', length: 10 },
  { code: '+49', country: 'Germany', length: 10 },
  { code: '+33', country: 'France', length: 9 },
  { code: '+39', country: 'Italy', length: 10 },
  { code: '+34', country: 'Spain', length: 9 },
  { code: '+61', country: 'Australia', length: 9 },
];

const RELATIONSHIPS = [
  'Spouse',
  'Parent',
  'Child',
  'Sibling',
  'Grandparent',
  'Aunt/Uncle',
  'Cousin',
  'Friend',
  'Guardian',
  'Other'
];

const EmergencyInfo = ({ assessment }) => {
  const theme = useTheme();
  const [contactName, setContactName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [relationship, setRelationship] = useState('');
  const [otherRelationship, setOtherRelationship] = useState('');
  const [selectedISD, setSelectedISD] = useState('');
  const [error, setError] = useState('');

  const handleNameChange = (event) => {
    const value = event.target.value.replace(/[^a-zA-Z\s]/g, '');
    setContactName(value);
    validateForm();
  };

  const handleRelationshipChange = (event) => {
    setRelationship(event.target.value);
    if (event.target.value !== 'Other') {
      setOtherRelationship('');
    }
    validateForm();
  };

  const handleOtherRelationshipChange = (event) => {
    const value = event.target.value.replace(/[^a-zA-Z\s]/g, '');
    setOtherRelationship(value);
    validateForm();
  };

  const handlePhoneChange = (event) => {
    const value = event.target.value.replace(/\D/g, '');
    setPhoneNumber(value);
    validatePhone(value);
  };

  const validatePhone = (number) => {
    if (!selectedISD) {
      setError('Please select a country code first');
      return false;
    }

    const selectedCountry = ISD_CODES.find(code => code.code === selectedISD);
    if (number.length !== selectedCountry.length) {
      setError(`Phone number should be ${selectedCountry.length} digits for ${selectedCountry.country}`);
      return false;
    }

    setError('');
    return true;
  };

  const validateForm = () => {
    if (!contactName.trim()) {
      setError('Contact name is required and can only contain letters and spaces');
      return false;
    }

    if (!relationship) {
      setError('Please select a relationship');
      return false;
    }

    if (relationship === 'Other' && !otherRelationship.trim()) {
      setError('Please specify the relationship');
      return false;
    }

    if (!phoneNumber) {
      setError('Phone number is required');
      return false;
    }

    if (!validatePhone(phoneNumber)) {
      return false;
    }

    setError('');
    return true;
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }

    alert('Emergency contact information saved!');
  };

  return (
    <Box sx={{ mt: 4 }}>
      <StyledPaper elevation={0}>
        <Typography 
          variant="h5" 
          gutterBottom 
          sx={{ 
            fontWeight: 600,
            color: theme.palette.primary.main,
            mb: 3
          }}
        >
          Emergency Contact Information
        </Typography>
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              borderRadius: 2,
              '& .MuiAlert-message': {
                fontWeight: 500
              }
            }}
          >
            {error}
          </Alert>
        )}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <StyledTextField
              fullWidth
              label="Contact Name"
              value={contactName}
              onChange={handleNameChange}
              error={!!error && error.includes('Contact name')}
              helperText={error && error.includes('Contact name') ? error : ''}
              placeholder="Enter contact's name"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth error={!!error && error.includes('relationship')}>
              <InputLabel>Relationship</InputLabel>
              <StyledSelect
                value={relationship}
                onChange={handleRelationshipChange}
                label="Relationship"
              >
                {RELATIONSHIPS.map((rel) => (
                  <MenuItem key={rel} value={rel}>
                    {rel}
                  </MenuItem>
                ))}
              </StyledSelect>
              {error && error.includes('relationship') && (
                <Typography color="error" variant="caption" sx={{ mt: 1 }}>
                  {error}
                </Typography>
              )}
            </FormControl>
          </Grid>
          {relationship === 'Other' && (
            <Grid item xs={12}>
              <StyledTextField
                fullWidth
                label="Specify Relationship"
                value={otherRelationship}
                onChange={handleOtherRelationshipChange}
                error={!!error && error.includes('specify')}
                helperText={error && error.includes('specify') ? error : ''}
                placeholder="Enter relationship"
              />
            </Grid>
          )}
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Country Code</InputLabel>
              <StyledSelect
                value={selectedISD}
                onChange={(e) => setSelectedISD(e.target.value)}
                label="Country Code"
              >
                {ISD_CODES.map((code) => (
                  <MenuItem key={code.code} value={code.code}>
                    {code.code} ({code.country})
                  </MenuItem>
                ))}
              </StyledSelect>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={8}>
            <StyledTextField
              fullWidth
              label="Phone Number"
              value={phoneNumber}
              onChange={handlePhoneChange}
              error={!!error && error.includes('Phone number')}
              helperText={error && error.includes('Phone number') ? error : ''}
              placeholder="Enter phone number"
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <StyledButton
                variant="contained"
                color="primary"
                onClick={handleSave}
                disabled={!!error}
                size="large"
              >
                Save Emergency Contact
              </StyledButton>
            </Box>
          </Grid>
        </Grid>
      </StyledPaper>
    </Box>
  );
};

export default EmergencyInfo; 