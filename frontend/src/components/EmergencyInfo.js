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
} from '@mui/material';

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

const EmergencyInfo = ({ assessment }) => {
  const [contactName, setContactName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [relationship, setRelationship] = useState('');
  const [selectedISD, setSelectedISD] = useState('');
  const [error, setError] = useState('');

  const handleNameChange = (event) => {
    const value = event.target.value.replace(/[^a-zA-Z\s]/g, ''); // Only allow alphabets and spaces
    setContactName(value);
    validateForm();
  };

  const handleRelationshipChange = (event) => {
    const value = event.target.value.replace(/[^a-zA-Z\s]/g, ''); // Only allow alphabets and spaces
    setRelationship(value);
    validateForm();
  };

  const handlePhoneChange = (event) => {
    const value = event.target.value.replace(/\D/g, ''); // Remove non-digits
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

    if (!relationship.trim()) {
      setError('Relationship is required and can only contain letters and spaces');
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
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Emergency Contact Information
      </Typography>
      <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Emergency Contact Name"
              placeholder="Enter contact name (letters only)"
              value={contactName}
              onChange={handleNameChange}
              error={!!error && !contactName.trim()}
              helperText={error && !contactName.trim() ? error : ''}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Country Code</InputLabel>
              <Select
                value={selectedISD}
                onChange={(e) => setSelectedISD(e.target.value)}
                label="Country Code"
              >
                {ISD_CODES.map((code) => (
                  <MenuItem key={code.code} value={code.code}>
                    {code.code} ({code.country})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Emergency Contact Phone"
              placeholder="Enter contact phone"
              value={phoneNumber}
              onChange={handlePhoneChange}
              error={!!error && error.includes('phone')}
              helperText={error && error.includes('phone') ? error : ''}
              inputProps={{ maxLength: selectedISD ? ISD_CODES.find(code => code.code === selectedISD).length : undefined }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Relationship to Patient"
              placeholder="Enter relationship (letters only)"
              value={relationship}
              onChange={handleRelationshipChange}
              error={!!error && error.includes('relationship')}
              helperText={error && error.includes('relationship') ? error : ''}
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleSave}
              disabled={!!error}
            >
              Save Emergency Contact
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default EmergencyInfo; 