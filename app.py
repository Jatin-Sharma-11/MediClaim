import streamlit as st
import pandas as pd
from src.rag_pipeline import RAGPipeline
from src.text2sql_pipeline import Text2SQLPipeline
from src.etl import process_bronze_to_silver, process_silver_to_gold
from src.visualization import visualize_query_results
import os

# Page Config
st.set_page_config(
    page_title="Vanish",
    page_icon="✨",
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

# Function to reload pipelines after data update
def reload_pipelines():
    st.cache_resource.clear()
    st.session_state.rag = get_rag_pipeline()
    st.session_state.t2s = get_text2sql_pipeline()
    st.success("Pipelines reloaded with new data!")

# Check for API Key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        pass

if not api_key:
    st.error("🚨 GROQ_API_KEY not found! Please set it in your environment variables or Streamlit Secrets.")
    st.info("To set in Streamlit Secrets: Go to App Settings -> Secrets and add `GROQ_API_KEY = 'your_key'`")
    st.stop()

try:
    rag = get_rag_pipeline()
    t2s = get_text2sql_pipeline()
except Exception as e:
    st.error(f"Error initializing pipelines: {e}")
    st.stop()

# UI Layout
st.title("✨ Vanish: Talk to your Data")
st.markdown("Ask questions about insurance claims using **Natural Language**.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Data Source Selection
    st.subheader("Data Source")
    data_source = st.radio("Choose Data Source", ["Sample Data", "Upload Your Own Data"])
    
    if data_source == "Upload Your Own Data":
        uploaded_files = st.file_uploader("Upload CSV Files", type=['csv'], accept_multiple_files=True)
        if uploaded_files:
            if st.button("Process Data"):
                with st.spinner("Processing uploaded files..."):
                    # Prepare files for ETL
                    files_to_process = []
                    for uploaded_file in uploaded_files:
                        # Read into DataFrame
                        df = pd.read_csv(uploaded_file)
                        files_to_process.append((uploaded_file.name, df))
                    
                    # Run ETL
                    try:
                        df_silver = process_bronze_to_silver(files_to_process)
                        process_silver_to_gold(df_silver)
                        st.success("Data processed successfully!")
                        reload_pipelines()
                    except Exception as e:
                        st.error(f"Error processing data: {e}")
    
    st.markdown("---")
    
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
        if "dataframe" in message and message["dataframe"] is not None:
            st.dataframe(message["dataframe"])
            with st.expander("Visualize Results"):
                visualize_query_results(message["dataframe"])
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
                        df_to_save = None
                    elif not results_df.empty:
                        st.dataframe(results_df)
                        
                        # Visualization
                        with st.expander("Visualize Results", expanded=True):
                            visualize_query_results(results_df)
                            
                        response_text = f"Found {len(results_df)} records."
                        df_to_save = results_df
                    else:
                        response_text = "No results found."
                        df_to_save = None
                        
                    st.markdown(response_text)
                    
                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sql": sql_query,
                        "dataframe": df_to_save
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

