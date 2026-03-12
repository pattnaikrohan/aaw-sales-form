import httpx
import xml.etree.ElementTree as ET
import io
from config import CARGOWISE_URL


async def submit_form(form_data: dict) -> dict:
    """Submit form data as XML to CargoWise eAdaptor endpoint."""
    
    # Create XML structure
    root = ET.Element("SalesCallRecord")
    
    mapping = {
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
    
    for key, value in mapping.items():
        child = ET.SubElement(root, key)
        child.text = str(value) if value is not None else ""

    # Convert to string
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    
    print(f"[FormSubmit] Sending XML to {CARGOWISE_URL}:\n{xml_str}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                CARGOWISE_URL, 
                content=xml_str,
                headers={"Content-Type": "application/xml"}
            )
            response.raise_for_status()
            
            # The endpoint might return XML or JSON; we'll check
            resp_text = response.text
            print(f"[FormSubmit] Response: {resp_text}")
            
            return {
                "status": "success",
                "message": "Form submitted successfully to CargoWise",
                "raw_response": resp_text
            }
        except Exception as e:
            print(f"[FormSubmit] Error during submission: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to submit to CargoWise: {str(e)}"
            }
