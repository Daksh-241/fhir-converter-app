#!/usr/bin/env python3
"""
Test script for FHIR Module
"""

import os
import json
from worker import FHIRModule

def test_fhir_module():
    """Test the FHIR module functionality"""
    print("🧪 Testing FHIR Module")
    print("=" * 30)
    
    # Test with the Excel file
    excel_file = "mapping 4.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Test file {excel_file} not found!")
        return False
    
    # Initialize FHIR module
    fhir_module = FHIRModule(excel_file)
    
    # Test loading Excel data
    print("1. Testing Excel data loading...")
    if not fhir_module.load_excel_data():
        print("❌ Failed to load Excel data")
        return False
    print("✅ Excel data loaded successfully")
    
    # Test FHIR resource generation
    print("\n2. Testing FHIR resource generation...")
    fhir_resources = fhir_module.process_excel_to_fhir()
    
    if not fhir_resources:
        print("❌ No FHIR resources generated")
        return False
    print(f"✅ Generated {len(fhir_resources)} FHIR resources")
    
    # Test saving FHIR Bundle
    print("\n3. Testing FHIR Bundle saving...")
    if fhir_module.save_fhir_bundle("test_fhir_bundle.json"):
        print("✅ FHIR Bundle saved successfully")
    else:
        print("❌ Failed to save FHIR Bundle")
        return False
    
    # Test saving individual resources
    print("\n4. Testing individual resource saving...")
    if fhir_module.save_individual_resources("test_fhir_resources"):
        print("✅ Individual resources saved successfully")
    else:
        print("❌ Failed to save individual resources")
        return False
    
    # Print summary
    print("\n5. Resource Summary:")
    fhir_module.print_summary()
    
    # Validate JSON structure
    print("\n6. Validating JSON structure...")
    try:
        with open("test_fhir_bundle.json", 'r') as f:
            bundle = json.load(f)
        
        if bundle.get("resourceType") == "Bundle":
            print("✅ FHIR Bundle structure is valid")
        else:
            print("❌ Invalid FHIR Bundle structure")
            return False
            
    except Exception as e:
        print(f"❌ Error validating JSON: {e}")
        return False
    
    print("\n🎉 All tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_fhir_module()
    if success:
        print("\n✅ FHIR Module is working correctly!")
    else:
        print("\n❌ FHIR Module has issues that need to be fixed.")
