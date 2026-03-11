from fastapi import APIRouter, HTTPException
from models.schemas import SubmitRequest, SubmitResponse
from services.form_submit import submit_form

router = APIRouter()


@router.post("/submit", response_model=SubmitResponse)
async def submit_sales_form(request: SubmitRequest):
    """Validate and submit form data to Power Automate Flow 2."""
    # Server-side validation
    errors = []
    if not request.clientName.strip():
        errors.append("Client Name is required")
    if not request.purpose.strip():
        errors.append("Purpose is required")
    if not request.method.strip():
        errors.append("Method is required")
    if not request.status.strip():
        errors.append("Status is required")

    if errors:
        raise HTTPException(status_code=422, detail="; ".join(errors))

    try:
        result = await submit_form(request.model_dump())
        return SubmitResponse(
            status=result.get("status", "success"),
            message=result.get("message", "Form submitted successfully"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Form submission failed: {str(e)}")
