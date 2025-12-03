import streamlit as st
import pandas as pd
from src.rag_pipeline import RAGPipeline
from src.text2sql_pipeline import Text2SQLPipeline
import os

# Page Config
st.set_page_config(
    page_title="Claims Query Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize Pipelines (Cached)
@st.cache_resource
def get_rag_pipeline():
    rag = RAGPipeline()
    # Ensure data is loaded (in a real app, this might be separate)
    if os.path.exists('data/gold/claims_master.csv'):
        rag.ingest('data/gold/claims_master.csv')
    return rag

@st.cache_resource
def get_text2sql_pipeline():
    t2s = Text2SQLPipeline()
    if os.path.exists('data/gold/claims_master.csv'):
        t2s.load_data('data/gold/claims_master.csv')
    return t2s

try:
    rag = get_rag_pipeline()
    t2s = get_text2sql_pipeline()
except Exception as e:
    st.error(f"Error initializing pipelines: {e}")
    st.stop()

# UI Layout
st.title("🏥 RAG-Powered Claims Query Assistant")
st.markdown("Ask questions about insurance claims using **Natural Language**.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    query_method = st.radio(
        "Query Method",
        ["RAG (Vector Search)", "Text2SQL (Structured Query)"],
        help="Choose 'RAG' for semantic search over text descriptions, or 'Text2SQL' for precise aggregation and filtering."
    )
    
    st.markdown("---")
    st.markdown("### Data Info")
    if os.path.exists('data/gold/claims_master.csv'):
        df = pd.read_csv('data/gold/claims_master.csv')
        st.info(f"Loaded {len(df)} claims.")
    else:
        st.warning("Data not found.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"])
        if "sql" in message:
            st.code(message["sql"], language="sql")

# User Input
if prompt := st.chat_input("Ask a question (e.g., 'Show me denied claims for diabetes')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if query_method == "Text2SQL (Structured Query)":
                    # Text2SQL Flow
                    sql_query = t2s.generate_sql(prompt)
                    st.markdown(f"**Generated SQL:**")
                    st.code(sql_query, language="sql")
                    
                    results_df = t2s.execute_sql(sql_query)
                    
                    if 'error' in results_df.columns:
                        st.error(f"SQL Execution Error: {results_df['error'].iloc[0]}")
                        response_text = "Failed to execute query."
                    elif not results_df.empty:
                        st.dataframe(results_df)
                        response_text = f"Found {len(results_df)} records."
                    else:
                        response_text = "No results found."
                        
                    st.markdown(response_text)
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sql": sql_query,
                        "dataframe": results_df if not results_df.empty else None
                    })
                    
                else:
                    # RAG Flow
                    retrieval_results = rag.query(prompt)
                    answer = rag.generate_answer(prompt, retrieval_results)
                    
                    st.markdown(answer)
                    
                    with st.expander("View Source Documents"):
                        for doc in retrieval_results['documents'][0]:
                            st.markdown(f"- {doc}")
                            
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
