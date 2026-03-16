import asyncio
from services.azure_speech import process_transcript_text
from services.company_search import load_company_cache

async def test():
    print("Loading cache...")
    await load_company_cache()
    transcript = "We met with Cozentus today (16-March-2026). Meeting discussed AI inbox checkers improvements and new incident and claims module development with follow-up proposal preparation."
    print("\nSending transcript...")
    res = await process_transcript_text(transcript, use_raw_notes=False)
    print("\nAI Extracted Result:")
    import json
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
