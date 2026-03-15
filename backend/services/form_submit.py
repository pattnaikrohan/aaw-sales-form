import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from config import CARGOWISE_URL, CARGOWISE_USERNAME, CARGOWISE_PASSWORD, CARGOWISE_API_KEY


async def submit_form(form_data: dict) -> dict:
    """Submit form data as XML to CargoWise eAdaptor endpoint following Native schema."""
    
    # Create XML structure following Table 21 specifications
    root = ET.Element("SalesCallRecord")
    
    # 1. Hardcoded & Global values
    ET.SubElement(root, "OwnerCode").text = "AAWGLO_AU1"
    ET.SubElement(root, "Timestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    ET.SubElement(root, "Duration").text = "1900-01-01T00:30:00"
    
    # 2. Date handling (Ensure T00:00:00 format)
    actual_date = form_data.get("actualDate", "")
    if actual_date:
        # If it's just a date 'YYYY-MM-DD', append time
        if len(actual_date) == 10:
            actual_date += "T00:00:00"
    ET.SubElement(root, "CallDate").text = actual_date

    # 3. Simple fields with XML escaping (handled by ElementTree)
    ET.SubElement(root, "CallSummary").text = form_data.get("subject", "")
    ET.SubElement(root, "SalesCallNotes").text = form_data.get("notes", "")

    # 4. Value Transformations
    
    # Category (Purpose)
    purpose = (form_data.get("purpose") or "").lower()
    category_map = {"pbs": "PBS", "ebs": "EBS", "trd": "TRD", "efo": "EFO"}
    ET.SubElement(root, "Category").text = category_map.get(purpose, "GEN")
    
    # TypeOfCall (Method)
    method = (form_data.get("method") or "").upper()
    # If method is already normalized code, keep it. If descriptive, map.
    # pbs->PBS transformation suggests the input might be both codes or labels.
    # Table 21 says: phone->PHN, teams/meeting->MTG, email->EML, else PHN
    if "PHONE" in method or "PHN" == method: ET.SubElement(root, "TypeOfCall").text = "PHN"
    elif any(x in method for x in ["MEET", "TEAM", "MTG"]): ET.SubElement(root, "TypeOfCall").text = "MTG"
    elif "EML" == method or "EMAIL" in method: ET.SubElement(root, "TypeOfCall").text = "EML"
    else: ET.SubElement(root, "TypeOfCall").text = "PHN"

    # Status
    status = (form_data.get("status") or "").upper()
    # Table 21: green/completed->COM, amber->PND, red/cancel->CAN, else PND
    if status in ["COM", "COMPLETED"]: ET.SubElement(root, "Status").text = "COM"
    elif status in ["PND", "AMBER"]: ET.SubElement(root, "Status").text = "PND"
    elif status in ["CAN", "CANCEL", "RED"]: ET.SubElement(root, "Status").text = "CAN"
    else: ET.SubElement(root, "Status").text = "PND"

    # 5. Nested Structures
    
    # OrgHeader/Code (ClientName)
    org_header = ET.SubElement(root, "OrgHeader")
    ET.SubElement(org_header, "Code").text = (form_data.get("clientName") or "").strip()
    
    # OrgContact/ContactName (PrimaryContact)
    org_contact = ET.SubElement(root, "OrgContact")
    ET.SubElement(org_contact, "ContactName").text = (form_data.get("primaryContact") or "").strip()
    
    # SalesRep/Code (SubmittedBy)
    sales_rep = ET.SubElement(root, "SalesRep")
    # Table 21 says: Name -> 3-char staff code (e.g. MEL). 
    # Since we might not have a full mapping, we'll try to use first 3 chars or default.
    submitted_by = (form_data.get("submittedBy") or "USR").strip()
    staff_code = submitted_by[:3].upper() if len(submitted_by) >= 3 else submitted_by.upper()
    ET.SubElement(sales_rep, "Code").text = staff_code

    # Convert to string
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    
    print(f"[FormSubmit] Sending XML to {CARGOWISE_URL}:\n{xml_str}")

    # Prepare headers and auth
    headers = {"Content-Type": "application/xml"}
    auth = None

    if CARGOWISE_USERNAME and CARGOWISE_PASSWORD:
        auth = (CARGOWISE_USERNAME, CARGOWISE_PASSWORD)
        print("[FormSubmit] Using Basic Auth")
    elif CARGOWISE_API_KEY:
        headers["Authorization"] = f"Bearer {CARGOWISE_API_KEY}"
        headers["eAdaptorKey"] = CARGOWISE_API_KEY
        print("[FormSubmit] Using API Key")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                CARGOWISE_URL, 
                content=xml_str,
                headers=headers,
                auth=auth
            )
            response.raise_for_status()
            
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
