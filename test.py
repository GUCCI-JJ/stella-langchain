import os
from typing import Dict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """获取传入城市的天气"""
    writer = get_stream_writer()
    writer(f'正在查询{city}的天气')
    writer(f'查询{city}的天气成功')
    return f'{city} 今日的天气多云转小雨'


model = init_chat_model(model='deepseek-chat', api_key=os.getenv('DEEPSEEK_API_KEY'))

agent = create_agent(
    model,
    tools=[get_weather],
    # checkpointer=InMemorySaver(),
    system_prompt='你是一个乐于助人的助手'
)

stream = agent.stream_events(
    {'messages': [{'role': 'user', 'content': '今天上海天气如何'}]},
    version='v3'
)

for message in stream.messages:
    for token in message.reasoning:
        print(f'[思考中] {token}', end='')
    for token in message.text:
        print(token, end='', flush=True)
