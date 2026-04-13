# Agentic Trading Bot

## 1. Overview

An AI-powered stock market chatbot built with an agentic architecture. Users can upload stock market documents (PDFs, DOCX) to build a custom knowledge base, then ask natural language questions about stocks, financials, and market trends. The bot intelligently routes queries through multiple tools — a document retriever, a financial data API, and a live web search — to provide accurate, context-aware answers.

**Key capabilities:**
- Upload and ingest stock market research documents into a vector database
- Ask questions about stocks, financial data, and market trends in natural language
- Agent autonomously decides which tool(s) to use per query (RAG, live financials, or web search)
- Streamlit-based chat UI with a FastAPI backend

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — `llama-3.3-70b-versatile` |
| Embeddings | Google Gemini — `gemini-embedding-001` |
| Agent Framework | LangGraph (StateGraph with tool nodes) |
| Tools | Pinecone RAG retriever, Polygon Financials API, Tavily Web Search |
| Vector Database | Pinecone (Serverless, AWS us-east-1, cosine similarity) |
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| Document Loaders | PyPDF, Docx2txt |
| Config | YAML (`config/config.yaml`) |
| Environment | Python 3.10, Conda |

---

## 3. How It Works (Architecture)

### High-Level Flow

```
User (Streamlit UI)
       │
       ▼
  FastAPI Backend
  ┌─────────────────────────────────────┐
  │  POST /upload  →  DataIngestion     │
  │    - Load PDF / DOCX                │
  │    - Chunk text (1000 chars, 200    │
  │      overlap)                       │
  │    - Embed with Google Gemini       │
  │    - Store in Pinecone vector DB    │
  │                                     │
  │  POST /query   →  LangGraph Agent   │
  │    - Receive user question          │
  │    - LLM decides which tool to use  │
  │       ├── retriever_tool  (RAG)     │
  │       ├── financials_tool (Polygon) │
  │       └── tavilytool     (Web)     │
  │    - Return final answer            │
  └─────────────────────────────────────┘
       │
       ▼
  Response → Streamlit Chat UI
```

### Agent Decision Loop (LangGraph)

```
START
  │
  ▼
chatbot node  ←──────────────────────┐
  │                                  │
  ▼ (tools_condition)                │
  ├── No tool needed → END           │
  └── Tool call needed               │
        │                            │
        ▼                            │
   tools node                        │
   (retriever / financials / tavily) │
        │                            │
        └────────────────────────────┘
```

The agent automatically loops between the chatbot and tool nodes until a final answer is produced — no fixed routing, fully dynamic.

### Component Breakdown

| Component | File | Role |
|---|---|---|
| FastAPI app | `main.py` | API endpoints (`/upload`, `/query`) |
| Agent graph | `agent/workflow.py` | LangGraph StateGraph builder |
| Tools | `toolkit/tools.py` | RAG retriever, Polygon, Tavily |
| Data ingestion | `data_ingestion/ingestion_pipeline.py` | Document loading → chunking → Pinecone |
| Model loader | `utils/model_loaders.py` | Loads Groq LLM and Gemini embeddings |
| Config | `config/config.yaml` | Centralized settings (model names, top-k, etc.) |
| Streamlit UI | `streamlit_ui.py` | Chat interface + document upload sidebar |

---

## 4. Setup Steps

### Prerequisites
- Python 3.10
- Conda (recommended) or venv
- API keys for all required services (see below)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Shyam-AI-Engineer/Agentic-Trading-Bot.git
cd Agentic-Trading-Bot
```

### Step 2 — Create and Activate the Environment

**Using Conda (recommended):**
```bash
conda create -p env python=3.10 -y

# On Windows CMD:
conda activate <full_path_to_env>

# On Git Bash / Linux / Mac:
source activate ./env
```

**Using venv (alternative):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux / Mac:
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

Create a `.env` file in the project root and add the following keys:

```env
POLYGON_API_KEY=your_polygon_api_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

| Key | Purpose | Get it from |
|---|---|---|
| `POLYGON_API_KEY` | Stock financial data | https://polygon.io |
| `GOOGLE_API_KEY` | Gemini LLM + embeddings | https://aistudio.google.com |
| `TAVILY_API_KEY` | Live web search | https://tavily.com |
| `GROQ_API_KEY` | Fast LLM inference (Llama 3.3) | https://console.groq.com |
| `PINECONE_API_KEY` | Vector database | https://pinecone.io |

### Step 5 — Run the Backend (FastAPI)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: `http://localhost:8000`
Interactive docs at: `http://localhost:8000/docs`

### Step 6 — Run the Frontend (Streamlit)

In a separate terminal (with the environment activated):

```bash
streamlit run streamlit_ui.py
```

UI will open at: `http://localhost:8501`

---

## 5. API Endpoints

### `POST /upload`
Upload stock market PDF or DOCX files to build the knowledge base.

**Request:** `multipart/form-data` with one or more files

**Response:**
```json
{ "message": "Files successfully processed and stored." }
```

### `POST /query`
Ask a question to the trading bot.

**Request:**
```json
{ "question": "What is the revenue of Apple for Q3 2024?" }
```

**Response:**
```json
{ "answer": "Apple's revenue for Q3 2024 was $85.8 billion..." }
```

---

## 6. Configuration

All model and retriever settings are managed in `config/config.yaml`:

```yaml
vector_db:
  index_name: "trading-bot"       # Pinecone index name

retriever:
  top_k: 3                        # Number of chunks retrieved
  score_threshold: 0.5            # Minimum similarity score

embedding_model:
  model_name: "gemini-embedding-001"

llm:
  groq:
    model_name: "llama-3.3-70b-versatile"

tools:
  tavily:
    max_results: 5
```

---

## 7. Project Structure

```
Agentic-Trading-Bot/
├── agent/
│   └── workflow.py          # LangGraph agent (StateGraph)
├── config/
│   └── config.yaml          # Centralized config
├── custom_logging/          # Logging utilities
├── data_ingestion/
│   └── ingestion_pipeline.py  # PDF/DOCX → Pinecone pipeline
├── data_models/
│   └── models.py            # Pydantic request/response models
├── exception/
│   └── exceptions.py        # Custom exception handler
├── fallback_data/           # Fallback responses
├── prompt_library/          # Prompt templates
├── toolkit/
│   └── tools.py             # LangChain tools (RAG, Polygon, Tavily)
├── utils/
│   ├── config_loader.py     # YAML config loader
│   └── model_loaders.py     # LLM + embedding loader
├── main.py                  # FastAPI application
├── streamlit_ui.py          # Streamlit chat frontend
├── requirements.txt
├── setup.py
└── .env                     # API keys (not committed)
```

---

## 8. Notes

- The Pinecone index is created automatically on first upload if it does not exist (dimension: 3072, metric: cosine, AWS us-east-1).
- The agent uses Groq for fast LLM inference and Google Gemini solely for embeddings.
- Do not commit your `.env` file — add it to `.gitignore`.
- CORS is currently set to `allow_origins=["*"]`; restrict this to specific origins in production.
