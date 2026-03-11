import json
import re
import anthropic
from config import ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are the AAW Sales Assistant. Extract meeting details from the user's messages and fill the sales form.
Always respond with TWO parts:
1. A friendly message to the user
2. A JSON block like this:
```json
{"clientName":"","subject":"","method":"","purpose":"","status":"","primaryContact":"","actualDate":"","scheduledDate":"","notes":""}
```
Required fields: clientName, purpose, method, status.
Ask follow-up questions for missing required fields.
Current form state is passed in each message.

For the "method" field, use exactly one of these shortcodes based on intent: PHN, MTG, EML, 1ST, FUP, SRV, TRV.
For the "purpose" field, use exactly one of these shortcodes based on intent: PBS, EBS, EFO, TRD.
For the "status" field, use exactly one of these shortcodes based on intent: SCH, COM, CAN, CUR, HOT, WRM, CLD.

Only include fields in the JSON that you can extract from the conversation. Leave fields empty ("") if not mentioned."""

client = None


def get_client():
    global client
    if client is None:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return client


async def send_chat_message(
    message: str,
    conversation_history: list,
    current_form_state: dict,
) -> dict:
    """Send a message to Claude API and extract fields from the response."""
    api_client = get_client()

    # Build messages with form state context
    form_state_text = json.dumps(current_form_state, indent=2)
    user_content = f"{message}\n\n[Current form state: {form_state_text}]"

    messages = list(conversation_history)
    messages.append({"role": "user", "content": user_content})

    response = api_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    response_text = response.content[0].text

    # Extract JSON block from response
    extracted_fields = {}
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if json_match:
        try:
            extracted_fields = json.loads(json_match.group(1))
            # Remove empty values
            extracted_fields = {k: v for k, v in extracted_fields.items() if v}
        except json.JSONDecodeError:
            pass

    # Clean reply (remove JSON block)
    reply = re.sub(r"```json\s*\{.*?\}\s*```", "", response_text, flags=re.DOTALL).strip()

    return {
        "reply": reply,
        "extractedFields": extracted_fields,
        "rawResponse": response_text,
    }


EXTRACTION_PROMPT = """You are a data extraction assistant for a Sales Call Record form.
You will be given a snippet of conversation between a user and a sales assistant bot.
Extract any sales meeting details mentioned and return ONLY a JSON object.

The JSON must use exactly these keys (include only fields that have values):
- clientName: company or client name
- subject: meeting subject
- method: one of PHN, MTG, EML, 1ST, FUP, SRV, TRV
- purpose: one of PBS, EBS, EFO, TRD
- status: one of SCH, COM, CAN, CUR, HOT, WRM, CLD
- primaryContact: contact person name
- actualDate: date in YYYY-MM-DD format
- scheduledDate: date in YYYY-MM-DD format
- notes: any additional notes

Return ONLY the JSON object, no markdown fences, no explanation.
If no fields can be extracted, return {}."""


async def extract_fields_from_conversation(
    user_message: str,
    bot_reply: str,
    current_form_state: dict,
) -> dict:
    """Extract form fields from a Copilot Studio conversation snippet."""
    api_client = get_client()

    form_state_text = json.dumps(current_form_state, indent=2)
    content = (
        f"User said: {user_message}\n\n"
        f"Bot replied: {bot_reply}\n\n"
        f"[Current form state: {form_state_text}]"
    )

    response = api_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    response_text = response.content[0].text.strip()

    # Try to parse as JSON directly
    try:
        fields = json.loads(response_text)
        return {k: v for k, v in fields.items() if v}
    except json.JSONDecodeError:
        # Fallback: try to find JSON in the response
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            try:
                fields = json.loads(json_match.group(0))
                return {k: v for k, v in fields.items() if v}
            except json.JSONDecodeError:
                pass
    return {}
