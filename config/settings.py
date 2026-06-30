import os
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

POSTS_PER_RUN = int(os.getenv("POSTS_PER_RUN", "3"))
MIN_WORD_COUNT = int(os.getenv("MIN_WORD_COUNT", "1500"))
DEFAULT_CATEGORY_ID = int(os.getenv("DEFAULT_CATEGORY_ID", "1"))
DEFAULT_STATUS = os.getenv("DEFAULT_STATUS", "draft")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
