def normalize_field_value(field_name, value):
    """Normalize descriptive labels to shortcodes for form dropdowns."""
    if not value or not isinstance(value, str):
        return value

    val = value.strip().upper()

    # METHOD MAPPING
    if field_name == 'method':
        # Shortcodes
        if val in ['PHN', 'MTG', 'EML', '1ST', 'FUP', 'SRV', 'TRV']:
            return val
        # Descriptive
        if 'PHONE' in val or 'CALL' in val: return 'PHN'
        if 'MEET' in val: return 'MTG'
        if 'EMAIL' in val: return 'EML'
        if 'FIRST' in val: return '1ST'
        if 'FOLLOW' in val or 'FUP' in val: return 'FUP'
        if 'SERVICE' in val: return 'SRV'
        if 'PORT' in val or 'VOLUME' in val: return 'TRV'

    # PURPOSE MAPPING
    if field_name == 'purpose':
        # Shortcodes
        if val in ['PBS', 'EBS', 'EFO', 'TRD']:
            return val
        # Descriptive
        if 'NEW' in val or 'PROSPECT' in val: return 'PBS'
        if 'EXISTING' in val and 'FURTHER' in val: return 'EFO'
        if 'EXISTING' in val: return 'EBS'
        if 'TRADE' in val or 'TRD' in val: return 'TRD'

    # STATUS MAPPING
    if field_name == 'status':
        # Shortcodes
        if val in ['SCH', 'COM', 'CAN', 'CUR', 'HOT', 'WRM', 'CLD']:
            return val
        # Descriptive
        if 'SCHEDULE' in val: return 'SCH'
        if 'COMPLET' in val: return 'COM'
        if 'CANCEL' in val: return 'CAN'
        if 'EXISTING' in val or 'CURRENT' in val: return 'CUR'
        if 'HOT' in val: return 'HOT'
        if 'WARM' in val: return 'WRM'
        if 'COLD' in val: return 'CLD'

    return value

def normalize_date(date_str):
    """Attempt to parse various date formats into YYYY-MM-DD for HTML5 date inputs."""
    if not date_str or not isinstance(date_str, str):
        return date_str
    
    date_str = date_str.strip()
    
    # Remove any trailing time components (e.g. " 13:45" or " 01:40:00")
    import re
    date_str = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?$', '', date_str).strip()

    # Early exit if it already looks like YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str

    from datetime import datetime
    formats = [
        "%d-%b-%y", "%d-%b-%Y", "%d %b %Y", "%d %B %Y",
        "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%d/%m/%Y",
        "%m-%d-%Y", "%d-%m-%Y", "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    # If all parsing fails, just return original
    return date_str
