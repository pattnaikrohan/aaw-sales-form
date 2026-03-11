from fastapi import APIRouter, HTTPException
from models.schemas import ExtractFieldsRequest, ExtractFieldsResponse
from services.claude_api import extract_fields_from_conversation

router = APIRouter()


@router.post("/extract-fields", response_model=ExtractFieldsResponse)
async def extract_fields(request: ExtractFieldsRequest):
    """Extract form fields from a Copilot Studio conversation snippet."""
    try:
        fields = await extract_fields_from_conversation(
            user_message=request.userMessage,
            bot_reply=request.botReply,
            current_form_state=request.currentFormState,
        )
        return ExtractFieldsResponse(extractedFields=fields)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Field extraction failed: {str(e)}",
        )
