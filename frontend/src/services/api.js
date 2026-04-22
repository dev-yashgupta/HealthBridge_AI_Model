const API_BASE_URL = 'http://localhost:5000/api';

export const submitDiagnosis = async (patientId, symptoms) => {
  const response = await fetch(`${API_BASE_URL}/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_id: patientId, symptoms }),
  });
  if (!response.ok) {
    throw new Error('Diagnosis failed');
  }
  return response.json();
};

export const fetchHistory = async (patientId) => {
  const response = await fetch(`${API_BASE_URL}/history/${patientId}/recent`);
  if (!response.ok) {
    throw new Error('Failed to fetch history');
  }
  return response.json();
};

export const fetchHistorySummary = async (patientId) => {
  const response = await fetch(`${API_BASE_URL}/history/${patientId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch history summary');
  }
  return response.json();
};

export const fetchReports = async (patientId) => {
  const response = await fetch(`${API_BASE_URL}/reports/${patientId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch reports');
  }
  return response.json();
};
