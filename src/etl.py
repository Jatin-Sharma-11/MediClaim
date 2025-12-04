import pandas as pd
import os
from datetime import datetime

def normalize_company_1(df):
    # Columns: claim_id, patient_id, member_number, patient_name, diagnosis, icd_code, procedure_name, procedure_code, claim_amount, claim_status, denial_reason, service_date, provider_specialty
    df_silver = df.rename(columns={
        'procedure_name': 'procedure',
        'provider_specialty': 'specialty'
    })
    df_silver['source'] = 'Company_1'
    return df_silver

def normalize_company_2(df):
    # Columns: claim_number, subscriber_id, patient_full_name, diagnosis_description, cpt_code, procedure_description, billed_amount, status, rejection_code, date_of_service, specialty
    df_silver = df.rename(columns={
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
    df_silver['claim_status'] = df_silver['claim_status'].map(status_map).fillna(df_silver['claim_status'])
    
    # Standardize Date Format to YYYY-MM-DD
    # Handle potential different date formats
    df_silver['service_date'] = pd.to_datetime(df_silver['service_date'], format='%m/%d/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
    
    df_silver['source'] = 'Company_2'
    return df_silver

def normalize_generic(df, source_name='Custom_Upload'):
    """
    Attempts to normalize a generic CSV. 
    Assumes columns might already be named correctly or close to it.
    """
    # Map common variations to standard names
    column_map = {
        'ClaimID': 'claim_id', 'Claim_ID': 'claim_id', 'ID': 'claim_id',
        'PatientID': 'patient_id', 'Patient_ID': 'patient_id',
        'PatientName': 'patient_name', 'Patient_Name': 'patient_name', 'Name': 'patient_name',
        'Diagnosis': 'diagnosis', 'DiagnosisCode': 'icd_code',
        'Procedure': 'procedure', 'ProcedureCode': 'procedure_code',
        'Amount': 'claim_amount', 'ClaimAmount': 'claim_amount', 'Cost': 'claim_amount',
        'Status': 'claim_status', 'ClaimStatus': 'claim_status',
        'Reason': 'denial_reason', 'DenialReason': 'denial_reason',
        'Date': 'service_date', 'ServiceDate': 'service_date', 'DateOfService': 'service_date',
        'Specialty': 'specialty', 'ProviderSpecialty': 'specialty'
    }
    
    df_silver = df.rename(columns=column_map)
    df_silver['source'] = source_name
    return df_silver

def process_bronze_to_silver(upload_files=None):
    """
    Args:
        upload_files: List of tuples (filename, DataFrame) or None. 
                      If None, loads default files from disk.
    """
    print("🔄 Processing Bronze to Silver...")
    
    processed_dfs = []
    
    if upload_files:
        # Process uploaded files
        for filename, df in upload_files:
            print(f"Processing uploaded file: {filename}")
            # Simple heuristic to decide normalization or just generic
            # In a real app, user might map columns. Here we try generic.
            df_norm = normalize_generic(df, source_name=filename)
            processed_dfs.append(df_norm)
    else:
        # Load Default Bronze Data
        try:
            df1 = pd.read_csv('data/bronze/insurance_company_1_claims.csv')
            processed_dfs.append(normalize_company_1(df1))
        except FileNotFoundError:
            print("Warning: Default Company 1 data not found.")

        try:
            df2 = pd.read_csv('data/bronze/insurance_company_2_claims.csv')
            processed_dfs.append(normalize_company_2(df2))
        except FileNotFoundError:
            print("Warning: Default Company 2 data not found.")
    
    if not processed_dfs:
        print("❌ No data to process.")
        return pd.DataFrame()

    # Combine
    common_columns = ['claim_id', 'patient_id', 'patient_name', 'diagnosis', 'procedure', 'claim_amount', 'claim_status', 'denial_reason', 'service_date', 'specialty', 'source']
    
    final_dfs = []
    for df in processed_dfs:
        # Ensure all columns exist
        for col in common_columns:
            if col not in df.columns:
                df[col] = None
        final_dfs.append(df[common_columns])
            
    df_silver = pd.concat(final_dfs, ignore_index=True)
    
    # Fill NA denial reasons with empty string
    df_silver['denial_reason'] = df_silver['denial_reason'].fillna('')
    
    # Save Silver
    os.makedirs('data/silver', exist_ok=True)
    output_path = 'data/silver/claims_normalized.csv'
    df_silver.to_csv(output_path, index=False)
    print(f"✅ Silver data saved to {output_path} ({len(df_silver)} records)")
    return df_silver

def process_silver_to_gold(df_silver):
    print("\n🔄 Processing Silver to Gold...")
    
    if df_silver.empty:
        print("❌ Silver dataframe is empty. Skipping Gold processing.")
        return pd.DataFrame()

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
    os.makedirs('data/gold', exist_ok=True)
    output_path = 'data/gold/claims_master.csv'
    df_gold.to_csv(output_path, index=False)
    print(f"✅ Gold data saved to {output_path}")
    
    # Also save a sample for quick inspection
    print("\nSample Gold Data (Text Representation):")
    print(df_gold['text_representation'].head(2).values)
    return df_gold

if __name__ == "__main__":
    df_silver = process_bronze_to_silver()
    process_silver_to_gold(df_silver)
