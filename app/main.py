from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, documents

app = FastAPI(title='产品介绍助手')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    chat.router, prefix='/api'
)
app.include_router(documents.router, prefix='/api')


@app.get('/')
async def root():
    return {'status': 'ok'}
