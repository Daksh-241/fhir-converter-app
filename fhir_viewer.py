import json
import pandas as pd

def view_fhir_bundle(bundle_file="fhir_bundle.json"):
    with open(bundle_file, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    print("FHIR Bundle Information")
    print("=" * 50)
    print(f"Resource Type: {bundle['resourceType']}")
    print(f"Bundle ID: {bundle['id']}")
    print(f"Type: {bundle['type']}")
    print(f"Timestamp: {bundle['timestamp']}")
    print(f"Total Entries: {len(bundle['entry'])}")
    
    print("\nFirst 5 Resources:")
    for i, entry in enumerate(bundle['entry'][:5]):
        resource = entry['resource']
        print(f"\n{i+1}. {resource['resourceType']} (ID: {resource['id']})")

def export_to_csv():
    with open("fhir_bundle.json", 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    data = []
    for entry in bundle['entry']:
        resource = entry['resource']
        row = {
            'Resource_Type': resource['resourceType'],
            'ID': resource['id'],
            'Created_Date': bundle['timestamp']
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv('fhir_export.csv', index=False)
    print(f"Exported {len(data)} records to fhir_export.csv")
    return df

if __name__ == "__main__":
    print("FHIR Data Viewer")
    print("=" * 30)
    view_fhir_bundle()
    print("\nExporting to CSV...")
    df = export_to_csv()
    print("\nFirst 5 rows of CSV:")
    print(df.head())
