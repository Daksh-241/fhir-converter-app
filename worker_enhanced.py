import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from code_mapping import CodeMappingService

class FHIRModule:
    """Enhanced FHIR Module for processing Excel data, user input, and generating FHIR resources"""
    
    def __init__(self, excel_file_path: str = None):
        self.excel_file_path = excel_file_path
        self.data = None
        self.fhir_resources = []
        self.user_input_data = []
        self.code_mapping = CodeMappingService()
        
    def load_excel_data(self) -> bool:
        """Load data from Excel file"""
        try:
            self.data = pd.read_excel(self.excel_file_path)
            print(f"✅ Excel data loaded successfully!")
            print(f"�� Shape: {self.data.shape}")
            print(f"�� Columns: {list(self.data.columns)}")
            print("\n📄 First 5 rows:")
            print(self.data.head())
            return True
        except FileNotFoundError:
            print(f"❌ File {self.excel_file_path} not found!")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    
    def get_user_input(self) -> bool:
        """Get user input data interactively"""
        print("\n🏥 Interactive FHIR Data Entry")
        print("=" * 40)
        print("Enter patient information (press Enter to skip optional fields)")
        print("Type 'done' when finished entering patients")
        
        while True:
            print(f"\n--- Patient {len(self.user_input_data) + 1} ---")
            
            # Get patient information
            patient_data = {}
            
            # Required fields
            patient_data['first_name'] = input("First Name: ").strip()
            if not patient_data['first_name']:
                print("❌ First name is required!")
                continue
                
            patient_data['last_name'] = input("Last Name: ").strip()
            if not patient_data['last_name']:
                print("❌ Last name is required!")
                continue
            
            # Optional fields
            patient_data['patient_id'] = input("Patient ID (optional): ").strip()
            patient_data['gender'] = input("Gender (male/female/other/unknown): ").strip().lower()
            patient_data['birth_date'] = input("Birth Date (YYYY-MM-DD, optional): ").strip()
            patient_data['phone'] = input("Phone Number (optional): ").strip()
            patient_data['email'] = input("Email (optional): ").strip()
            patient_data['address'] = input("Address (optional): ").strip()
            patient_data['city'] = input("City (optional): ").strip()
            patient_data['state'] = input("State (optional): ").strip()
            patient_data['postal_code'] = input("Postal Code (optional): ").strip()
            patient_data['country'] = input("Country (optional, default: US): ").strip() or "US"
            
            # Medical information
            print("\n--- Medical Information ---")
            patient_data['condition_name'] = input("Medical Condition (optional): ").strip()
            patient_data['snomed_code'] = input("SNOMED Code (optional): ").strip()
            patient_data['icd_code'] = input("ICD Code (optional): ").strip()
            patient_data['observation_name'] = input("Observation/Test Name (optional): ").strip()
            patient_data['value'] = input("Observation Value (optional): ").strip()
            patient_data['unit'] = input("Unit of Measurement (optional): ").strip()
            patient_data['observation_date'] = input("Observation Date (YYYY-MM-DD, optional): ").strip()
            
            # Add to user input data
            self.user_input_data.append(patient_data)
            
            # Ask if user wants to continue
            continue_input = input("\nAdd another patient? (y/n): ").strip().lower()
            if continue_input in ['n', 'no', 'done', '']:
                break
        
        if self.user_input_data:
            print(f"\n✅ Collected {len(self.user_input_data)} patient records")
            return True
        else:
            print("❌ No patient data collected")
            return False
    
    def convert_user_input_to_dataframe(self) -> bool:
        """Convert user input data to pandas DataFrame"""
        if not self.user_input_data:
            return False
        
        try:
            self.data = pd.DataFrame(self.user_input_data)
            print(f"✅ User input data converted to DataFrame!")
            print(f"�� Shape: {self.data.shape}")
            print(f"�� Columns: {list(self.data.columns)}")
            return True
        except Exception as e:
            print(f"❌ Error converting user input: {e}")
            return False
    
    def generate_patient_resource(self, row: pd.Series) -> Dict[str, Any]:
        """Generate FHIR Patient resource from data row"""
        patient_id = str(uuid.uuid4())
        
        # Extract patient information
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
        """Generate FHIR Observation resource from data row"""
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
                "value": float(row.get('value', 0)) if pd.notna(row.get('value')) and str(row.get('value')).replace('.', '').isdigit() else 0,
                "unit": str(row.get('unit', '')),
                "system": "http://unitsofmeasure.org",
                "code": str(row.get('unit_code', ''))
            }
        }
        
        return observation_data
    
    def generate_condition_resource(self, row: pd.Series) -> Dict[str, Any]:
        """Generate FHIR Condition resource from data row"""
        condition_id = str(uuid.uuid4())
        
        # Build primary SNOMED coding (if any)
        snomed_code = str(row.get('snomed_code', '') or '').strip()
        condition_name = str(row.get('condition_name', '') or '').strip()

        # Resolve additional codes using mapping service if we have a condition name
        mapped = self.code_mapping.find_by_disease(condition_name) if condition_name else None

        codings: List[Dict[str, Any]] = []
        if snomed_code or condition_name:
            codings.append({
                "system": "http://snomed.info/sct",
                "code": snomed_code,
                "display": condition_name
            })

        # ICD-11
        if mapped and mapped.get('icd11_code'):
            codings.append({
                "system": self.code_mapping.systems_for_response().get('icd11'),
                "code": mapped.get('icd11_code'),
                "display": condition_name or mapped.get('disease', '')
            })

        # AYUSH: Ayurveda, Siddha, Unani
        if mapped and mapped.get('ayurveda_code'):
            codings.append({
                "system": self.code_mapping.systems_for_response().get('ayurveda'),
                "code": mapped.get('ayurveda_code'),
                "display": condition_name or mapped.get('disease', '')
            })
        if mapped and mapped.get('siddha_code'):
            codings.append({
                "system": self.code_mapping.systems_for_response().get('siddha'),
                "code": mapped.get('siddha_code'),
                "display": condition_name or mapped.get('disease', '')
            })
        if mapped and mapped.get('unani_code'):
            codings.append({
                "system": self.code_mapping.systems_for_response().get('unani'),
                "code": mapped.get('unani_code'),
                "display": condition_name or mapped.get('disease', '')
            })

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
                "coding": codings or [],
                "text": condition_name
            },
            "subject": {
                "reference": f"Patient/{str(uuid.uuid4())}"
            },
            "onsetDateTime": str(row.get('onset_date', datetime.now().isoformat())),
            "recordedDate": datetime.now().isoformat()
        }
        
        return condition_data
    
    def process_data_to_fhir(self) -> List[Dict[str, Any]]:
        """Process data and generate FHIR resources"""
        if self.data is None:
            print("❌ No data loaded. Please load Excel data or enter user input first.")
            return []
        
        fhir_resources = []
        
        print(f"\n🔄 Processing {len(self.data)} rows to FHIR resources...")
        
        for index, row in self.data.iterrows():
            print(f"Processing row {index + 1}/{len(self.data)}")
            
            try:
                # Always generate Patient resource
                patient_resource = self.generate_patient_resource(row)
                fhir_resources.append(patient_resource)
                
                # Generate Observation if relevant data exists
                if any(col in self.data.columns for col in ['observation_name', 'value', 'unit']):
                    if pd.notna(row.get('observation_name')) and str(row.get('observation_name')).strip():
                        observation_resource = self.generate_observation_resource(row)
                        fhir_resources.append(observation_resource)
                
                # Generate Condition if relevant data exists
                if any(col in self.data.columns for col in ['condition_name', 'snomed_code']):
                    if pd.notna(row.get('condition_name')) and str(row.get('condition_name')).strip():
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
        
        print(f"\n�� FHIR Resources Summary:")
        print(f"Total resources: {len(self.fhir_resources)}")
        for resource_type, count in resource_types.items():
            print(f"  - {resource_type}: {count}")

def main():
    """Main function with menu options"""
    print("🏥 Enhanced FHIR Module - Excel & User Input to FHIR Converter")
    print("=" * 70)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Process Excel file")
        print("2. Enter data manually")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Excel file processing
            excel_file = "mapping 4.xlsx"
            if not os.path.exists(excel_file):
                print(f"❌ Excel file '{excel_file}' not found!")
                continue
            
            fhir_module = FHIRModule(excel_file)
            if fhir_module.load_excel_data():
                fhir_resources = fhir_module.process_data_to_fhir()
                if fhir_resources:
                    fhir_module.print_summary()
                    fhir_module.save_fhir_bundle("fhir_bundle_excel.json")
                    fhir_module.save_individual_resources("fhir_resources_excel")
                    print("🎉 Excel processing completed!")
        
        elif choice == "2":
            # User input processing
            fhir_module = FHIRModule()
            if fhir_module.get_user_input():
                if fhir_module.convert_user_input_to_dataframe():
                    fhir_resources = fhir_module.process_data_to_fhir()
                    if fhir_resources:
                        fhir_module.print_summary()
                        fhir_module.save_fhir_bundle("fhir_bundle_user.json")
                        fhir_module.save_individual_resources("fhir_resources_user")
                        print("🎉 User input processing completed!")
        
        elif choice == "3":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
