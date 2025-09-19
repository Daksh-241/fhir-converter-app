# FHIR Converter Node.js Backend

This is a Node.js Express backend for converting FHIR data to CSV format. It works alongside your existing Python Flask application.

## Files Created

1. **package.json** - Node.js dependencies and project configuration
2. **index.js** - Main Express server with health check and conversion endpoint
3. **fhirService.js** - Service for fetching FHIR data from external servers
4. **converterService.js** - Service for converting FHIR bundles to CSV format

## Installation

1. Install Node.js dependencies:
```bash
npm install
```

This will install:
- `express` - Web framework
- `cors` - Cross-Origin Resource Sharing
- `axios` - HTTP client for API requests
- `json2csv` - JSON to CSV converter

## Running the Server

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

The server will run on port 5000 by default (or the PORT environment variable if set).

## API Endpoints

### Health Check
- **GET** `/` - Returns server status message

### Convert FHIR to CSV
- **POST** `/api/convert`
- **Body**: 
  ```json
  {
    "serverUrl": "https://your-fhir-server.com",
    "patientId": "patient-123"
  }
  ```
- **Response**: CSV file download with patient data

## Usage Example

```javascript
// Example API call to convert FHIR data
fetch('http://localhost:5000/api/convert', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    serverUrl: 'https://hapi.fhir.org/baseR4',
    patientId: '1234567'
  })
})
.then(response => response.blob())
.then(blob => {
  // Handle CSV download
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'patient-data.csv';
  a.click();
});
```

## Architecture

- **index.js**: Main server setup and routing
- **fhirService.js**: Handles FHIR server communication using the `$everything` operation
- **converterService.js**: Converts FHIR Bundle resources to flat CSV structure

## CSV Output Format

The CSV includes the following columns:
- `resourceType` - Type of FHIR resource (Patient, Observation, etc.)
- `id` - Resource ID
- `status` - Resource status
- `code_text` - Human-readable code description
- `effective_date` - Relevant date for the resource
- `patient_reference` - Reference to the patient

## Error Handling

The API includes comprehensive error handling for:
- Missing required parameters
- FHIR server connection issues
- Data conversion errors
- Invalid FHIR responses

## Development

For development with auto-restart on file changes:
```bash
npm install -g nodemon
npm run dev
```

## Integration with Existing Python App

This Node.js backend runs independently from your existing Python Flask app. You can:
1. Run both servers on different ports
2. Use the Node.js backend for FHIR-to-CSV conversion
3. Use the Python backend for other functionality
4. Create a frontend that communicates with both backends as needed
