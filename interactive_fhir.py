#!/usr/bin/env python3
"""
Simple Interactive FHIR Data Entry
"""

from worker_enhanced import FHIRModule

def quick_patient_entry():
    """Quick patient entry function"""
    print("🏥 Quick Patient Entry")
    print("=" * 30)
    
    fhir_module = FHIRModule()
    
    # Get basic patient info
    print("Enter patient information:")
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    gender = input("Gender (male/female/other): ").strip().lower()
    condition = input("Medical Condition: ").strip()
    
    if not first_name or not last_name:
        print("❌ First name and last name are required!")
        return
    
    # Create patient data
    patient_data = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'condition_name': condition,
        'patient_id': f"{first_name.lower()}_{last_name.lower()}"
    }
    
    fhir_module.user_input_data = [patient_data]
    
    if fhir_module.convert_user_input_to_dataframe():
        fhir_resources = fhir_module.process_data_to_fhir()
        if fhir_resources:
            fhir_module.print_summary()
            fhir_module.save_fhir_bundle("quick_patient.json")
            print("✅ Patient data saved to quick_patient.json")

if __name__ == "__main__":
    quick_patient_entry()
