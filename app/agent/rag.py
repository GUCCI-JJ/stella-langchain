import os
import pickle

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine

from app.config import OPENAI_API_KEY, QWEN_API_KEY, QWEN_BASE_URL, DB_CONFIG, EMBEDDING_MODEL

PERSIS_DIR = 'chroma_db'

'''
To use it run `pip install -U `langchain-huggingface` and import as `from `langchain_huggingface import HuggingFaceEmbeddings``.
  embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-large-zh-v1.5')
'''

_retriever = None

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    dimensions=1024,
    check_embedding_ctx_length=False,  # 关键：禁止客户端 token 化
)

CONNECTION_STRING = f"postgresql+psycopg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['dbname']}?sslmode=require"

engine = create_engine(
    CONNECTION_STRING,
    pool_pre_ping=True,
    pool_recycle=180,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

vs = PGVector(
    embeddings=embeddings,
    connection=engine,
    collection_name='product_docs',
    use_jsonb=True,
)


def reset_vector_engine():
    vs.session_maker.remove()
    engine.dispose()


def load_file(path: str):
    ext = os.path.splitext(path)[1].lower()
    print(f'文件扩展名：{repr(ext)}')
    if ext == '.pdf':
        return PyPDFLoader(path).load()
    elif ext in ('.docx', '.doc'):
        return Docx2txtLoader(path).load()
    raise Exception(f'File type not supported:{ext}')


def ingest(path: str, doc_id: int):
    # 加载文件
    docs = load_file(path)
    # 创建文件分割器（每块 500 字符，块间内容可重叠 50）
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # 分割 docs
    chunks = splitter.split_documents(docs)
    # embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-large-zh-v1.5')
    # Chroma.from_documents(chunks, embeddings, persist_directory=PERSIS_DIR)

    # 给每个chunk加上doc_id
    for chunk in chunks:
        chunk.metadata['doc_id'] = doc_id
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        connection=CONNECTION_STRING,
        collection_name='product_docs',
        use_jsonb=True,
    )
    return len(chunks)


def get_retriever():
    global _retriever
    if _retriever is None:
        # embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-large-zh-v1.5')
        # vs = Chroma(persist_directory=PERSIS_DIR, embedding_function=embeddings)
        _retriever = vs.as_retriever(search_kwargs={'k': 4})
    return _retriever
