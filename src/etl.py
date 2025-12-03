import pandas as pd
import os
from datetime import datetime

def process_bronze_to_silver():
    print("🔄 Processing Bronze to Silver...")
    
    # Load Bronze Data
    df1 = pd.read_csv('data/bronze/insurance_company_1_claims.csv')
    df2 = pd.read_csv('data/bronze/insurance_company_2_claims.csv')
    
    # Normalize Company 1
    # Columns: claim_id, patient_id, member_number, patient_name, diagnosis, icd_code, procedure_name, procedure_code, claim_amount, claim_status, denial_reason, service_date, provider_specialty
    df1_silver = df1.rename(columns={
        'procedure_name': 'procedure',
        'provider_specialty': 'specialty'
    })
    df1_silver['source'] = 'Company_1'
    
    # Normalize Company 2
    # Columns: claim_number, subscriber_id, patient_full_name, diagnosis_description, cpt_code, procedure_description, billed_amount, status, rejection_code, date_of_service, specialty
    df2_silver = df2.rename(columns={
        'claim_number': 'claim_id',
        'subscriber_id': 'patient_id',
        'patient_full_name': 'patient_name',
        'diagnosis_description': 'diagnosis',
        'procedure_description': 'procedure',
        'billed_amount': 'claim_amount',
        'status': 'claim_status',
        'rejection_code': 'denial_reason',
        'date_of_service': 'service_date',
        'cpt_code': 'procedure_code'
    })
    
    # Standardize Values for Company 2
    status_map = {'PAID': 'Approved', 'REJECTED': 'Denied'}
    df2_silver['claim_status'] = df2_silver['claim_status'].map(status_map)
    
    # Standardize Date Format to YYYY-MM-DD
    df2_silver['service_date'] = pd.to_datetime(df2_silver['service_date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
    
    df2_silver['source'] = 'Company_2'
    
    # Combine
    common_columns = ['claim_id', 'patient_id', 'patient_name', 'diagnosis', 'procedure', 'claim_amount', 'claim_status', 'denial_reason', 'service_date', 'specialty', 'source']
    
    # Ensure all columns exist
    for col in common_columns:
        if col not in df1_silver.columns:
            df1_silver[col] = None
        if col not in df2_silver.columns:
            df2_silver[col] = None
            
    df_silver = pd.concat([df1_silver[common_columns], df2_silver[common_columns]], ignore_index=True)
    
    # Fill NA denial reasons with empty string
    df_silver['denial_reason'] = df_silver['denial_reason'].fillna('')
    
    # Save Silver
    output_path = 'data/silver/claims_normalized.csv'
    df_silver.to_csv(output_path, index=False)
    print(f"✅ Silver data saved to {output_path} ({len(df_silver)} records)")
    return df_silver

def process_silver_to_gold(df_silver):
    print("\n🔄 Processing Silver to Gold...")
    
    df_gold = df_silver.copy()
    
    # Create Text Representation for RAG
    # "Claim [ID]: Patient [Name] (ID: [ID]) - [Procedure] for [Diagnosis]. Status: [Status]. Reason: [Reason]. Date: [Date]."
    
    def create_text(row):
        text = f"Claim {row['claim_id']}: Patient {row['patient_name']} (ID: {row['patient_id']}) received {row['procedure']} for {row['diagnosis']} on {row['service_date']}. "
        text += f"Amount: ${row['claim_amount']}. Status: {row['claim_status']}."
        if row['claim_status'] == 'Denied':
            text += f" Denial Reason: {row['denial_reason']}."
        text += f" Specialty: {row['specialty']}."
        return text

    df_gold['text_representation'] = df_gold.apply(create_text, axis=1)
    
    # Save Gold
    output_path = 'data/gold/claims_master.csv'
    df_gold.to_csv(output_path, index=False)
    print(f"✅ Gold data saved to {output_path}")
    
    # Also save a sample for quick inspection
    print("\nSample Gold Data (Text Representation):")
    print(df_gold['text_representation'].head(2).values)

if __name__ == "__main__":
    df_silver = process_bronze_to_silver()
    process_silver_to_gold(df_silver)
