import json
from datetime import datetime
from azure.storage.blob import AppendBlobClient
from azure.core.exceptions import ResourceNotFoundError
from config import (
    AZURE_STORAGE_ACCOUNT_NAME, 
    AZURE_STORAGE_SAS_TOKEN, 
    AZURE_STORAGE_CONTAINER, 
    AZURE_STORAGE_BLOB_PREFIX
)

async def log_failed_submission(payload: dict, error_message: str):
    if not AZURE_STORAGE_ACCOUNT_NAME or not AZURE_STORAGE_SAS_TOKEN:
        print("[AzureLogger] Missing Storage Account Name or SAS Token. Skipping log.")
        return
    
    try:
        account_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        
        now = datetime.utcnow()
        month_str = now.strftime("%Y_%m")
        timestamp_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        blob_name = f"{AZURE_STORAGE_BLOB_PREFIX}_{month_str}.txt"
        
        blob_url = f"{account_url}/{AZURE_STORAGE_CONTAINER}/{blob_name}?{AZURE_STORAGE_SAS_TOKEN}"
        
        client = AppendBlobClient.from_blob_url(blob_url)
        
        log_entry = (
            f"\n{'='*50}\n"
            f"Timestamp: {timestamp_str} UTC\n"
            f"Error: {error_message}\n"
            f"Payload/Transcript Data:\n{json.dumps(payload, indent=2)}\n"
            f"{'='*50}\n"
        )
        
        try:
            client.append_block(log_entry)
        except ResourceNotFoundError:
            # If the blob doesn't exist, create it and then append
            client.create_append_blob()
            client.append_block(log_entry)
            
        print(f"[AzureLogger] Successfully logged failure to {blob_name}")
        
    except Exception as e:
        print(f"[AzureLogger] Failed to write to Azure Storage: {str(e)}")
