"""Settings read from environment variables, with sensible defaults."""

import os

from dotenv import load_dotenv

load_dotenv()

OPENF1_BASE_URL = os.getenv("OPENF1_BASE_URL", "https://api.openf1.org/v1")
OPENF1_TIMEOUT_SECONDS = float(os.getenv("OPENF1_TIMEOUT_SECONDS", "10"))
CACHE_TTL_SEASONS_SECONDS = int(os.getenv("CACHE_TTL_SEASONS_SECONDS", "3600"))
CACHE_TTL_RESULTS_SECONDS = int(os.getenv("CACHE_TTL_RESULTS_SECONDS", "86400"))
# Season statistics need one call per round. Pause between them to stay
# comfortably under OpenF1's free-tier limit of 30 requests per minute.
OPENF1_BATCH_PAUSE_SECONDS = float(os.getenv("OPENF1_BATCH_PAUSE_SECONDS", "2.1"))
CACHE_TTL_STANDINGS_SECONDS = int(os.getenv("CACHE_TTL_STANDINGS_SECONDS", "3600"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
