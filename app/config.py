import os

from dotenv import load_dotenv

# 1 获取当前环境
env=os.getenv('APP_ENV','development')

# 2 拼接出环境变量文件名
env_file=f'.env.{env}'

print(env_file)

# 3 显式加载对应文件
load_dotenv(env_file)

print(os.getenv('DB_HOST'))
print(os.getenv('DB_PORT'))
print(os.getenv('DB_USER'))

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME')
}

OPENAI_API_KEY = os.getenv('DEEPSEEK_API_KEY')

EMBEDDING_MODEL = os.getenv('DASHSCOPE_MODEL')
QWEN_API_KEY = os.getenv('DASHSCOPE_API_KEI')
QWEN_BASE_URL = os.getenv('DASHSCOPE_URL')

CHROMA_HOST = os.getenv('CHROMA_HOST')
CHROMA_PORT = int(os.getenv('CHROMA_PORT'))
