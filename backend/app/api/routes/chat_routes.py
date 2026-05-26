import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse, HistoryDetail, HistoryItem
from app.services.history_service import HistoryService
from app.services.rag_service import RAGService
from app.services.vector_service import VectorService

router = APIRouter(tags=["chat"])


@router.post("/ask")
async def ask(payload: ChatRequest):
    try:
        rag = RAGService()
        HistoryService().append_messages(
            payload.collection_id,
            [{"role": "user", "content": payload.question}],
        )
        if payload.stream:
            async def event_stream():
                tokens = []
                async for token in rag.stream_answer(payload.collection_id, payload.question):
                    tokens.append(token)
                    yield f"data: {json.dumps({'token': token})}\n\n"
                answer = "".join(tokens)
                HistoryService().append_messages(
                    payload.collection_id,
                    [{"role": "assistant", "content": answer}],
                )
                yield f"data: {json.dumps({'done': True})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")
        answer, sources = await rag.answer(payload.collection_id, payload.question)
        HistoryService().append_messages(
            payload.collection_id,
            [{"role": "assistant", "content": answer}],
        )
        return ChatResponse(answer=answer, sources=sources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history", response_model=list[HistoryItem])
async def history():
    return HistoryService().list()


@router.get("/stats")
async def stats():
    return HistoryService().stats()


@router.get("/history/{chat_id}", response_model=HistoryDetail)
async def history_detail(chat_id: str):
    item = HistoryService().get(chat_id)
    if not item:
        raise HTTPException(status_code=404, detail="Chat history not found.")
    return item


@router.delete("/history")
async def clear_history():
    HistoryService().clear()
    return {"deleted": "all"}


@router.delete("/history/{collection_id}")
async def delete_history(collection_id: str):
    HistoryService().delete(collection_id)
    VectorService().delete_collection(collection_id)
    return {"deleted": collection_id}
