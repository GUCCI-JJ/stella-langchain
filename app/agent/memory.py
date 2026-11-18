from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from app.db.crud import get_messages, save_message


class PostgresChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id

    @property
    def messages(self):
        rows = get_messages(self.session_id)
        result = []
        for session_id, role, content in rows:
            if role == 'user':
                result.append(HumanMessage(content=content))
            else:
                result.append(AIMessage(content=content))
        return result

    def add_message(self, message):
        role = 'user' if isinstance(message, HumanMessage) else 'assistant'
        save_message(self.session_id, role, message.content)

    def clear(self):
        pass
