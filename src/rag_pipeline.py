import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict

class RAGPipeline:
    def __init__(self, collection_name="insurance_claims", persist_directory="chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        
    def ingest(self, csv_path: str):
        print(f"📥 Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Check if already indexed
        if self.collection.count() > 0:
            print(f"⚠️ Collection {self.collection_name} already has {self.collection.count()} documents. Skipping ingestion.")
            return

        documents = df['text_representation'].tolist()
        ids = [str(i) for i in range(len(df))]
        metadatas = df.drop(columns=['text_representation']).to_dict('records')
        
        # Convert all metadata values to strings to avoid ChromaDB issues with None/Int mix
        for meta in metadatas:
            for k, v in meta.items():
                meta[k] = str(v)

        print("🧠 Generating embeddings...")
        embeddings = self.model.encode(documents).tolist()
        
        print("💾 Storing in Vector DB...")
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Indexed {len(documents)} documents.")

    def query(self, query_text: str, n_results: int = 5) -> Dict:
        print(f"🔍 Querying RAG for: '{query_text}'")
        query_embedding = self.model.encode([query_text]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results

    def generate_answer(self, query_text: str, context_results: Dict) -> str:
        from groq import Groq
        import os
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets["GROQ_API_KEY"]
            except:
                pass
                
        client = Groq(api_key=api_key)
        
        context_str = "\n\n".join(context_results['documents'][0])
        
        prompt = f"""
        Context information is below.
        ---------------------
        {context_str}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {query_text}
        Answer:
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering questions based on provided insurance claims data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        return completion.choices[0].message.content

if __name__ == "__main__":
    # Test
    rag = RAGPipeline()
    if os.path.exists('data/gold/claims_master.csv'):
        rag.ingest('data/gold/claims_master.csv')
        results = rag.query("denied claims for diabetes")
        print("Retrieval Results:", results)
        
        answer = rag.generate_answer("Why were claims for diabetes denied?", results)
        print("\nGenerated Answer:", answer)
    else:
        print("❌ Gold data not found. Run ETL first.")
