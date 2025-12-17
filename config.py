import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
USER_AGENT = os.getenv("USER_AGENT")
LLM_PROVIDER = os.getenv("LLM_PROVIDER")
LLM_MODEL = os.getenv("LLM_MODEL")

APPROVED_SOURCES = [
    "reuters.com",
    "bloomberg.com",
    "economictimes.indiatimes.com",
    "moneycontrol.com",
    "cnbc.com"
]

CACHE_FILE = "query_cache.json"