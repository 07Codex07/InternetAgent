import json
import hashlib
from typing import Dict, Optional
import config
import os

def normalize_query(query: str) -> str:
    """Normalize query for cache key generation."""
    return query.lower().strip()

def generate_cache_key(query: str) -> str:
    """Generate a consistent cache key from query."""
    normalized = normalize_query(query)
    return hashlib.md5(normalized.encode()).hexdigest()

def load_cache() -> Dict:
    """Load cache from file."""
    if not os.path.exists(config.CACHE_FILE):
        return {}
    
    try:
        with open(config.CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return {}

def save_cache(cache: Dict) -> None:
    """Save cache to file."""
    try:
        with open(config.CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def get_cached_response(query: str) -> Optional[Dict]:
    """Get cached response for query."""
    cache = load_cache()
    key = generate_cache_key(query)
    
    if key in cache:
        print(f"Cache hit for query: {query}")
        return cache[key]
    
    return None

def cache_response(query: str, response: Dict) -> None:
    """Cache a response."""
    cache = load_cache()
    key = generate_cache_key(query)
    cache[key] = response
    save_cache(cache)
    print(f"Cached response for query: {query}")