from fastapi import APIRouter, HTTPException
from models.schemas import CompanySearchRequest, CompanySearchResponse
from services.company_search import search_companies

router = APIRouter()


@router.post("/company-search", response_model=CompanySearchResponse)
async def company_search(request: CompanySearchRequest):
    """Search for matching company names via Power Automate Flow 1."""
    try:
        companies = await search_companies(request.companySearchText)
        return CompanySearchResponse(companies=companies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company search failed: {str(e)}")
