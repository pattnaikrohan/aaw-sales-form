import asyncio
import json
import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.azure_speech import process_transcript_text
from services.company_search import load_company_cache

async def test_user_transcript():
    print("--- Loading Company Cache ---")
    await load_company_cache()
    
    transcript = (
        "I had a meeting with Amazon today to see if everything is working fine or not. "
        "They were very keen to know that our Lighthouse project implementation on Snowflake. "
        "The thing is that. Uh, uh. There's mean person I talked to was Rohan and he was very keen "
        "to understand if everything is working fine or not. I'm not really sure if that's that's "
        "the case, but if that is the case, then we need to, uh, make sure everything's working fine, "
        "yeah and everything, yeah. And so, uh, tomorrow we'll be meeting the contact name is Rohan "
        "and purpose was something. Method was there that that."
    )
    
    print("\n--- Sending Transcript to AI ---")
    res = await process_transcript_text(transcript, use_raw_notes=False)
    
    print("\n--- Final Result for Frontend ---")
    print(json.dumps(res, indent=4))

if __name__ == "__main__":
    asyncio.run(test_user_transcript())
