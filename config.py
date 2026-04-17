import os
from datetime import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

COUNCILS = {
    "westminster": {
        "name": "Westminster City Council",
        "base_url": "https://idoxpa.westminster.gov.uk",
        "search_url": "https://idoxpa.westminster.gov.uk/online-applications/search.do",
        "enabled": False,
    },
    "blackpool": {
        "name": "Blackpool Council",
        "base_url": "https://idoxpa.blackpool.gov.uk",
        "search_url": "https://idoxpa.blackpool.gov.uk/online-applications/search.do",
        "enabled": True,
    },
    "tendring": {
        "name": "Tendring District Council",
        "base_url": "https://idox.tendringdc.gov.uk",
        "search_url": "https://idox.tendringdc.gov.uk/online-applications/search.do",
        "enabled": False,
    },
}

KEYWORDS = [
    "extension",
    "loft",
    "conversion",
    "new build",
    "garage",
]

SCHEDULE = {
    "enabled": True,
    "time": time(8, 0),
    "timezone": "Europe/London",
}

EMAIL = {
    "enabled": True,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    "smtp_user": "",
    "smtp_password": "",
    "from_email": "",
    "to_email": "",
}

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2
MAX_RETRIES = 3

CACHE_FILE = os.path.join(DATA_DIR, "cache.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
ERROR_LOG_FILE = os.path.join(DATA_DIR, "errors.log")