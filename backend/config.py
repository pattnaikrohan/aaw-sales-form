import os
from dotenv import load_dotenv

load_dotenv()

AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL", "")
FLOW1_URL = os.getenv("FLOW1_URL", "")
FLOW2_URL = os.getenv("FLOW2_URL", "")
CARGOWISE_URL = os.getenv("CARGOWISE_URL", "https://aawmelservices.wisegrid.net/eadaptor")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
COPILOT_DIRECT_LINE_SECRET = os.getenv("COPILOT_DIRECT_LINE_SECRET", "")
