import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME')
}

OPENAI_API_KEY=os.getenv('DEEPSEEK_API_KEY')

EMBEDDING_MODEL=os.getenv('DASHSCOPE_MODEL')
QWEN_API_KEY=os.getenv('DASHSCOPE_API_KEI')
QWEN_BASE_URL=os.getenv('DASHSCOPE_URL')
