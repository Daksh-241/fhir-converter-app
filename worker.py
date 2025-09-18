import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class FHIRModule:
    """FHIR Module for processing Excel data and generating FHIR resources"""
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path
        self.data = None
        self.fhir_resources = []
        
    def load_excel_data(self) -> bool:
        """Load data from Excel file"""
        try:
            self.data = pd.read_excel(self.excel_file_path)
            print(f"✅ Excel data loaded successfully!")
            print(f"📊 Shape: {self.data.shape}")
            print(f"📋 Columns: {list(self.data.columns)}")
            print("\n📄 First 5 rows:")
            print(self.data.head())
            return True
        except FileNotFoundError:
            print(f"❌ File {self.excel_file_path} not found!")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    
    def generate_patient_resource(self, row: pd.Series) -> Dict[str, Any]:
        """Generate FHIR Patient resource from Excel row"""
        patient_id = str(uuid.uuid4())
        
        # Extract patient information (adjust column names based on your Excel structure)
        patient_data = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [
                {
                    "use": "usual",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR",
                                "display": "Medical Record Number"
                            }
                        ]
                    },
                    "value": str(row.get('patient_id', patient_id))
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": str(row.get('last_name', '')),
                    "given": [str(row.get('first_name', ''))]
                }
            ],
            "gender": str(row.get('gender', 'unknown')).lower(),
            "birthDate": str(row.get('birth_date', '')),
            "address": [
                {
                    "use": "home",
                    "line": [str(row.get('address', ''))],
                    "city": str(row.get('city', '')),
                    "state": str(row.get('state', '')),
                    "postalCode": str(row.get('postal_code', '')),
                    "country": str(row.get('country', 'US'))
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": str(row.get('phone', '')),
                    "use": "home"
                },
                {
                    "system": "email",
                    "value": str(row.get('email', '')),
                    "use": "home"
                }
            ]
        }
        
        return patient_data
    
    def generate_observation_resource(self, row: pd.Series) -> Dict[str, Any]:
        """Generate FHIR Observation resource from Excel row"""
        observation_id = str(uuid.uuid4())
        
        observation_data = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": str(row.get('loinc_code', '')),
                        "display": str(row.get('observation_name', ''))
                    }
                ],
                "text": str(row.get('observation_name', ''))
            },
            "subject": {
                "reference": f"Patient/{str(uuid.uuid4())}"
            },
            "effectiveDateTime": str(row.get('observation_date', datetime.now().isoformat())),
            "valueQuantity": {
                "value": float(row.get('value', 0)) if pd.notna(row.get('value')) else 0,
                "unit": str(row.get('unit', '')),
                "system": "http://unitsofmeasure.org",
                "code": str(row.get('unit_code', ''))
            }
        }
        
        return observation_data
    
    def generate_condition_resource(self, row: pd.Series) -> Dict[str, Any]:
        """Generate FHIR Condition resource from Excel row"""
        condition_id = str(uuid.uuid4())
        
        condition_data = {
            "resourceType": "Condition",
            "id": condition_id,
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": str(row.get('snomed_code', '')),
                        "display": str(row.get('condition_name', ''))
                    }
                ],
                "text": str(row.get('condition_name', ''))
            },
            "subject": {
                "reference": f"Patient/{str(uuid.uuid4())}"
            },
            "onsetDateTime": str(row.get('onset_date', datetime.now().isoformat())),
            "recordedDate": datetime.now().isoformat()
        }
        
        return condition_data
    
    def process_excel_to_fhir(self) -> List[Dict[str, Any]]:
        """Process Excel data and generate FHIR resources"""
        if self.data is None:
            print("❌ No data loaded. Please load Excel data first.")
            return []
        
        fhir_resources = []
        
        print(f"\n🔄 Processing {len(self.data)} rows to FHIR resources...")
        
        for index, row in self.data.iterrows():
            print(f"Processing row {index + 1}/{len(self.data)}")
            
            # Generate different types of FHIR resources based on data
            try:
                # Always generate Patient resource
                patient_resource = self.generate_patient_resource(row)
                fhir_resources.append(patient_resource)
                
                # Generate Observation if relevant columns exist
                if any(col in self.data.columns for col in ['observation_name', 'value', 'unit']):
                    observation_resource = self.generate_observation_resource(row)
                    fhir_resources.append(observation_resource)
                
                # Generate Condition if relevant columns exist
                if any(col in self.data.columns for col in ['condition_name', 'snomed_code']):
                    condition_resource = self.generate_condition_resource(row)
                    fhir_resources.append(condition_resource)
                    
            except Exception as e:
                print(f"⚠️  Error processing row {index + 1}: {e}")
                continue
        
        self.fhir_resources = fhir_resources
        print(f"✅ Generated {len(fhir_resources)} FHIR resources")
        return fhir_resources
    
    def save_fhir_bundle(self, output_file: str = "fhir_bundle.json") -> bool:
        """Save FHIR resources as a Bundle"""
        if not self.fhir_resources:
            print("❌ No FHIR resources to save. Process data first.")
            return False
        
        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": []
        }
        
        for resource in self.fhir_resources:
            bundle["entry"].append({
                "resource": resource
            })
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)
            print(f"✅ FHIR Bundle saved to {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving FHIR Bundle: {e}")
            return False
    
    def save_individual_resources(self, output_dir: str = "fhir_resources") -> bool:
        """Save individual FHIR resources as separate files"""
        if not self.fhir_resources:
            print("❌ No FHIR resources to save. Process data first.")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            for i, resource in enumerate(self.fhir_resources):
                filename = f"{resource['resourceType'].lower()}_{i+1}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(resource, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Individual FHIR resources saved to {output_dir}/")
            return True
        except Exception as e:
            print(f"❌ Error saving individual resources: {e}")
            return False
    
    def print_summary(self):
        """Print summary of generated FHIR resources"""
        if not self.fhir_resources:
            print("❌ No FHIR resources generated.")
            return
        
        resource_types = {}
        for resource in self.fhir_resources:
            resource_type = resource.get('resourceType', 'Unknown')
            resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
        
        print(f"\n📊 FHIR Resources Summary:")
        print(f"Total resources: {len(self.fhir_resources)}")
        for resource_type, count in resource_types.items():
            print(f"  - {resource_type}: {count}")

def main():
    """Main function to run the FHIR module"""
    print("🏥 FHIR Module - Excel to FHIR Converter")
    print("=" * 50)
    
    # Initialize FHIR module
    excel_file = "mapping 4.xlsx"
    fhir_module = FHIRModule(excel_file)
    
    # Load Excel data
    if not fhir_module.load_excel_data():
        return
    
    # Process data to FHIR
    fhir_resources = fhir_module.process_excel_to_fhir()
    
    if fhir_resources:
        # Print summary
        fhir_module.print_summary()
        
        # Save FHIR Bundle
        fhir_module.save_fhir_bundle("fhir_bundle.json")
        
        # Save individual resources
        fhir_module.save_individual_resources("fhir_resources")
        
        print(f"\n🎉 FHIR conversion completed successfully!")
    else:
        print("❌ No FHIR resources were generated.")

if __name__ == "__main__":
    main()
