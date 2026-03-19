import asyncio
import json
from unittest.mock import AsyncMock, patch
from services.form_submit import submit_form

async def test_submit_logic():
    print("Starting verification test for submit_form...")
    
    # Sample form data
    form_data = {
        "clientName": "Test Company",
        "subject": "Discussion about logistics",
        "purpose": "PBS",
        "method": "PHN",
        "status": "COM",
        "primaryContact": "John Doe",
        "actualDate": "2026-03-20",
        "scheduledDate": "2026-03-19",
        "notes": "Met with John to discuss the new route.",
        "submittedBy": "Test User"
    }

    # Mock get_company_code to return a known code
    with patch("services.form_submit.get_company_code", return_value="TC001"):
        # Mock httpx.AsyncClient.post
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "Accepted"
        mock_response.raise_for_status = AsyncMock()

        with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
            result = await submit_form(form_data)
            
            print(f"Result Status: {result['status']}")
            print(f"Result Message: {result['message']}")
            
            # Verify the payload sent to mock_post
            args, kwargs = mock_post.call_args
            sent_payload = kwargs["json"]
            
            print("\nSent Payload:")
            print(json.dumps(sent_payload, indent=2))
            
            assert sent_payload["clientName"] == "Test Company"
            assert sent_payload["company_code"] == "TC001"
            assert sent_payload["subject"] == "Discussion about logistics"
            assert "timestamp" in sent_payload
            
            print("\nVerification successful! JSON payload contains the correct company_code and form fields.")

if __name__ == "__main__":
    asyncio.run(test_submit_logic())
