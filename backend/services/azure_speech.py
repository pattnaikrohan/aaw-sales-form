import httpx
import base64
from datetime import datetime, timezone, timedelta
from config import AZURE_FUNCTION_URL, FLOW1_URL
from services.normalization import normalize_field_value, normalize_date
from services.company_search import fuzzy_match_company


async def process_transcript_text(transcript: str, use_raw_notes: bool = False) -> dict:
    """Send transcript to Power Automate flow (AI Builder) -> get structured fields"""
    if not transcript:
        return {
            "transcript": "", "clientName": "", "subject": "", "method": "",
            "purpose": "", "status": "", "primaryContact": "", "actualDate": "", "notes": ""
        }

    ist = timezone(timedelta(hours=5, minutes=30))
    current_dt = datetime.now(ist).strftime("%d-%b-%y %H:%M").upper()

    extracted = {}
    try:
        print(f"[Speech] Sending transcript to Flow 1 (AI Builder)...")
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
                print(f"[Speech] Flow 1 error {flow_response.status_code}: {flow_response.text}")
            else:
                extracted = flow_response.json()
                print(f"[Speech] Flow 1 extraction successful")
    except Exception as e:
        print(f"[Speech] Failed to extract fields via Flow 1: {e}")

    # Try to find an exact company name match
    raw_client_name = extracted.get("clientName", "")
    best_client_name = fuzzy_match_company(raw_client_name) if raw_client_name else ""

    # Decide what goes into the notes field
    final_notes = transcript if use_raw_notes else extracted.get("notes", "")

    # Return merged result with normalized field values (CAMEL CASE for frontend)
    return {
        "transcript": transcript,
        "clientName": best_client_name,
        "subject": extracted.get("subject", ""),
        "method": normalize_field_value("method", extracted.get("method", "")),
        "purpose": normalize_field_value("purpose", extracted.get("purpose", "")),
        "status": normalize_field_value("status", extracted.get("status", "")),
        "primaryContact": extracted.get("primaryContact", ""),
        "actualDate": normalize_date(extracted.get("actualDate", "")),
        "notes": final_notes,
    }


async def process_speech(name: str, content_bytes: str) -> dict:
    """Process audio in two steps:
        1. Send raw binary audio to Azure Function -> get transcript (v2 with higher timeout)
        2. Send transcript to Power Automate flow -> get structured fields
    """
    # Step 1: Decode base64 and send raw binary to Azure Function
    audio_binary = base64.b64decode(content_bytes)

    print(f"[Speech] Sending {len(audio_binary)} bytes to Azure Function (Speech-to-Text)...")

    try:
        # Increase timeout to 300s (5 minutes) to handle long recordings as requested.
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                AZURE_FUNCTION_URL,
                content=audio_binary,
                headers={"Content-Type": "application/octet-stream"}
            )
            
            if response.status_code != 200:
                error_detail = response.text[:500] # Limit size of error text
                print(f"[Speech] Azure Function 500/Error: {error_detail}")
                raise Exception(f"Azure Speech Service Error ({response.status_code}). Long recordings might hit Azure limits.")

            result = response.json()
            transcript = result.get("transcript", "")
            if not transcript:
                print("[Speech] Azure returned empty transcript")
            else:
                print(f"[Speech] Azure transcript (first 50 chars): {transcript[:50]}...")

    except httpx.TimeoutException:
        print("[Speech] Timeout reaching Azure Function after 300s")
        raise Exception("Transcription timeout: The recording is too long (over 5 mins) for the current processing limit.")
    except Exception as e:
        print(f"[Speech] Azure Function processing failed: {e}")
        raise

    # Step 2: Process the transcript to extract fields
    return await process_transcript_text(transcript, use_raw_notes=True)
