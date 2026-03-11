from fastapi import APIRouter, HTTPException
from models.schemas import SpeechRequest, SpeechResponse
from services.azure_speech import process_speech

router = APIRouter()


@router.post("/speech", response_model=SpeechResponse)
async def speech_to_text(request: SpeechRequest):
    """Process audio recording through Azure Speech SDK and extract fields."""
    try:
        result = await process_speech(request.name, request.contentBytes)
        return SpeechResponse(
            transcript=result.get("transcript", ""),
            clientname=result.get("clientname", ""),
            subject=result.get("subject", ""),
            method=result.get("method", ""),
            purpose=result.get("purpose", ""),
            status=result.get("status", ""),
            primarycontact=result.get("primarycontact", ""),
            actualdate=result.get("actualdate", ""),
            notes=result.get("notes", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech processing failed: {str(e)}")
