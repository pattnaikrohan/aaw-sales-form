import httpx
from config import FLOW2_URL


async def submit_form(form_data: dict) -> dict:
    """Submit form data to Power Automate Flow 2 (SalesFormAutomation_NormalFlow)."""
    payload = {
        "ClientName": form_data.get("clientName", ""),
        "Subject": form_data.get("subject", ""),
        "Method": form_data.get("method", ""),
        "Purpose": form_data.get("purpose", ""),
        "Status": form_data.get("status", ""),
        "PrimaryContact": form_data.get("primaryContact", ""),
        "ActualDate": form_data.get("actualDate", ""),
        "ScheduledDate": form_data.get("scheduledDate", ""),
        "Notes": form_data.get("notes", ""),
        "SubmittedBy": form_data.get("submittedBy", ""),
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(FLOW2_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        return {
            "status": data.get("submitStatus", "success"),
            "message": data.get("message", "Form submitted successfully"),
        }
