import os
from dotenv import load_dotenv

load_dotenv()

AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL", "")
FLOW1_URL = os.getenv("FLOW1_URL", "https://default9a3bb30112fd4106a7f7563f72cfdf.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/a492309035b44a55a699fe2de584fbb5/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=W40V_Qr4ducBrIman7OY-LOzBPJg-cfY8J3dVozvi6w")
FLOW2_URL = os.getenv("FLOW2_URL", "https://default9a3bb30112fd4106a7f7563f72cfdf.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/fa5d86d020854bfb85d39f0d8c251d90/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=Obd2NQ4vUifMVz3slob4y5gKJGEmy64Hmm94F8iG0f4")
CARGOWISE_URL = os.getenv("CARGOWISE_URL", "https://default9a3bb30112fd4106a7f7563f72cfdf.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/923822fefc2f405e955b14c991251795/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=WDqw58nKwtKpVfuhIykBcz3uXTRc3akZ9euHYAPCorI")
COPILOT_DIRECT_LINE_SECRET = os.getenv("COPILOT_DIRECT_LINE_SECRET", "")
