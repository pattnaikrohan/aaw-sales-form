import httpx
from config import FLOW2_URL

# In-memory cache of all company names
_company_cache: list[str] = []
_cache_loaded = False


async def load_company_cache():
    """Load all company names from Dataverse via Power Automate flow.
    Called once on startup.
    """
    global _company_cache, _cache_loaded

    if not FLOW2_URL or FLOW2_URL.startswith("<"):
        print("[CompanySearch] FLOW2_URL not configured, skipping cache load")
        return

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                FLOW2_URL,
                json={},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            # Debug: show what the flow returns
            print(f"[CompanySearch] Flow response type: {type(data)}")
            if isinstance(data, dict):
                print(f"[CompanySearch] Response keys: {list(data.keys())}")
                # Show first item for debugging
                for key, val in data.items():
                    if isinstance(val, list) and len(val) > 0:
                        print(f"[CompanySearch] First item in '{key}': {val[0]}")
            elif isinstance(data, list) and len(data) > 0:
                print(f"[CompanySearch] First item: {data[0]}")

            # Parse response — handles list of strings OR list of dicts with 'name' key
            if isinstance(data, list):
                _company_cache = []
                for item in data:
                    if isinstance(item, str) and item.strip():
                        _company_cache.append(item.strip())
                    elif isinstance(item, dict):
                        # Extract 'name' or first string value from dict
                        name = item.get("name", "") or item.get("Company Name", "")
                        if not name:
                            # Fallback: get first string value
                            for v in item.values():
                                if isinstance(v, str) and v.strip():
                                    name = v.strip()
                                    break
                        if name:
                            _company_cache.append(name.strip())
            elif isinstance(data, dict) and "companies" in data:
                _company_cache = [c.strip() for c in data["companies"] if isinstance(c, str) and c.strip()]
            else:
                # Try to extract from any list-like structure
                _company_cache = []
                for key, val in data.items():
                    if isinstance(val, list):
                        _company_cache = [c.strip() for c in val if isinstance(c, str) and c.strip()]
                        break

            _cache_loaded = True
            print(f"[CompanySearch] Loaded {len(_company_cache)} company names into cache")

    except Exception as e:
        print(f"[CompanySearch] Failed to load company cache: {e}")
        _company_cache = []


async def search_companies(search_text: str) -> list:
    """Search cached company names. Returns up to 10 matches."""
    if not _cache_loaded:
        await load_company_cache()

    if not search_text or len(search_text) < 2:
        return []

    query = search_text.lower()
    matches = [c for c in _company_cache if query in c.lower()]

    return matches[:10]
