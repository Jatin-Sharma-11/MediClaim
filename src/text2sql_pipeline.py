import duckdb
import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class Text2SQLPipeline:
    def __init__(self, db_path=':memory:'):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.con = duckdb.connect(database=db_path)
        
    def load_data(self, csv_path: str, table_name: str = "claims"):
        print(f"📥 Loading data from {csv_path} into DuckDB table '{table_name}'...")
        # DuckDB can query CSV directly, but creating a table is cleaner for repeated queries
        self.con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
        print(f"✅ Data loaded. Schema:")
        print(self.con.execute(f"DESCRIBE {table_name}").fetchdf())

    def generate_sql(self, query_text: str) -> str:
        print(f"🧠 Generating SQL for: '{query_text}'")
        
        # Get schema to inform the LLM
        schema_df = self.con.execute("DESCRIBE claims").fetchdf()
        columns = ", ".join([f"{row['column_name']} ({row['column_type']})" for _, row in schema_df.iterrows()])
        
        prompt = f"""
        You are an expert SQL data analyst.
        Table name: claims
        Columns: {columns}
        
        User Question: {query_text}
        
        Instructions:
        1. Write a valid DuckDB SQL query to answer the question.
        2. Return ONLY the SQL query. No markdown, no explanations.
        3. Do not use LIMIT unless specified.
        4. ALWAYS use ILIKE for string matching to handle case sensitivity (e.g. claim_status ILIKE 'Approved').
        5. Map synonyms to schema values:
           - "accepted" -> 'Approved'
           - "rejected" -> 'Denied'
        6. Be aware that column names are lowercase (e.g., claim_status, diagnosis).
        7. Alias aggregations for readability (e.g. SELECT COUNT(*) AS total_claims ...).
        """
        
        import re
        
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a SQL generator. Output only SQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=200
        )
        
        content = completion.choices[0].message.content.strip()
        
        # Try to find SQL in code blocks first
        match = re.search(r'```sql\n(.*?)\n```', content, re.DOTALL)
        if match:
            sql_query = match.group(1).strip()
        else:
            # Fallback: assume the whole text is SQL if no code blocks, 
            # but remove any markdown formatting just in case
            sql_query = content.replace('```sql', '').replace('```', '').strip()
            
        return sql_query

    def execute_sql(self, sql_query: str) -> pd.DataFrame:
        print(f"🚀 Executing SQL: {sql_query}")
        try:
            result = self.con.execute(sql_query).fetchdf()
            return result
        except Exception as e:
            print(f"❌ SQL Execution Failed: {e}")
            return pd.DataFrame({'error': [str(e)]})

if __name__ == "__main__":
    # Test
    t2s = Text2SQLPipeline()
    if os.path.exists('data/gold/claims_master.csv'):
        t2s.load_data('data/gold/claims_master.csv')
        sql = t2s.generate_sql("Show me 5 denied claims for diabetes")
        print(f"Generated SQL: {sql}")
        res = t2s.execute_sql(sql)
        print(res)
    else:
        print("❌ Gold data not found.")
