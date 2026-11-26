import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File

from app.agent.rag import ingest
from app.db.crud import save_document, get_doc_by_id, delete_product_doc, delete_product_doc_embeddings, \
    put_document_chunks, get_all_documents
from app.schemas.common import ApiResponse

router = APIRouter()
UPLOAD_DIR = 'data/uploads'


@router.post('/upload')
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    results = []

    for file in files:
        # 1 清洗文件名，防止目录穿越
        safe_name = os.path.basename(file.filename or "")
        if not safe_name:
            results.append({'filename': file.filename, 'status': '无效的文件名'})
            continue

        # 2 避免覆盖
        name, ext = os.path.splitext(safe_name)
        final_name = safe_name
        path = os.path.join(UPLOAD_DIR, final_name)
        if os.path.exists(path):
            final_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            path = os.path.join(UPLOAD_DIR, final_name)

        # 3 保存
        with open(path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        # 4 存入chroma
        doc_id = save_document(
            filename=final_name,
            original_filename=file.filename or "",
            file_type=ext,
            size=file.size or 0,
        )
        n = ingest(path, doc_id)
        put_document_chunks(doc_id, n)  # 存入chunks数

        results.append({
            'filename': final_name,
            'original_filename': file.filename,
            'size': file.size,
            'chunks': n,
            'status': 'processed',
            'doc_id': doc_id
        })

    return results


@router.delete('/delete/{doc_id}')
async def delete_document(doc_id: int):
    # 1 查询对应文件是否存在
    targetDoc = get_doc_by_id(doc_id)
    if not targetDoc:
        return ApiResponse(message='目标文件不存在')

    # 2 删除对应文件记录
    res = delete_product_doc(doc_id)

    # 3 删除对应的文件向量
    vecRes = delete_product_doc_embeddings(doc_id)

    return ApiResponse(data={
        'product_doc_delete_status': res,
        'product_doc_embeddings_delete_status': vecRes
    })


@router.get('/documents')
async def get_documents():
    rows = get_all_documents()
    return ApiResponse(data=rows)
