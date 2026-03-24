import os
from dotenv import load_dotenv

load_dotenv()

AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL", "")
FLOW1_URL = os.getenv("FLOW1_URL", "")
FLOW2_URL = os.getenv("FLOW2_URL", "")
CARGOWISE_URL = os.getenv("CARGOWISE_URL", "https://default9a3bb30112fd4106a7f7563f72cfdf.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/923822fefc2f405e955b14c991251795/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=WDqw58nKwtKpVfuhIykBcz3uXTRc3akZ9euHYAPCorI")
CARGOWISE_USERNAME = os.getenv("CARGOWISE_USERNAME", "")
CARGOWISE_PASSWORD = os.getenv("CARGOWISE_PASSWORD", "")
CARGOWISE_API_KEY = os.getenv("CARGOWISE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
COPILOT_DIRECT_LINE_SECRET = os.getenv("COPILOT_DIRECT_LINE_SECRET", "")
