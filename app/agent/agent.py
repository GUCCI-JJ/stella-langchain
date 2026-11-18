from langchain.chat_models import init_chat_model
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

from app.agent.memory import PostgresChatHistory
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.rag import get_retriever
from app.agent.tools import search_product_docs
from app.config import OPENAI_API_KEY

llm = init_chat_model(model='deepseek-chat', api_key=OPENAI_API_KEY)

tools = [search_product_docs]

prompt = ChatPromptTemplate.from_messages([
    ('system', SYSTEM_PROMPT),
    MessagesPlaceholder('chat_history', optional=True),  # 长期记忆
    ('human', '{input}'),
    MessagesPlaceholder('agent_scratchpad')
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history=lambda session_id: PostgresChatHistory(session_id=session_id),
    input_messages_key='input',
    history_messages_key='history'
)


# retreiver = get_retriever()
#
# RAG_PROMPT = ChatPromptTemplate.from_messages([
#     ('system', SYSTEM_PROMPT + '\n\n参考资料: \n{context}'),
#     ('human', '{input}')
# ])
#
# base_chain = RAG_PROMPT | llm
#
# chain_with_history = RunnableWithMessageHistory(
#     base_chain,
#     get_session_history=lambda session_id: PostgresChatHistory(session_id=session_id),
#     input_messages_key='input'
# )


def ask(message: str, session_id: str):
    # docs = retreiver.invoke(message)
    # context = '\n\n'.join(d.page_content for d in docs) if docs else '无'
    result = agent_with_history.invoke(
        {'input': message},
        config={'configurable': {'session_id': session_id}},
    )
    if (isinstance(result, dict)):
        return result.get('output')
    if (hasattr(result, 'content')):
        return result.content
    return str(result)
