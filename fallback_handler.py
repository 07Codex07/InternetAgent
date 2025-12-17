"""
Fallback mechanisms and error recovery for robust operation.
"""

from typing import List, Dict, Any, Callable, Optional
import time
from functools import wraps

class RetryConfig:
    def __init__(
        self,
        max_attempts: int = 3,
        backoff_base: float = 2.0,
        backoff_factor: float = 1.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_factor = backoff_factor
        self.jitter = jitter

def exponential_backoff(
    func: Callable,
    config: RetryConfig = RetryConfig(),
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry logic.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import random
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if attempt == config.max_attempts:
                    print(f"[RETRY] Final attempt failed for {func.__name__}: {e}")
                    raise
                
                # Calculate backoff
                backoff = config.backoff_factor * (config.backoff_base ** (attempt - 1))
                if config.jitter:
                    backoff *= (0.5 + random.random() * 0.5)
                
                print(f"[RETRY] Attempt {attempt} failed, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
        
        return None
    
    return wrapper

class FallbackChain:
    """
    Chain of fallback strategies for critical operations.
    """
    def __init__(self):
        self.strategies = []
    
    def add_strategy(self, name: str, func: Callable, priority: int = 0):
        """Add fallback strategy."""
        self.strategies.append({
            "name": name,
            "func": func,
            "priority": priority
        })
        self.strategies.sort(key=lambda x: x["priority"])
    
    def execute(self, *args, **kwargs) -> Optional[Any]:
        """Execute strategies in order until one succeeds."""
        last_error = None
        
        for strategy in self.strategies:
            try:
                print(f"[FALLBACK] Trying: {strategy['name']}")
                result = strategy["func"](*args, **kwargs)
                
                if result:
                    print(f"[FALLBACK] ✓ Success with: {strategy['name']}")
                    return result
                
            except Exception as e:
                print(f"[FALLBACK] ✗ Failed: {strategy['name']} - {e}")
                last_error = e
                continue
        
        print(f"[FALLBACK] All strategies exhausted")
        if last_error:
            raise last_error
        
        return None

# Search fallbacks
def create_search_fallback_chain():
    """
    Create fallback chain for search operations.
    """
    chain = FallbackChain()
    
    # Primary: SerpAPI
    def serpapi_search(query: str, num_results: int = 5) -> List[str]:
        from scripts.web_search import search_web
        return search_web(query, num_results)
    
    # Fallback 1: DuckDuckGo
    def duckduckgo_search(query: str, num_results: int = 5) -> List[str]:
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append(r.get("href"))
            return results
        except ImportError:
            print("[FALLBACK] DuckDuckGo not available (pip install duckduckgo-search)")
            return []
    
    # Fallback 2: Direct URL construction (for known sources)
    def direct_url_search(query: str, num_results: int = 5) -> List[str]:
        """Construct direct URLs to known financial sources."""
        urls = []
        query_clean = query.replace(" ", "+")
        
        # Investopedia
        urls.append(f"https://www.investopedia.com/search?q={query_clean}")
        
        # Yahoo Finance
        if any(word in query.lower() for word in ["stock", "ticker", "price", "earnings"]):
            urls.append(f"https://finance.yahoo.com/quote/{query.split()[0].upper()}")
        
        # SEC EDGAR (if company mentioned)
        urls.append(f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={query_clean}")
        
        return urls[:num_results]
    
    chain.add_strategy("serpapi", serpapi_search, priority=1)
    chain.add_strategy("duckduckgo", duckduckgo_search, priority=2)
    chain.add_strategy("direct_urls", direct_url_search, priority=3)
    
    return chain

# Scraping fallbacks
def create_scraping_fallback_chain():
    """
    Create fallback chain for web scraping.
    """
    chain = FallbackChain()
    
    # Primary: CloudScraper + BeautifulSoup
    def cloudscraper_fetch(url: str) -> str:
        from scripts.fetch_and_scrape import fetch_and_scrape, clean_text, is_pdf_url
        
        # Skip PDFs
        if is_pdf_url(url):
            return ""
        
        result = fetch_and_scrape(url)
        if result and isinstance(result, dict):
            return clean_text(result.get("text", ""))
        return ""
    
    # Fallback 1: Newspaper3k
    def newspaper_fetch(url: str) -> str:
        try:
            from newspaper import Article
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except ImportError:
            return ""
        except Exception:
            return ""
    
    # Fallback 2: Requests + BeautifulSoup
    def requests_fetch(url: str) -> str:
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts and styles
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            
            return soup.get_text(separator=" ", strip=True)
        except Exception:
            return ""
    
    # Fallback 3: Selenium (heavy, last resort)
    def selenium_fetch(url: str) -> str:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(2)  # Wait for JS
            
            text = driver.find_element("tag name", "body").text
            driver.quit()
            
            return text
        except Exception:
            return ""
    
    chain.add_strategy("cloudscraper", cloudscraper_fetch, priority=1)
    chain.add_strategy("newspaper", newspaper_fetch, priority=2)
    chain.add_strategy("requests", requests_fetch, priority=3)
    chain.add_strategy("selenium", selenium_fetch, priority=4)
    
    return chain

# LLM fallbacks
def create_llm_fallback_chain():
    """
    Create fallback chain for LLM calls.
    """
    chain = FallbackChain()
    
    def format_context(context_list):
        """Format context list into string."""
        if isinstance(context_list, str):
            return context_list
        formatted = []
        for i, ctx in enumerate(context_list[:10], 1):
            if isinstance(ctx, dict):
                url = ctx.get("url", "unknown")
                snippet = ctx.get("snippet", ctx.get("text", ctx.get("raw", "")))
                formatted.append(f"SOURCE {i}: {url}\n{snippet[:1000]}\n{'-'*80}")
            else:
                formatted.append(str(ctx))
        return "\n\n".join(formatted)
    
    def format_top_chunks(chunks_list):
        """Format top chunks list into string."""
        if isinstance(chunks_list, str):
            return chunks_list
        formatted = []
        for i, chunk in enumerate(chunks_list[:10], 1):
            if isinstance(chunk, dict):
                url = chunk.get("url", "unknown")
                text = chunk.get("text", chunk.get("snippet", ""))
                formatted.append(f"CHUNK {i} ({url}):\n{text[:1000]}\n{'-'*80}")
            else:
                formatted.append(str(chunk))
        return "\n\n".join(formatted)
    
    def parse_llm_response(response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract answer and claims."""
        import json
        import re
        
        result = {"answer": "", "claims": []}
        
        if not response_text or not isinstance(response_text, str):
            return result
        
        # Clean response - remove any binary/corrupted characters
        try:
            # Remove non-printable characters except newlines and tabs
            response_text = re.sub(r'[^\x20-\x7E\n\t]', '', response_text)
        except:
            pass
        
        # Extract answer section
        answer_match = re.search(r'---ANSWER---\s*(.*?)(?=---CLAIMS---|$)', response_text, re.DOTALL)
        if answer_match:
            result["answer"] = answer_match.group(1).strip()
        else:
            # If no markers, take everything before claims
            claims_match = re.search(r'---CLAIMS---', response_text)
            if claims_match:
                result["answer"] = response_text[:claims_match.start()].strip()
            else:
                # If no markers at all, check if it's just JSON or just text
                if response_text.strip().startswith('['):
                    # Might be just claims JSON
                    result["answer"] = ""
                else:
                    result["answer"] = response_text.strip()
        
        # Extract claims section - try multiple patterns
        claims_found = False
        
        # Pattern 1: ---CLAIMS--- marker
        claims_match = re.search(r'---CLAIMS---\s*(.*?)$', response_text, re.DOTALL)
        if claims_match:
            claims_text = claims_match.group(1).strip()
            claims_found = True
        else:
            # Pattern 2: **CLAIMS** marker
            claims_match = re.search(r'\*\*CLAIMS\*\*\s*(.*?)$', response_text, re.DOTALL)
            if claims_match:
                claims_text = claims_match.group(1).strip()
                claims_found = True
            else:
                # Pattern 3: Look for JSON array in the entire response
                json_match = re.search(r'\[[\s\S]*?\]', response_text, re.DOTALL)
                if json_match:
                    claims_text = json_match.group(0)
                    claims_found = True
        
        if claims_found:
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                claims_text = re.sub(r'^```json\s*', '', claims_text, flags=re.MULTILINE)
                claims_text = re.sub(r'^```\s*$', '', claims_text, flags=re.MULTILINE)
                claims_text = claims_text.strip()
                
                # Try to find JSON array if not already extracted
                if not claims_text.strip().startswith('['):
                    json_match = re.search(r'\[[\s\S]*?\]', claims_text, re.DOTALL)
                    if json_match:
                        claims_text = json_match.group(0)
                
                result["claims"] = json.loads(claims_text)
            except (json.JSONDecodeError, ValueError) as e:
                # Try to extract JSON array manually with better regex
                json_match = re.search(r'\[[\s\S]*?\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        result["claims"] = json.loads(json_match.group(0))
                    except:
                        result["claims"] = []
                else:
                    result["claims"] = []
        else:
            # Last resort: Try to find JSON array anywhere in response
            json_match = re.search(r'\[[\s\S]*?\]', response_text, re.DOTALL)
            if json_match:
                try:
                    result["claims"] = json.loads(json_match.group(0))
                except:
                    result["claims"] = []
        
        # Validate claims structure
        if result["claims"] and isinstance(result["claims"], list):
            # Filter out invalid claims
            valid_claims = []
            for claim in result["claims"]:
                if isinstance(claim, dict) and ("claim" in claim or "text" in claim):
                    valid_claims.append(claim)
            result["claims"] = valid_claims
        
        return result
    
    def primary_llm(worker_payload: Dict[str, Any], prompt_template: str, temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
        from scripts.llm_client import call_llm
        
        # Format context and chunks
        context_str = format_context(worker_payload.get("context", []))
        top_chunks_str = format_top_chunks(worker_payload.get("top_chunks", []))
        
        # Format prompt
        prompt = prompt_template.format(
            query=worker_payload.get("query", ""),
            context=context_str,
            top_chunks=top_chunks_str
        )
        
        # Call LLM
        response = call_llm(prompt, temperature=temperature)
        
        # Parse response
        return parse_llm_response(response)
    
    def fallback_shorter_prompt(worker_payload: Dict[str, Any], prompt_template: str, temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Retry with truncated prompt if token limit exceeded."""
        from scripts.llm_client import call_llm
        
        # Truncate context and chunks
        context_list = worker_payload.get("context", [])
        if isinstance(context_list, list):
            context_list = context_list[:3]  # Reduce to 3 sources
        
        chunks_list = worker_payload.get("top_chunks", [])
        if isinstance(chunks_list, list):
            chunks_list = chunks_list[:3]  # Reduce to 3 chunks
        
        context_str = format_context(context_list)
        top_chunks_str = format_top_chunks(chunks_list)
        
        # Format prompt
        prompt = prompt_template.format(
            query=worker_payload.get("query", ""),
            context=context_str,
            top_chunks=top_chunks_str
        )
        
        # Truncate prompt further if needed
        if len(prompt) > 8000:
            prompt = prompt[:8000] + "\n\n[Context truncated due to length]"
        
        # Call LLM
        response = call_llm(prompt, temperature=temperature)
        
        # Parse response
        return parse_llm_response(response)
    
    def fallback_simpler_model(worker_payload: Dict[str, Any], prompt_template: str, temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Retry with faster/cheaper model."""
        import os
        from scripts.llm_client import call_llm
        
        # Format context and chunks (reduced)
        context_list = worker_payload.get("context", [])[:2]
        chunks_list = worker_payload.get("top_chunks", [])[:2]
        
        context_str = format_context(context_list)
        top_chunks_str = format_top_chunks(chunks_list)
        
        # Format prompt
        prompt = prompt_template.format(
            query=worker_payload.get("query", ""),
            context=context_str,
            top_chunks=top_chunks_str
        )
        
        # Override to use faster model
        original_model = os.getenv("LLM_MODEL")
        os.environ["LLM_MODEL"] = "llama-3.1-8b-instant"  # Faster Groq model
        
        try:
            response = call_llm(prompt, temperature=temperature)
            result = parse_llm_response(response)
        finally:
            if original_model:
                os.environ["LLM_MODEL"] = original_model
            else:
                os.environ.pop("LLM_MODEL", None)
        
        return result
    
    chain.add_strategy("primary", primary_llm, priority=1)
    chain.add_strategy("truncated", fallback_shorter_prompt, priority=2)
    chain.add_strategy("simpler_model", fallback_simpler_model, priority=3)
    
    return chain

# Validation utilities
def validate_response(response: Dict[str, Any]) -> bool:
    """Validate that response contains required fields."""
    required_fields = ["answer", "claims"]
    
    if not isinstance(response, dict):
        return False
    
    for field in required_fields:
        if field not in response:
            return False
        
        if field == "answer" and not response[field]:
            return False
        
        if field == "claims" and not isinstance(response[field], list):
            return False
    
    return True

def sanitize_input(query: str) -> str:
    """Sanitize user input."""
    # Remove excessive whitespace
    query = " ".join(query.split())
    
    # Length limits
    if len(query) > 500:
        query = query[:500]
    
    # Remove potentially malicious content
    dangerous_patterns = ["<script", "javascript:", "onerror="]
    for pattern in dangerous_patterns:
        query = query.replace(pattern, "")
    
    return query.strip()