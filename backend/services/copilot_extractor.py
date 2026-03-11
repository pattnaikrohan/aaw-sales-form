import httpx
import asyncio
import json
from config import COPILOT_DIRECT_LINE_SECRET

DIRECT_LINE_BASE = "https://directline.botframework.com/v3/directline"


async def extract_fields_from_transcript(transcript: str, current_datetime: str) -> dict:
    """Call a Copilot Studio agent via Direct Line API to extract structured fields from a transcript.

    Args:
        transcript: The speech-to-text transcript.
        current_datetime: Current datetime string (e.g. "11-MAR-26 07:25") for date resolution.

    Returns:
        dict with keys: clientName, subject, method, purpose, status,
                        primaryContact, actualDate, notes
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Generate a token from the Direct Line secret
        token_response = await client.post(
            f"{DIRECT_LINE_BASE}/tokens/generate",
            headers={
                "Authorization": f"Bearer {COPILOT_DIRECT_LINE_SECRET}",
            },
        )
        token_response.raise_for_status()
        token = token_response.json()["token"]

        auth_header = {"Authorization": f"Bearer {token}"}

        # 2. Start a new conversation
        conv_response = await client.post(
            f"{DIRECT_LINE_BASE}/conversations",
            headers=auth_header,
        )
        conv_response.raise_for_status()
        conv_data = conv_response.json()
        conversation_id = conv_data["conversationId"]

        # 3. Send the transcript + datetime as a message to the agent
        message_payload = {
            "type": "message",
            "from": {"id": "python-backend"},
            "text": f"{transcript}\n\nCurrentDateTime: {current_datetime}",
        }
        send_response = await client.post(
            f"{DIRECT_LINE_BASE}/conversations/{conversation_id}/activities",
            headers=auth_header,
            json=message_payload,
        )
        send_response.raise_for_status()

        # 4. Poll for the bot's response (the agent's extraction result)
        watermark = None
        max_attempts = 30  # Up to 60 seconds (30 attempts × 2s)
        for attempt in range(max_attempts):
            await asyncio.sleep(2)

            params = {}
            if watermark:
                params["watermark"] = watermark

            poll_response = await client.get(
                f"{DIRECT_LINE_BASE}/conversations/{conversation_id}/activities",
                headers=auth_header,
                params=params,
            )
            poll_response.raise_for_status()
            poll_data = poll_response.json()
            watermark = poll_data.get("watermark")

            # Look for bot responses (not our own message)
            for activity in poll_data.get("activities", []):
                if (
                    activity.get("type") == "message"
                    and activity.get("from", {}).get("id") != "python-backend"
                    and activity.get("text")
                ):
                    return _parse_agent_response(activity["text"])

        # If no response after max attempts, return empty
        return {}


def _parse_agent_response(text: str) -> dict:
    """Parse the JSON response from the Copilot Studio agent."""
    text = text.strip()

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in fenced block
    import re
    json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find any JSON object
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return {}
