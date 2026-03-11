"""
Rivhit Dashboard — Configuration
Reads all settings from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Rivhit API ──────────────────────────────────────────────
RIVHIT_API_TOKEN = os.getenv("RIVHIT_API_TOKEN", "")
RIVHIT_BASE_URL = os.getenv(
    "RIVHIT_BASE_URL",
    "https://api.rivhit.co.il/online/RivhitOnlineAPI.svc",
)

# ── API request settings ────────────────────────────────────
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))

# ── Document-type codes we care about for the Sales page ────
# These are the Rivhit numeric document_type IDs.
# Use Document.TypeList to discover them for your account,
# then set them here. Defaults are the common Rivhit codes.
#
# ASSUMPTION: The mapping below reflects the *most common*
# Rivhit installations.  If your account uses different codes,
# override via env-vars or adjust the dict below.
SALES_DOC_TYPES: dict[int, str] = {
    1:  "חשבונית מס",
    3:  "חשבונית מס קבלה",
    9:  "חשבונית מס קבלה קופה",
    2:  "חשבונית זיכוי",
}

# You can also override via a comma-separated env-var:
#   SALES_DOC_TYPE_IDS=1,2,3,9
_override = os.getenv("SALES_DOC_TYPE_IDS")
if _override:
    SALES_DOC_TYPE_IDS = [int(x.strip()) for x in _override.split(",") if x.strip()]
else:
    SALES_DOC_TYPE_IDS = list(SALES_DOC_TYPES.keys())

# ── Date format returned by Rivhit (dd/MM/yyyy or similar) ──
RIVHIT_DATE_FORMAT = os.getenv("RIVHIT_DATE_FORMAT", "%d/%m/%Y")

# ── UI ──────────────────────────────────────────────────────
APP_TITLE = os.getenv("APP_TITLE", "Rivhit Business Dashboard")
PAGE_ICON = "📊"
