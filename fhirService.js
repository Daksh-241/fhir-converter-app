const axios = require('axios');

async function fetchPatientData(serverUrl, patientId) {
  const requestUrl = `${serverUrl}/Patient/${patientId}/$everything`;
  console.log(`Fetching data from: ${requestUrl}`);
  try {
    const response = await axios.get(requestUrl, {
      headers: { 'Accept': 'application/fhir+json' }
    });
    return response.data; // This is the FHIR Bundle
  } catch (error) {
    console.error('Error fetching FHIR data:', error.message);
    throw new Error('Could not fetch data from the FHIR server.');
  }
}

module.exports = { fetchPatientData };
