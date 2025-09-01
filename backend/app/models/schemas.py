from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    content: str
    doc_id: str

class SearchResponse(BaseModel):
    results: List[dict]

class AskResponse(BaseModel):
    answer: str
    context: List[str]
