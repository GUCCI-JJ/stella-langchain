from typing import Generic, TypeVar, List, Optional

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class UploadedDoc(BaseModel):
    doc_id: int
    filename: str
    original_filename: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    session_id: str = Field(alias='sessionId')
    content: str = ''
    uploaded_doc: Optional[List[UploadedDoc]] = None


class ChatResponse(BaseModel):
    reply: str


class ChatMessage(BaseModel):
    session_id: str
    role: str
    content: str
