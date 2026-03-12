import httpx
import base64
from datetime import datetime, timezone, timedelta
from config import AZURE_FUNCTION_URL, FLOW1_URL
from services.normalization import normalize_field_value


async def process_speech(name: str, content_bytes: str) -> dict:
    """Process audio in two steps:
        1. Send raw binary audio to Azure Function → get transcript
        2. Send transcript to Power Automate flow (AI Builder) → get structured fields
    """
    # Step 1: Decode base64 and send raw binary to Azure Function
    audio_binary = base64.b64decode(content_bytes)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            AZURE_FUNCTION_URL,
            content=audio_binary,
            headers={"Content-Type": "application/octet-stream"},
        )
        if response.status_code != 200:
            print(f"[Speech] Azure Function error {response.status_code}: {response.text}")
            response.raise_for_status()
        transcription_result = response.json()

    transcript = transcription_result.get("transcript", "")

    if not transcript:
        return {"transcript": "", "clientname": "", "subject": "", "method": "",
                "purpose": "", "status": "", "primarycontact": "", "actualdate": "", "notes": ""}

    # Step 2: Send transcript to Power Automate flow for AI Builder extraction
    ist = timezone(timedelta(hours=5, minutes=30))
    current_dt = datetime.now(ist).strftime("%d-%b-%y %H:%M").upper()

    async with httpx.AsyncClient(timeout=120.0) as client:
        flow_response = await client.post(
            FLOW1_URL,
            json={
                "transcript": transcript,
                "currentDateTime": current_dt,
            },
            headers={"Content-Type": "application/json"},
        )
        if flow_response.status_code != 200:
            print(f"[Speech] Flow error {flow_response.status_code}: {flow_response.text}")
            flow_response.raise_for_status()
        extracted = flow_response.json()

    # Step 3: Return merged result with normalized field values
    return {
        "transcript": transcript,
        "clientname": extracted.get("clientName", ""),
        "subject": extracted.get("subject", ""),
        "method": normalize_field_value("method", extracted.get("method", "")),
        "purpose": normalize_field_value("purpose", extracted.get("purpose", "")),
        "status": normalize_field_value("status", extracted.get("status", "")),
        "primarycontact": extracted.get("primaryContact", ""),
        "actualdate": extracted.get("actualDate", ""),
        "notes": extracted.get("notes", ""),
    }
