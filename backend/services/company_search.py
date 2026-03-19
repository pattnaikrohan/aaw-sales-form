import httpx
import difflib
from config import FLOW2_URL

# In-memory cache of all company names and codes
_company_cache: list[dict] = []
_cache_loaded = False


async def load_company_cache():
    """Load all company names and codes from Dataverse via Power Automate flow.
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

            print(f"[CompanySearch] Flow response type: {type(data)}")
            
            new_cache = []
            
            # Extract common patterns for companies list
            companies_list = []
            if isinstance(data, list):
                companies_list = data
            elif isinstance(data, dict):
                # Look for common keys like 'companies', 'value', etc.
                for key in ["companies", "value", "results"]:
                    if key in data and isinstance(data[key], list):
                        companies_list = data[key]
                        break
                if not companies_list:
                    # Generic fallback: first list found in dict
                    for val in data.values():
                        if isinstance(val, list):
                            companies_list = val
                            break

            for item in companies_list:
                name = ""
                code = ""
                
                if isinstance(item, str):
                    name = item.strip()
                elif isinstance(item, dict):
                    # Prioritize exact matches from the user's Flow 2 screenshot
                    name = (item.get("helios_companyname") or 
                            item.get("name") or 
                            item.get("Company Name") or "")
                    code = (item.get("helios_companycode") or 
                            item.get("code") or 
                            item.get("Company Code") or "")
                    
                    if not name:
                        # Fallback for name: first string value
                        for v in item.values():
                            if isinstance(v, str) and v.strip():
                                name = v.strip()
                                break
                                
                if name:
                    new_cache.append({"name": name.strip(), "code": (code or "").strip()})

            _company_cache = new_cache
            _cache_loaded = True
            print(f"[CompanySearch] Loaded {len(_company_cache)} company records into cache")

    except Exception as e:
        print(f"[CompanySearch] Failed to load company cache: {e}")
        _company_cache = []


async def search_companies(search_text: str) -> list[str]:
    """Search cached company names. Returns up to 10 matching names."""
    if not _cache_loaded:
        await load_company_cache()

    if not search_text or len(search_text) < 2:
        return []

    query = search_text.lower()
    matches = [c["name"] for c in _company_cache if query in c["name"].lower()]

    return matches[:10]


def get_company_code(company_name: str) -> str:
    """Look up the company code for a given company name.
    Uses fuzzy matching to ensure we find the correct record even if capitalization or spacing differs.
    """
    if not _company_cache or not company_name:
        return ""
        
    all_names = [c["name"] for c in _company_cache]
    matches = difflib.get_close_matches(company_name, all_names, n=1, cutoff=0.8)
    
    if matches:
        matched_name = matches[0]
        for c in _company_cache:
            if c["name"] == matched_name:
                return c["code"]
    
    return ""


def fuzzy_match_company(raw_name: str, threshold: float = 0.6) -> str:
    """Find the closest company name from the cache using fuzzy matching.
    Returns the exact matched string from the cache, or the original raw_name
    if no good match is found.
    """
    if not _company_cache or not raw_name:
        return raw_name
        
    all_names = [c["name"] for c in _company_cache]
    matches = difflib.get_close_matches(
        raw_name, 
        all_names, 
        n=1, 
        cutoff=threshold
    )
    
    if matches:
        print(f"[CompanySearch] Fuzzy matched '{raw_name}' -> '{matches[0]}'")
        return matches[0]
        
    return raw_name
