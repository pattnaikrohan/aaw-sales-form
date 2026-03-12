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
