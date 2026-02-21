# =========================
# API CONFIGURATION
# =========================

BASE_URL = "https://api.tiki.vn/product-detail/api/v1/products/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 5
MAX_RETRIES = 3

# Concurrency control
CONCURRENCY_LIMIT = 40
CHUNK_SIZE = 100


# =========================
# PIPELINE CONFIGURATION
# =========================

BATCH_SIZE = 1000
SLEEP_BETWEEN_BATCH = 0.5


# =========================
# PATH CONFIGURATION
# =========================

INPUT_FILE = "data/input/product_ids.csv"

SUCCESS_DIR = "data/processed/jsonfile"
ERROR_DIR = "data/processed/errorfile"

LOG_FILE = "logs/pipeline.log"

# =========================
# RETRY ERROR
# =========================
RETRY_SUCCESS_DIR= "data/processed/jsonfile"
RETRY_ERROR_DIR = "data/processed/errorfile"