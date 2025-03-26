# RAG CSV Analyzer

A FastAPI-based application that enables users to upload and query CSV files using Retrieval-Augmented Generation (RAG) with a lightweight language model.

## Features
- CSV file upload and analysis
- RAG-powered querying using DistilGPT2 (82M parameters)
- MongoDB storage for file management
- Streamlit UI for easy interaction
- Lightweight and efficient processing

## Technical Stack
- **LLM**: DistilGPT2 (82M parameters) with float16 optimization
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Backend**: FastAPI
- **Database**: MongoDB
- **Frontend**: Streamlit

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB server

3. Set environment variables:
```bash
cp .env.example .env
# Required settings:
# MONGODB_URI=mongodb://localhost:27017/
# DATABASE_NAME=rag_csv_db
```

4. Run the API:
```bash
uvicorn app.main:app --reload
```

5. Run Streamlit UI:
```bash
streamlit run streamlit_app.py
```

## API Documentation
- POST /upload - Upload CSV files (supports both file upload and file path)
- GET /files - List available files in database
- POST /query - Query CSV data using natural language
- DELETE /file/{file_id} - Delete a file from database

## Query Examples
The system can answer questions like:
- "What is the average value in column X?"
- "Show me trends in the data"
- "Summarize the contents of this CSV"
- "Find the maximum/minimum values"

## Performance Notes
- Uses float16 precision for reduced memory usage
- Processes only first 10 rows for quick analysis
- Optimized for CPU usage with minimal memory footprint

## Deployment
The application is configured for Heroku deployment.
```bash
git push heroku main
```

## Limitations
- Analysis limited to first 10 rows for performance
- Responses are concise due to lightweight model
- Best suited for simple analytical queries
