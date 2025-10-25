from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.openai_utils import get_chat_response
from app.vectorstore import embed_and_store_text, query_vectorstore
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Request/Response Schemas ---
class ChatRequest(BaseModel):
    message: str

class EmbedRequest(BaseModel):
    content: str
    metadata: dict = {}

# --- /chat endpoint ---
@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # 1. Retrieve relevant context from Supabase
        context = query_vectorstore(request.message)

        # 2. Send to OpenAI for response
        response = get_chat_response(request.message, context)

        return {"response": response}
    except Exception as e:
        logger.error(f"Chat endpoint error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --- /embed endpoint ---
@router.post("/embed")
async def embed(request: EmbedRequest):
    try:
        success = embed_and_store_text(request.content, metadata=request.metadata)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ OPTIONS handler to fix CORS preflight error
@router.options("/chat")
async def options_chat():
    return Response(status_code=204)
