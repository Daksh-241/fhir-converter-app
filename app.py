from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import io
import base64
from worker_enhanced import FHIRModule
from code_mapping import CodeMappingService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
code_mapper = CodeMappingService()

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process to FHIR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process with FHIR module
            fhir_module = FHIRModule(filepath)
            if fhir_module.load_excel_data():
                fhir_resources = fhir_module.process_data_to_fhir()
                
                # Save results
                bundle_id = str(uuid.uuid4())
                bundle_file = f"fhir_bundle_{bundle_id}.json"
                fhir_module.save_fhir_bundle(bundle_file)
                
                return jsonify({
                    'success': True,
                    'message': f'Processed {len(fhir_resources)} resources',
                    'bundle_id': bundle_id,
                    'resource_count': len(fhir_resources),
                    'data_preview': fhir_module.data.head().to_dict('records') if fhir_module.data is not None else []
                })
            else:
                return jsonify({'error': 'Failed to process file'}), 400
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patient', methods=['POST'])
def create_patient():
    """Create FHIR patient from form data"""
    try:
        data = request.json
        
        # Create patient data structure
        patient_data = {
            'first_name': data.get('firstName', ''),
            'last_name': data.get('lastName', ''),
            'gender': data.get('gender', 'unknown'),
            'birth_date': data.get('birthDate', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'postal_code': data.get('postalCode', ''),
            'country': data.get('country', 'US'),
            'condition_name': data.get('condition', ''),
            'snomed_code': data.get('snomedCode', ''),
            'observation_name': data.get('observation', ''),
            'value': data.get('value', ''),
            'unit': data.get('unit', '')
        }
        
        # Process with FHIR module
        fhir_module = FHIRModule()
        fhir_module.user_input_data = [patient_data]
        
        if fhir_module.convert_user_input_to_dataframe():
            fhir_resources = fhir_module.process_data_to_fhir()
            
            if fhir_resources:
                bundle_id = str(uuid.uuid4())
                bundle_file = f"fhir_bundle_{bundle_id}.json"
                fhir_module.save_fhir_bundle(bundle_file)
                
                return jsonify({
                    'success': True,
                    'message': 'Patient created successfully',
                    'bundle_id': bundle_id,
                    'resources': fhir_resources
                })
        
        return jsonify({'error': 'Failed to create patient'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bundle/<bundle_id>')
def get_bundle(bundle_id):
    """Get FHIR bundle by ID"""
    try:
        bundle_file = f"fhir_bundle_{bundle_id}.json"
        if os.path.exists(bundle_file):
            with open(bundle_file, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
            return jsonify(bundle)
        else:
            return jsonify({'error': 'Bundle not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<bundle_id>')
def download_bundle(bundle_id):
    """Download FHIR bundle as JSON file"""
    try:
        bundle_file = f"fhir_bundle_{bundle_id}.json"
        if os.path.exists(bundle_file):
            return send_file(bundle_file, as_attachment=True, download_name=f'fhir_bundle_{bundle_id}.json')
        else:
            return jsonify({'error': 'Bundle not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<bundle_id>/csv')
def export_csv(bundle_id):
    """Export FHIR bundle data to CSV"""
    try:
        bundle_file = f"fhir_bundle_{bundle_id}.json"
        if os.path.exists(bundle_file):
            with open(bundle_file, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
            
            # Convert to CSV
            data = []
            for entry in bundle.get('entry', []):
                resource = entry.get('resource', {})
                data.append({
                    'Resource_Type': resource.get('resourceType', ''),
                    'ID': resource.get('id', ''),
                    'Created_Date': bundle.get('timestamp', '')
                })
            
            df = pd.DataFrame(data)
            csv_file = f"export_{bundle_id}.csv"
            df.to_csv(csv_file, index=False)
            
            return send_file(csv_file, as_attachment=True, download_name=f'fhir_export_{bundle_id}.csv')
        else:
            return jsonify({'error': 'Bundle not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/map-codes', methods=['POST'])
def map_codes():
    """Map by any identifier (disease or any code) to return all codes and a FHIR Condition."""
    try:
        data = request.json or {}
        disease = str(data.get('disease', '')).strip()
        snomed = str(data.get('snomedCode', '')).strip()
        icd11 = str(data.get('icd11Code', '')).strip()
        ayurveda = str(data.get('ayurvedaCode', '')).strip()
        siddha = str(data.get('siddhaCode', '')).strip()
        unani = str(data.get('unaniCode', '')).strip()
        if not any([disease, snomed, icd11, ayurveda, siddha, unani]):
            return jsonify({'error': 'Provide at least one of disease/snomedCode/icd11Code/ayurvedaCode/siddhaCode/unaniCode'}), 400

        mapped = code_mapper.find_by_any(
            disease=disease or None,
            snomed=snomed or None,
            icd11=icd11 or None,
            ayurveda=ayurveda or None,
            siddha=siddha or None,
            unani=unani or None
        )
        if not mapped:
            return jsonify({'error': 'No mapping found'}), 404

        systems = code_mapper.systems_for_response()
        codings = []
        display = disease or mapped.get('disease', '')
        if mapped.get('snomed_code') or display:
            codings.append({'system': systems.get('snomed'), 'code': mapped.get('snomed_code', ''), 'display': display})
        if mapped.get('icd11_code'):
            codings.append({'system': systems.get('icd11'), 'code': mapped.get('icd11_code'), 'display': display})
        if mapped.get('ayurveda_code'):
            codings.append({'system': systems.get('ayurveda'), 'code': mapped.get('ayurveda_code'), 'display': display})
        if mapped.get('siddha_code'):
            codings.append({'system': systems.get('siddha'), 'code': mapped.get('siddha_code'), 'display': display})
        if mapped.get('unani_code'):
            codings.append({'system': systems.get('unani'), 'code': mapped.get('unani_code'), 'display': display})

        condition_resource = {
            'resourceType': 'Condition',
            'code': {
                'coding': codings,
                'text': display
            }
        }

        return jsonify({
            'success': True,
            'mappings': mapped,
            'systems': systems,
            'condition': condition_resource
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
