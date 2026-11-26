from psycopg2.extras import RealDictCursor

from app.agent.rag import chroma_client
from app.db.connection import get_conn


# 保存一条信息
def save_message(session_id: str, role: str, content: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s) RETURNING id',
        (session_id, role, content)
    )
    msg_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return msg_id


# 获取这个session的信息
def get_messages(session_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'select session_id, role, content from chat_messages where session_id = %s order by created_at asc',
        (session_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# 保存文件
def save_document(filename: str, original_filename: str, file_type: str, size: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'insert into product_documents (filename, original_filename, file_type,size) values (%s, %s, %s, %s) returning id',
        (filename, original_filename, file_type, size)
    )
    doc_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return doc_id


# 补充文件的chunks数
def put_document_chunks(doc_id: int, chunks: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'update product_documents set chunks = %s where id = %s',
        (chunks, doc_id,)
    )
    count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return count > 0


# 查询所有文件
def get_all_documents():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                'select id as doc_id, filename, original_filename, size, chunks,status from product_documents'
            )
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


# 查询是否该文件名已存在
def is_filename_exists(filename: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'select filename from product_documents where filename = %s',
        (filename,)
    )
    filename = cur.fetchone()[0]
    cur.close()
    conn.close()
    return filename


# 按文件id查询
def get_doc_by_id(doc_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'select * from product_documents where id = %s',
        (doc_id,)
    )
    doc = cur.fetchone()
    cur.close()
    conn.close()
    return doc


# 删除product_documents中文件记录
def delete_product_doc(doc_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'delete from product_documents where id = %s',
        (doc_id,)
    )
    deleted = cur.rowcount  # 受影响行数
    conn.commit()
    cur.close()
    conn.close()
    return {'success': deleted > 0, 'doc_id': doc_id}


# 删除langchain_pg_embedding中文件向量
def delete_product_doc_embeddings(doc_id: int):
    collection = chroma_client.get_or_create_collection("product_docs")
    collection.delete(where={"doc_id": doc_id})
    return True
