// Install dependencies by running this in the terminal:
// npm install express cors axios json2csv

const express = require('express');
const cors = require('cors');
const { fetchPatientData } = require('./fhirService');
const { convertBundleToCsv } = require('./converterService');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check route
app.get('/', (req, res) => {
  res.send('FHIR Converter Backend is ready!');
});

// Add this endpoint inside index.js, before the app.listen() call
app.post('/api/convert', async (req, res) => {
  const { serverUrl, patientId } = req.body;

  if (!serverUrl || !patientId) {
    return res.status(400).json({ error: 'serverUrl and patientId are required.' });
  }

  try {
    // 1. Fetch data from the FHIR server
    const fhirBundle = await fetchPatientData(serverUrl, patientId);

    // 2. Convert the bundle to CSV
    const csvData = convertBundleToCsv(fhirBundle);
    
    // 3. Send CSV back as a downloadable file
    res.header('Content-Type', 'text/csv');
    res.attachment(`patient-${patientId}-data.csv`);
    res.send(csvData);

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
