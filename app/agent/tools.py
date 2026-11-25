import logging
import os
import shutil
import uuid
from typing import List

from fastapi import UploadFile, File
from langchain_core.tools import tool
from sqlalchemy.exc import OperationalError

from app.agent.rag import get_retriever, ingest, reset_vector_engine
from app.db.crud import save_document

logger = logging.getLogger(__name__)

UPLOAD_DIR = 'data/uploads'


@tool
def search_product_docs(query: str) -> str:
    """搜索公司产品文档，回答产品相关时使用"""
    rt = get_retriever()

    for attempt in range(2):
        try:
            docs = rt.invoke(query)
            return "\n\n".join(d.page_content for d in docs)
        except OperationalError as e:
            message = str(e)
            is_stale_connection = (
                "SSL connection has been closed unexpectedly" in message
                or "server closed the connection unexpectedly" in message
            )
            if attempt == 0 and is_stale_connection:
                logger.warning("向量库连接已失效，正在重建连接池并重试一次")
                reset_vector_engine()
                continue
            raise
