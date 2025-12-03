import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Realistic data pools based on actual insurance standards
DIAGNOSES = [
    'Type 2 Diabetes Mellitus', 'Hypertension', 'Coronary Artery Disease',
    'Acute Bronchitis', 'Pneumonia', 'COPD', 'Asthma',
    'Osteoarthritis', 'Rheumatoid Arthritis', 'Lower Back Pain',
    'Migraine', 'Anxiety Disorder', 'Depression',
    'Chronic Kidney Disease', 'Heart Failure', 'Atrial Fibrillation',
    'Hyperlipidemia', 'Hypothyroidism', 'GERD',
    'Urinary Tract Infection'
]

# ICD-10 codes (matching diagnoses above)
ICD10_CODES = {
    'Type 2 Diabetes Mellitus': 'E11.9',
    'Hypertension': 'I10',
    'Coronary Artery Disease': 'I25.10',
    'Acute Bronchitis': 'J20.9',
    'Pneumonia': 'J18.9',
    'COPD': 'J44.9',
    'Asthma': 'J45.909',
    'Osteoarthritis': 'M19.90',
    'Rheumatoid Arthritis': 'M06.9',
    'Lower Back Pain': 'M54.5',
    'Migraine': 'G43.909',
    'Anxiety Disorder': 'F41.9',
    'Depression': 'F32.9',
    'Chronic Kidney Disease': 'N18.9',
    'Heart Failure': 'I50.9',
    'Atrial Fibrillation': 'I48.91',
    'Hyperlipidemia': 'E78.5',
    'Hypothyroidism': 'E03.9',
    'GERD': 'K21.9',
    'Urinary Tract Infection': 'N39.0'
}

# CPT procedure codes
PROCEDURES = {
    'Office Visit - New Patient': '99203',
    'Office Visit - Established': '99213',
    'Lab - Complete Blood Count': '85025',
    'Lab - Comprehensive Metabolic Panel': '80053',
    'Lab - Lipid Panel': '80061',
    'Lab - HbA1c Test': '83036',
    'X-Ray - Chest': '71046',
    'X-Ray - Lower Back': '72100',
    'CT Scan - Head': '70450',
    'MRI - Brain': '70551',
    'EKG': '93000',
    'Echocardiogram': '93306',
    'Physical Therapy Session': '97110',
    'Psychiatric Evaluation': '90791',
    'Emergency Room Visit': '99284',
    'Ultrasound - Abdominal': '76700',
    'Colonoscopy': '45378',
    'Prescription Medication': 'J3420'
}

SPECIALTIES = [
    'Internal Medicine', 'Cardiology', 'Endocrinology',
    'Pulmonology', 'Orthopedics', 'Neurology',
    'Psychiatry', 'Emergency Medicine', 'Family Medicine',
    'Rheumatology', 'Nephrology', 'Gastroenterology'
]

# Common denial reasons from real insurance claims
DENIAL_REASONS = [
    'Missing prior authorization',
    'Service not covered under plan',
    'Duplicate billing',
    'Missing documentation',
    'Out of network provider',
    'Procedure not medically necessary',
    'Pre-existing condition exclusion',
    'Incorrect billing code',
    'Timely filing limit exceeded',
    'Patient not eligible on service date'
]

FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily',
    'Robert', 'Lisa', 'James', 'Mary', 'William', 'Jennifer',
    'Richard', 'Linda', 'Joseph', 'Patricia', 'Thomas', 'Barbara',
    'Charles', 'Elizabeth', 'Daniel', 'Susan', 'Matthew', 'Jessica'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
    'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson',
    'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris'
]

def generate_date(start_date, end_date):
    """Generate random date between start and end"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def generate_insurance_1_data(n_records=2500):
    """
    Generate data for Insurance Company 1 (e.g., BlueCross BlueShield)
    Schema: More detailed, includes ICD codes
    """
    data = []
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(n_records):
        claim_id = f"BC{str(i+10001).zfill(6)}"
        patient_id = f"P{str(random.randint(1000, 9999))}"
        patient_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        diagnosis = random.choice(DIAGNOSES)
        icd_code = ICD10_CODES[diagnosis]
        
        procedure_name = random.choice(list(PROCEDURES.keys()))
        procedure_code = PROCEDURES[procedure_name]
        
        # Claim amounts vary by procedure type
        base_amount = {
            'Office Visit': random.randint(100, 300),
            'Lab': random.randint(50, 250),
            'X-Ray': random.randint(200, 500),
            'CT Scan': random.randint(800, 1500),
            'MRI': random.randint(1200, 2500),
            'EKG': random.randint(150, 300),
            'Echocardiogram': random.randint(500, 1000),
            'Physical Therapy': random.randint(100, 200),
            'Emergency Room': random.randint(1000, 3000),
            'Colonoscopy': random.randint(1500, 3000),
            'Ultrasound': random.randint(300, 600),
            'Prescription': random.randint(50, 500)
        }
        
        # Determine amount based on procedure
        for key in base_amount:
            if key.lower() in procedure_name.lower():
                claim_amount = base_amount[key]
                break
        else:
            claim_amount = random.randint(100, 500)
        
        # 70% approved, 30% denied
        claim_status = random.choices(['Approved', 'Denied'], weights=[0.70, 0.30])[0]
        denial_reason = random.choice(DENIAL_REASONS) if claim_status == 'Denied' else ''
        
        service_date = generate_date(start_date, end_date)
        provider_specialty = random.choice(SPECIALTIES)
        
        # Insurance 1 specific fields
        member_number = f"MEM{random.randint(100000, 999999)}"
        
        data.append({
            'claim_id': claim_id,
            'patient_id': patient_id,
            'member_number': member_number,
            'patient_name': patient_name,
            'diagnosis': diagnosis,
            'icd_code': icd_code,
            'procedure_name': procedure_name,
            'procedure_code': procedure_code,
            'claim_amount': claim_amount,
            'claim_status': claim_status,
            'denial_reason': denial_reason,
            'service_date': service_date.strftime('%Y-%m-%d'),
            'provider_specialty': provider_specialty
        })
    
    return pd.DataFrame(data)

def generate_insurance_2_data(n_records=2500):
    """
    Generate data for Insurance Company 2 (e.g., Aetna)
    Schema: Different column names, no ICD codes, different date format
    """
    data = []
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(n_records):
        # Different claim ID format
        claim_number = f"AET-{str(i+20001)}"
        
        # Different patient ID format
        subscriber_id = f"SUB{random.randint(10000, 99999)}"
        
        # Different name format (Last, First)
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        patient_full_name = f"{last}, {first}"
        
        diagnosis = random.choice(DIAGNOSES)
        
        procedure_name = random.choice(list(PROCEDURES.keys()))
        cpt_code = PROCEDURES[procedure_name]  # Different column name
        
        # Similar amount logic
        base_amount = {
            'Office Visit': random.randint(100, 300),
            'Lab': random.randint(50, 250),
            'X-Ray': random.randint(200, 500),
            'CT Scan': random.randint(800, 1500),
            'MRI': random.randint(1200, 2500),
            'EKG': random.randint(150, 300),
            'Echocardiogram': random.randint(500, 1000),
            'Physical Therapy': random.randint(100, 200),
            'Emergency Room': random.randint(1000, 3000),
            'Colonoscopy': random.randint(1500, 3000),
            'Ultrasound': random.randint(300, 600),
            'Prescription': random.randint(50, 500)
        }
        
        for key in base_amount:
            if key.lower() in procedure_name.lower():
                billed_amount = base_amount[key]  # Different column name
                break
        else:
            billed_amount = random.randint(100, 500)
        
        # Different status values
        status = random.choices(['PAID', 'REJECTED'], weights=[0.70, 0.30])[0]
        rejection_code = random.choice(DENIAL_REASONS) if status == 'REJECTED' else None
        
        date_of_service = generate_date(start_date, end_date)
        specialty = random.choice(SPECIALTIES)
        
        data.append({
            'claim_number': claim_number,
            'subscriber_id': subscriber_id,
            'patient_full_name': patient_full_name,
            'diagnosis_description': diagnosis,  # Different column name
            'cpt_code': cpt_code,  # Different column name
            'procedure_description': procedure_name,
            'billed_amount': billed_amount,  # Different column name
            'status': status,  # Different values
            'rejection_code': rejection_code,  # Different column name
            'date_of_service': date_of_service.strftime('%m/%d/%Y'),  # Different format
            'specialty': specialty
        })
    
    return pd.DataFrame(data)

def main():
    print("🏥 Generating Insurance Claims Data...")
    print("=" * 50)
    
    # Generate data for both insurance companies
    print("\n📊 Generating Insurance Company 1 (BlueCross-style) data...")
    df_insurance1 = generate_insurance_1_data(2500)
    
    print("📊 Generating Insurance Company 2 (Aetna-style) data...")
    df_insurance2 = generate_insurance_2_data(2500)
    
    # Save to CSV
    insurance1_file = 'insurance_company_1_claims.csv'
    insurance2_file = 'insurance_company_2_claims.csv'
    
    df_insurance1.to_csv(insurance1_file, index=False)
    df_insurance2.to_csv(insurance2_file, index=False)
    
    print("\n✅ Data generation complete!")
    print("=" * 50)
    print(f"\n📁 Files created:")
    print(f"   • {insurance1_file} ({len(df_insurance1)} records)")
    print(f"   • {insurance2_file} ({len(df_insurance2)} records)")
    
    print("\n📋 Schema Differences:")
    print("\nInsurance 1 columns:")
    print(f"   {list(df_insurance1.columns)}")
    print("\nInsurance 2 columns:")
    print(f"   {list(df_insurance2.columns)}")
    
    print("\n📊 Sample Data Preview:")
    print("\n--- Insurance Company 1 (First 2 rows) ---")
    print(df_insurance1.head(2).to_string())
    
    print("\n--- Insurance Company 2 (First 2 rows) ---")
    print(df_insurance2.head(2).to_string())
    
    print("\n📈 Statistics:")
    print(f"\nInsurance 1:")
    print(f"   Approved: {len(df_insurance1[df_insurance1['claim_status']=='Approved'])}")
    print(f"   Denied: {len(df_insurance1[df_insurance1['claim_status']=='Denied'])}")
    
    print(f"\nInsurance 2:")
    print(f"   PAID: {len(df_insurance2[df_insurance2['status']=='PAID'])}")
    print(f"   REJECTED: {len(df_insurance2[df_insurance2['status']=='REJECTED'])}")

if __name__ == "__main__":
    main()

