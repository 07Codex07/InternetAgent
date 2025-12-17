
"""
Enhanced search with multiple strategies and fallbacks.
Targets specific authoritative sources for financial data.
"""

from typing import List, Dict, Any
import time
from scripts.web_search import search_web

def build_search_queries(query: str, entity: str = None) -> List[Dict[str, str]]:
    """
    Generate multiple search queries with different strategies.
    Returns list of {query, strategy, priority}
    """
    queries = []
    
    # Strategy 1: SEC filings (highest priority for US stocks)
    if entity:
        queries.append({
            "query": f"{entity} SEC filing site:sec.gov",
            "strategy": "sec_filing",
            "priority": 1
        })
        queries.append({
            "query": f"{entity} 10-K site:sec.gov",
            "strategy": "sec_10k",
            "priority": 1
        })
    
    # Strategy 2: Financial data providers
    queries.append({
        "query": f"{query} site:bloomberg.com OR site:reuters.com OR site:wsj.com",
        "strategy": "tier1_news",
        "priority": 2
    })
    
    # Strategy 3: Analyst ratings & research
    queries.append({
        "query": f"{query} analyst rating site:morningstar.com OR site:seekingalpha.com",
        "strategy": "analyst_research",
        "priority": 2
    })
    
    # Strategy 4: Exchange data
    if entity:
        queries.append({
            "query": f"{entity} site:nasdaq.com OR site:nyse.com",
            "strategy": "exchange_data",
            "priority": 3
        })
    
    # Strategy 5: Broad financial media
    queries.append({
        "query": f"{query} site:investopedia.com OR site:cnbc.com OR site:marketwatch.com",
        "strategy": "tier2_news",
        "priority": 3
    })
    
    # Strategy 6: General search (fallback)
    queries.append({
        "query": query,
        "strategy": "general",
        "priority": 4
    })
    
    return sorted(queries, key=lambda x: x["priority"])

def search_with_fallback(
    query: str, 
    entity: str = None,
    min_sources: int = 5,
    max_attempts: int = 3
) -> List[str]:
    """
    Execute multi-strategy search with fallback.
    Returns deduplicated list of URLs.
    """
    all_urls = []
    seen_urls = set()
    
    search_queries = build_search_queries(query, entity)
    
    for sq in search_queries:
        if len(all_urls) >= min_sources:
            break
        
        print(f"[SEARCH] Strategy: {sq['strategy']}, Query: {sq['query'][:60]}...")
        
        try:
            urls = search_web(sq["query"], num_results=5)
            
            for url in urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_urls.append(url)
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"[SEARCH] Failed for {sq['strategy']}: {e}")
            continue
    
    print(f"[SEARCH] ✓ Found {len(all_urls)} unique sources")
    return all_urls

def extract_entity_from_query(query: str) -> str:
    """
    Extract company/ticker from query.
    Simple heuristic - can be enhanced with NER.
    """
    query_lower = query.lower()
    
    # Remove common question words
    for word in ["should i", "is", "the", "a", "an", "invest in", "buy", "sell"]:
        query_lower = query_lower.replace(word, "")
    
    # Extract first significant word (usually the entity)
    words = query_lower.strip().split()
    if words:
        return words[0].upper()
    
    return None

# Usage example
if __name__ == "__main__":
    query = "should I invest in Tesla"
    entity = extract_entity_from_query(query)
    
    urls = search_with_fallback(query, entity, min_sources=8)
    
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")