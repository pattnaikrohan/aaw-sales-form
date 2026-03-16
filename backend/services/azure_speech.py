import httpx
import base64
import httpx
import base64
from datetime import datetime, timezone, timedelta
from config import AZURE_FUNCTION_URL, FLOW1_URL
from services.normalization import normalize_field_value
from services.company_search import fuzzy_match_company


async def process_transcript_text(transcript: str, use_raw_notes: bool = False) -> dict:
    """Send transcript to Power Automate flow (AI Builder) -> get structured fields"""
    if not transcript:
        return {"transcript": "", "clientname": "", "subject": "", "method": "",
                "purpose": "", "status": "", "primarycontact": "", "actualdate": "", "notes": ""}

    ist = timezone(timedelta(hours=5, minutes=30))
    current_dt = datetime.now(ist).strftime("%d-%b-%y %H:%M").upper()

    extracted = {}
    try:
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
                # Don't raise, just fall back to empty fields
            else:
                extracted = flow_response.json()
    except Exception as e:
        print(f"[Speech] Failed to extract fields via AI Builder: {e}")
        # Proceed with empty extracted fields, but we still have the transcript

    # Try to find an exact company name match
    raw_client_name = extracted.get("clientName", "")
    best_client_name = fuzzy_match_company(raw_client_name) if raw_client_name else ""

    # Decide what goes into the notes field
    final_notes = transcript if use_raw_notes else extracted.get("notes", "")

    # Return merged result with normalized field values
    return {
        "transcript": transcript,
        "clientname": best_client_name,
        "subject": extracted.get("subject", ""),
        "method": normalize_field_value("method", extracted.get("method", "")),
        "purpose": normalize_field_value("purpose", extracted.get("purpose", "")),
        "status": normalize_field_value("status", extracted.get("status", "")),
        "primarycontact": extracted.get("primaryContact", ""),
        "actualdate": extracted.get("actualDate", ""),
        "notes": final_notes,
    }


async def process_speech(name: str, content_bytes: str) -> dict:
    """Process audio in two steps:
        1. Send raw binary audio to Azure Function → get transcript
        2. Send transcript to Power Automate flow → get structured fields
    """
    # Step 1: Decode base64 and send raw binary to Azure Function
    audio_binary = base64.b64decode(content_bytes)

    print(f"[Speech] Sending {len(audio_binary)} bytes to Azure Function...")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                AZURE_FUNCTION_URL,
                content=audio_binary,
                headers={"Content-Type": "application/octet-stream"}
            )
            if response.status_code != 200:
                raise Exception(f"Azure Function returned {response.status_code}: {response.text}")

            result = response.json()
            transcript = result.get("transcript", "")
            print(f"[Speech] Azure returned transcript: {transcript}")

    except Exception as e:
        print(f"[Speech] Azure Function failed: {e}")
        raise

    # Step 2: Process the transcript to extract fields
    # For voice dictation, we want the raw transcript in the notes field
    fields = await process_transcript_text(transcript, use_raw_notes=True)
    return fields
