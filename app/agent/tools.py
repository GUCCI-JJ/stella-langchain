import os
import shutil
from typing import List
import uuid

from fastapi import UploadFile, File
from langchain_core.tools import tool

from app.agent.rag import get_retriever, ingest
from app.db.crud import save_document

UPLOAD_DIR = 'data/uploads'


@tool
def search_product_docs(query: str) -> str:
    """搜索公司产品文档，回答产品相关时使用"""
    rt = get_retriever()
    docs = rt.invoke(query)
    return "\n\n".join(d.page_content for d in docs)
