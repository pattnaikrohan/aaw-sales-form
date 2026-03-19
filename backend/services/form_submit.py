import httpx
from datetime import datetime
from config import CARGOWISE_URL
from services.company_search import get_company_code


async def submit_form(form_data: dict) -> dict:
    """Submit form data as JSON to Power Automate flow."""
    
    # 1. Look up company code
    client_name = form_data.get("clientName", "").strip()
    company_code = get_company_code(client_name)
    
    # 2. Prepare JSON payload
    # We include all existing fields plus the looked-up company_code
    payload = {
        "clientName": client_name,
        "company_code": company_code,
        "subject": form_data.get("subject", ""),
        "purpose": form_data.get("purpose", ""),
        "method": form_data.get("method", ""),
        "status": form_data.get("status", ""),
        "primaryContact": form_data.get("primaryContact", ""),
        "actualDate": form_data.get("actualDate", ""),
        "scheduledDate": form_data.get("scheduledDate", ""),
        "notes": form_data.get("notes", ""),
        "submittedBy": form_data.get("submittedBy", "AAW Demo User"),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    print(f"[FormSubmit] Sending JSON to {CARGOWISE_URL}:\n{payload}")

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                CARGOWISE_URL, 
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            # Power Automate flows often return 200/202 with etc.
            resp_text = response.text
            print(f"[FormSubmit] Response ({response.status_code}): {resp_text}")
            
            return {
                "status": "success",
                "message": "Form submitted successfully to CargoWise flow",
                "raw_response": resp_text
            }
        except Exception as e:
            print(f"[FormSubmit] Error during submission: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to submit to CargoWise flow: {str(e)}"
            }
