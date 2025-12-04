<div align="center">
  <img src="public/vanish_banner.png" alt="Vanish Banner" width="100%" />

  # ✨ Vanish: Talk to Your Data
  
  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
  [![ChromaDB](https://img.shields.io/badge/ChromaDB-Search-green?style=for-the-badge)](https://www.trychroma.com/)
  [![Groq](https://img.shields.io/badge/Groq-LPU%20Inference-orange?style=for-the-badge)](https://groq.com/)

  **Turn your insurance claims data into actionable insights using Natural Language.**
  
  [Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage)

</div>

---

## 🚀 Overview

**Vanish** is a powerful AI-driven analytics platform that bridges the gap between raw data and human understanding. By leveraging **Large Language Models (LLMs)** via Groq, **Vector Search (RAG)**, and **Text-to-SQL** capabilities, Vanish allows users to query complex insurance claims datasets as if they were talking to a colleague.

Whether you need to find specific denied claims for a diagnosis or aggregate millions of dollars in payouts, Vanish understands your intent and fetches the answer instantly.

---

## 🏗 Architecture

Vanish employs a dual-pipeline architecture to handle both structured aggregation and semantic search.

<div align="center">
  <img src="public/detailed_system_architecture.png" alt="Detailed System Architecture" width="800" />
</div>

### System Flow
The system processes data through a robust **ETL (Extract, Transform, Load)** pipeline before making it available for querying. The diagram above illustrates the complete transaction flow from user query to API calls and response generation.

```mermaid
graph TD
    subgraph "Data Ingestion Layer"
        A[Raw CSV Files] -->|Normalize| B(Silver Layer)
        B -->|Enrich| C(Gold Layer)
    end

    subgraph "Storage Layer"
        C -->|Structured Data| D[(DuckDB)]
        C -->|Text Representation| E[(ChromaDB Vector Store)]
    end

    subgraph "Intelligence Layer"
        User[User Query] --> Router{Query Router}
        Router -->|Aggregation/Stats| T2S[Text2SQL Pipeline]
        Router -->|Semantic Search| RAG[RAG Pipeline]
        
        T2S -->|Generate SQL| LLM[Groq LLM]
        LLM -->|SQL Query| D
        D -->|Results| Viz[Visualization Engine]
        
        RAG -->|Embed Query| Embed[Embedding Model]
        Embed -->|Vector Search| E
        E -->|Context| LLM
        LLM -->|Natural Answer| Response
    end

    Viz --> UI[Streamlit Dashboard]
    Response --> UI
```

---

## ✨ Features

### 🧠 1. Text-to-SQL Pipeline
*For precise numbers, aggregations, and filtering.*
- Converts natural language (e.g., *"Show me total claims for Diabetes in 2023"*) into executable **DuckDB SQL**.
- Handles complex logic like case insensitivity, synonyms (Approved/Paid), and date filtering.
- **Self-Correction**: Automatically detects SQL errors and provides feedback.

### 🔍 2. RAG (Retrieval Augmented Generation) Pipeline
*For context, reasoning, and semantic understanding.*

<div align="center">
  <img src="public/rag_diagram.png" alt="RAG Pipeline Diagram" width="700" />
</div>

- Indexes claims as text documents using **ChromaDB**.
- Retrieves relevant claims based on meaning, not just keywords.
- Generates human-like explanations for *why* a claim might have been denied.

### 📊 3. Interactive Visualizations
- Automatically generates charts (Bar, Line, Pie) based on the data returned.
- seamless integration with Streamlit for a responsive UI.

### 🔄 4. Robust ETL
- **Bronze -> Silver -> Gold** architecture.
- Normalizes disparate data sources (different column names, formats) into a unified schema.

---

## 🛠 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/vanish.git
   cd vanish
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## 🖥 Usage

1. **Run the Application**
   ```bash
   streamlit run app.py
   ```

2. **Load Data**
   - Use the sidebar to upload your CSV files or use the sample data.
   - Click **"Process Data"** to run the ETL pipeline.

3. **Ask Questions!**
   - Select **Text2SQL** for questions like: *"How many claims were denied?"*
   - Select **RAG** for questions like: *"Why was patient John Doe's claim rejected?"*

---

## 📦 Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | Streamlit | Interactive web interface |
| **LLM** | Groq (Llama 3) | High-speed inference for SQL & Chat |
| **Database** | DuckDB | High-performance analytical SQL engine |
| **Vector DB** | ChromaDB | Embedding storage for semantic search |
| **Embeddings** | SentenceTransformers | `all-MiniLM-L6-v2` for text encoding |
| **Data Proc** | Pandas | Data manipulation and ETL |

---

<div align="center">
  <sub>Built with ❤️ by the Vanish Team</sub>
</div>
