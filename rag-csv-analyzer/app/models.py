from pydantic import BaseModel

class UploadResponse(BaseModel):
    file_id: str
    message: str

class FileInfo(BaseModel):
    file_id: str
    file_name: str

class FilesResponse(BaseModel):
    files: list[FileInfo]

class QueryRequest(BaseModel):
    file_id: str
    query: str

class QueryResponse(BaseModel):
    response: str

class DeleteResponse(BaseModel):
    message: str