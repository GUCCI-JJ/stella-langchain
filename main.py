import os
import urllib

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()

agent_system_prompt = """你是一名乐于助人的助手。面向的用户是中国人，回答需使用中文。回答需简洁精干"""

invoke_content = """总结 AI 的趋势"""


class Answer(BaseModel):
    summary: str
    confidence: float


@tool
def add(a, b):
    """计算两个数字之和"""
    return a + b


@tool
def fetch_text_from_url(url: str) -> str:
    """从url中获取文档"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"}, )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read()
    except urllib.error.URLError as e:
        return f"获取失败：{e}"
    text = raw.decode("utf-8", errors="replace")
    return text


model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

agent = create_agent(
    model,
    response_format=Answer,
    tools=[add, fetch_text_from_url],
    system_prompt=agent_system_prompt
)

print("正在运行。。。")

result = agent.invoke({
    "messages": [
        {"role": "user", "content": invoke_content}
    ]
})

print(result["messages"][-1].content)
