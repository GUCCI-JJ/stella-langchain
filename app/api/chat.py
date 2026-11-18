import json

from fastapi import APIRouter

from app.agent.agent import ask, agent_executor
from app.db.crud import save_message, get_messages
from app.schemas.chat import ChatResponse, ChatRequest, ChatMessage
from app.schemas.common import ApiResponse
from fastapi.responses import StreamingResponse

router = APIRouter(prefix='/chat', tags=['chat'])


@router.post('', response_model=ApiResponse[ChatResponse])
async def chat(req: ChatRequest):
    """在 PostgresChatHistory 会自动调用 save_message 保存用户和ai的消息，这里不再手动保存"""
    # save_message(req.session_id, 'user', req.message)
    reply = ask(req.content, req.session_id)
    # save_message(req.session_id, 'assistant', reply)
    return ApiResponse(data=ChatResponse(reply=reply))


@router.get('/{session_id}', response_model=ApiResponse[list[ChatMessage]])
async def chat_messages(session_id: str):
    rows = get_messages(session_id)
    data = [
        ChatMessage(session_id=r[0], role=r[1], content=r[2]) for r in rows
    ]
    return ApiResponse(data=data)


@router.post('/stream')
async def chat_stream(req: ChatRequest):
    async def event_generator():
        full_reply = ""
        try:
            # 用户消息在流开始时保存，和生成在同一生命周期内
            save_message(req.session_id, "user", req.content)

            # 如果是上传了文件，让agent知道上下文
            agent_input = req.content
            if req.uploaded_doc:
                ori_filenames = ''
                doc_ids = ''
                for doc in req.uploaded_doc:
                    ori_filenames += doc.original_filename + '; '
                    doc_ids += str(doc.doc_id) + '; '
                agent_input = (
                    f'[系统提示] 用户刚刚上传了文件{ori_filenames}',
                    f'doc_id={doc_ids}已入库完成',
                    f'用户说: {req.content}'
                )

            async for event in agent_executor.astream_events(
                    {"input": agent_input},
                    config={"configurable": {"session_id": req.session_id}},
                    version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    text = getattr(chunk, "content", None)
                    if isinstance(text, str) and text:
                        full_reply += text
                        payload = json.dumps(
                            {"type": "token", "content": text},
                            ensure_ascii=False,
                        )
                        yield f"data: {payload}\n\n"

            # 流结束，保存完整助手回复
            save_message(req.session_id, "assistant", full_reply)
            payload = json.dumps({"type": "done"}, ensure_ascii=False)
            yield f"data: {payload}\n\n"

        except Exception as e:
            payload = json.dumps(
                {"type": "error", "content": str(e)}, ensure_ascii=False
            )
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
