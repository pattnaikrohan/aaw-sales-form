import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import (
    SF_ACCOUNT, SF_USER, SF_ROLE, SF_WAREHOUSE,
    SF_DATABASE, SF_SCHEMA, SF_PRIVATE_KEY_PATH,
)


def _load_private_key():
    """Load the RSA private key from the .p8 file for Snowflake key-pair auth."""
    key_path = SF_PRIVATE_KEY_PATH
    if not os.path.isabs(key_path):
        key_path = os.path.join(os.path.dirname(__file__), "..", key_path)

    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend(),
        )

    # Snowflake connector expects DER-encoded private key bytes
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return private_key_bytes


def _get_connection():
    """Create a new Snowflake connection using key-pair authentication."""
    private_key_bytes = _load_private_key()

    conn = snowflake.connector.connect(
        account=SF_ACCOUNT,
        user=SF_USER,
        private_key=private_key_bytes,
        role=SF_ROLE,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA,
    )
    return conn


def validate_client_contact(client_name: str, contact_name: str) -> dict:
    """
    Validate that a client/contact pair exists in Snowflake.

    Queries DEV.CORE.ORGHEADER joined with DEV.CORE.ORGCONTACT to confirm:
    1. The organisation (client_name) exists
    2. The contact (contact_name) belongs to that organisation

    Returns a dict with:
      - valid (bool)
      - message (str)
      - oh_pk (str | None)  — Organisation primary key
      - oc_pk (str | None)  — Contact primary key
    """
    if not client_name or not contact_name:
        return {
            "valid": False,
            "message": "Both client name and primary contact are required.",
            "oh_pk": None,
            "oc_pk": None,
        }

    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Validate the client/contact pair via the FK relationship
        query = """
            SELECT oh.OH_PK, oh.OH_FULLNAME, oc.OC_PK, oc.OC_CONTACTNAME
            FROM DEV.CORE.ORGHEADER oh
            JOIN DEV.CORE.ORGCONTACT oc ON oc.OC_OH = oh.OH_PK
            WHERE UPPER(oh.OH_FULLNAME) = UPPER(%s)
              AND UPPER(oc.OC_CONTACTNAME) = UPPER(%s)
            LIMIT 1
        """
        cursor.execute(query, (client_name.strip(), contact_name.strip()))
        row = cursor.fetchone()

        if row:
            return {
                "valid": True,
                "message": f"Valid: '{row[1]}' with contact '{row[3]}'.",
                "oh_pk": str(row[0]),
                "oc_pk": str(row[2]),
            }

        # Check if the organisation exists at all (to give a better error message)
        org_query = """
            SELECT OH_PK, OH_FULLNAME
            FROM DEV.CORE.ORGHEADER
            WHERE UPPER(OH_FULLNAME) = UPPER(%s)
            LIMIT 1
        """
        cursor.execute(org_query, (client_name.strip(),))
        org_row = cursor.fetchone()

        if org_row:
            return {
                "valid": False,
                "message": f"Organisation '{org_row[1]}' exists, but contact '{contact_name}' was not found under it.",
                "oh_pk": str(org_row[0]),
                "oc_pk": None,
            }

        return {
            "valid": False,
            "message": f"Organisation '{client_name}' not found in the database.",
            "oh_pk": None,
            "oc_pk": None,
        }

    except Exception as e:
        print(f"[Snowflake] Validation error: {e}")
        return {
            "valid": False,
            "message": f"Snowflake validation failed: {str(e)}",
            "oh_pk": None,
            "oc_pk": None,
        }
    finally:
        if conn:
            conn.close()


def search_organisations(search_text: str) -> list[str]:
    """
    Search for organisation names matching the given text using ILIKE.
    Used for typeahead/autocomplete on the Client Name field.
    Returns up to 10 matching organisation full names.
    """
    if not search_text or len(search_text) < 2:
        return []

    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT OH_FULLNAME
            FROM DEV.CORE.ORGHEADER
            WHERE OH_FULLNAME ILIKE %s
            ORDER BY OH_FULLNAME
            LIMIT 10
        """
        cursor.execute(query, (f"%{search_text.strip()}%",))
        rows = cursor.fetchall()
        return [row[0] for row in rows if row[0]]

    except Exception as e:
        print(f"[Snowflake] Organisation search error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_contacts_for_org(client_name: str) -> list[str]:
    """
    Return a list of contact names belonging to the given organisation.
    Useful for dropdown/autocomplete when the org is known but contact is not.
    """
    if not client_name:
        return []

    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        query = """
            SELECT oc.OC_CONTACTNAME
            FROM DEV.CORE.ORGCONTACT oc
            JOIN DEV.CORE.ORGHEADER oh ON oc.OC_OH = oh.OH_PK
            WHERE UPPER(oh.OH_FULLNAME) = UPPER(%s)
            ORDER BY oc.OC_CONTACTNAME
            LIMIT 50
        """
        cursor.execute(query, (client_name.strip(),))
        rows = cursor.fetchall()
        return [row[0] for row in rows if row[0]]

    except Exception as e:
        print(f"[Snowflake] Contact search error: {e}")
        return []
    finally:
        if conn:
            conn.close()
