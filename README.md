# FHIR Module - Excel to FHIR Converter

A comprehensive Python module that converts Excel data to FHIR (Fast Healthcare Interoperability Resources) format.

## Features

- 📊 **Excel Data Loading**: Reads data from Excel files (.xlsx, .xls)
- 🏥 **FHIR Resource Generation**: Creates Patient, Observation, and Condition resources
- 📦 **Bundle Creation**: Generates FHIR Bundles for complete data sets
- 💾 **Multiple Output Formats**: Saves as JSON Bundle or individual resource files
- 🔍 **Data Validation**: Includes error handling and data validation
- 📈 **Progress Tracking**: Shows processing progress and summaries

## Installation

1. **Install Python** (3.8 or higher)
2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from worker import FHIRModule

# Initialize with your Excel file
fhir_module = FHIRModule("mapping 4.xlsx")

# Load and process data
fhir_module.load_excel_data()
fhir_resources = fhir_module.process_excel_to_fhir()

# Save results
fhir_module.save_fhir_bundle("output.json")
fhir_module.save_individual_resources("fhir_resources/")
```

### Command Line Usage

```bash
# Run the main script
python worker.py

# Run tests
python test_fhir.py
```

## Excel File Format

The module expects Excel files with columns that can be mapped to FHIR resources. Supported column names include:

### Patient Resource Mapping
- `patient_id` - Patient identifier
- `first_name` - Patient first name
- `last_name` - Patient last name
- `gender` - Patient gender
- `birth_date` - Date of birth
- `address` - Street address
- `city` - City
- `state` - State/Province
- `postal_code` - Postal code
- `country` - Country
- `phone` - Phone number
- `email` - Email address

### Observation Resource Mapping
- `observation_name` - Name of the observation
- `loinc_code` - LOINC code for the observation
- `value` - Observation value
- `unit` - Unit of measurement
- `unit_code` - Unit code
- `observation_date` - Date of observation

### Condition Resource Mapping
- `condition_name` - Name of the condition
- `snomed_code` - SNOMED CT code
- `onset_date` - Date of onset

## Output Files

### FHIR Bundle (fhir_bundle.json)
A complete FHIR Bundle containing all generated resources:

```json
{
  "resourceType": "Bundle",
  "id": "bundle-id",
  "type": "collection",
  "timestamp": "2024-01-01T00:00:00Z",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "patient-id",
        ...
      }
    }
  ]
}
```

### Individual Resources (fhir_resources/)
Separate JSON files for each FHIR resource:
- `patient_1.json`
- `observation_1.json`
- `condition_1.json`
- etc.

## FHIR Resources Generated

### 1. Patient Resource
- Contains patient demographic information
- Includes identifiers, names, contact information
- Maps to standard FHIR Patient resource structure

### 2. Observation Resource
- Contains clinical observations and measurements
- Includes vital signs, lab results, etc.
- Uses LOINC codes for standardization

### 3. Condition Resource
- Contains medical conditions and diagnoses
- Uses SNOMED CT codes for standardization
- Includes clinical and verification status

## Error Handling

The module includes comprehensive error handling:
- File not found errors
- Invalid Excel format errors
- Missing required data warnings
- JSON serialization errors

## Testing

Run the test suite to validate functionality:

```bash
python test_fhir.py
```

The test script will:
1. Load the Excel file
2. Generate FHIR resources
3. Save output files
4. Validate JSON structure
5. Print summary statistics

## Customization

You can customize the FHIR resource generation by modifying the methods in the `FHIRModule` class:

- `generate_patient_resource()` - Customize Patient resource generation
- `generate_observation_resource()` - Customize Observation resource generation
- `generate_condition_resource()` - Customize Condition resource generation

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- fhir.resources >= 7.0.0

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please check the error messages and ensure:
1. Python is properly installed
2. Required packages are installed
3. Excel file exists and is accessible
4. Excel file has the expected column structure
