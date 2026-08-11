from fastapi import APIRouter, HTTPException
import httpx
from config import CONTACT_FLOW_URL
from models.schemas import ContactSearchRequest, ContactSearchResponse

router = APIRouter()

@router.post("/contact-search", response_model=ContactSearchResponse)
async def contact_search(request: ContactSearchRequest):
    """Search for matching contacts via Power Automate Flow."""
    try:
        if not CONTACT_FLOW_URL:
            return ContactSearchResponse(contacts=[])
            
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                CONTACT_FLOW_URL,
                json={"contactName": request.contactName, "clientName": request.clientName},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            
            contacts = []
            if isinstance(data, list):
                contacts = data
            elif isinstance(data, dict):
                for key in ["contacts", "value", "results"]:
                    if key in data and isinstance(data[key], list):
                        contacts = data[key]
                        break
                if not contacts:
                    for val in data.values():
                        if isinstance(val, list):
                            contacts = val
                            break
            
            # Extract just strings if it's a list of dicts
            clean_contacts = []
            for item in contacts:
                if isinstance(item, str):
                    clean_contacts.append(item.strip())
                elif isinstance(item, dict):
                    # Try common keys
                    for k in ["name", "contactName", "contact", "value"]:
                        if k in item:
                            clean_contacts.append(str(item[k]).strip())
                            break
                    else:
                        if len(item) > 0:
                            clean_contacts.append(str(list(item.values())[0]).strip())
            
            # Deduplicate and sort
            clean_contacts = sorted(list(set(clean_contacts)))
            return ContactSearchResponse(contacts=clean_contacts)
    except Exception as e:
        print(f"Contact search failed: {e}")
        # Return empty list instead of raising error so frontend doesn't break
        return ContactSearchResponse(contacts=[])
