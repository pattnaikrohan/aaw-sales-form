from fastapi import APIRouter, HTTPException
from models.schemas import (
    ValidateClientContactRequest,
    ValidateClientContactResponse,
    ContactSearchRequest,
    ContactSearchResponse,
    OrgSearchRequest,
    OrgSearchResponse,
)
from services.snowflake_connector import (
    validate_client_contact,
    search_contacts_for_org,
    search_organisations,
)

router = APIRouter()


@router.post("/validate-client-contact", response_model=ValidateClientContactResponse)
async def validate_client_contact_endpoint(request: ValidateClientContactRequest):
    """
    Validate that a client name and primary contact pair exist in the database.
    Checks DEV.CORE.ORGHEADER and DEV.CORE.ORGCONTACT with FK relationship.
    """
    try:
        result = validate_client_contact(request.clientName, request.primaryContact)
        return ValidateClientContactResponse(
            valid=result["valid"],
            message=result["message"],
            ohPk=result.get("oh_pk"),
            ocPk=result.get("oc_pk"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation service error: {str(e)}",
        )


@router.post("/search-organisations", response_model=OrgSearchResponse)
async def search_organisations_endpoint(request: OrgSearchRequest):
    """
    Search for organisation names matching the given text.
    Used for typeahead/autocomplete on the Client Name field.
    """
    try:
        organisations = search_organisations(request.searchText)
        return OrgSearchResponse(organisations=organisations)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Organisation search failed: {str(e)}",
        )


@router.post("/search-contacts", response_model=ContactSearchResponse)
async def search_contacts_endpoint(request: ContactSearchRequest):
    """
    Search for contacts belonging to a given organisation.
    Returns a list of contact names for dropdown/autocomplete.
    """
    try:
        contacts = search_contacts_for_org(request.clientName)
        return ContactSearchResponse(contacts=contacts)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Contact search failed: {str(e)}",
        )
