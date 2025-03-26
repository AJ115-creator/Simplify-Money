from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
from .models import *
from .database import store_file_metadata, get_file, delete_file, get_all_files
from .rag import query_csv
from .utils import generate_file_id, read_csv_file, process_uploaded_file

app = FastAPI(title="RAG CSV Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for predefined files
DATA_DIR = "data/"

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(None), file_path: str = None):
    if not file and not file_path:
        raise HTTPException(status_code=400, detail="Provide a file or file path")
    
    file_id = generate_file_id()
    if file:
        content = process_uploaded_file(file.file)
        file_name = file.filename
    elif file_path:
        if os.path.exists(file_path):
            content = read_csv_file(file_path)
            file_name = os.path.basename(file_path)
        else:
            raise HTTPException(status_code=400, detail="File path does not exist")
    
    try:
        store_file_metadata(file_id, file_name, content)
        return {"file_id": file_id, "message": "Upload successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

@app.get("/files", response_model=FilesResponse)
async def list_files():
    try:
        files = get_all_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_file(request: QueryRequest):
    if not request.file_id or not request.query:
        raise HTTPException(status_code=400, detail="Missing file_id or query")
    
    file_data = get_file(request.file_id)
    if not file_data:
        raise HTTPException(
            status_code=404, 
            detail=f"File not found with ID: {request.file_id}. Please check if the ID is correct."
        )
    
    if not file_data.get("document"):
        raise HTTPException(
            status_code=400, 
            detail="File exists but contains no data"
        )
    
    response = query_csv(file_data["document"], request.query)
    return {"response": response}

@app.delete("/file/{file_id}", response_model=DeleteResponse)
async def delete_file_endpoint(file_id: str):
    result = delete_file(file_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}