from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.claude_api import send_chat_message

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Send a message to Claude AI and get reply with extracted form fields."""
    try:
        result = await send_chat_message(
            message=request.message,
            conversation_history=request.conversationHistory,
            current_form_state=request.currentFormState,
        )
        return ChatResponse(
            reply=result.get("reply", ""),
            extractedFields=result.get("extractedFields", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
