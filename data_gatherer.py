"""
Dynamic Financial Data Scraper - Works for ANY company query
Uses multiple search strategies and fallbacks
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import config
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
import time
import json

class DynamicFinancialScraper:
    """Scraper that adapts to any financial query"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def extract_company_from_query(self, query: str) -> Tuple[str, str]:
        """
        Extract company name from query using multiple strategies.
        Returns: (company_name, query_type)
        """
        query_lower = query.lower()
        
        # Remove common financial terms to isolate company name
        remove_terms = [
            'analysis of', 'give me', 'show me', 'what is', 'how is',
            'p/e ratio', 'p/b ratio', 'revenue', 'profit', 'debt',
            'ebitda', 'margin', 'growth', 'dividend', 'yield',
            'on the basis of', 'fy2024', 'fy 2024', 'financial year',
            'tyres', 'tires', 'stock', 'share', 'equity', 'company'
        ]
        
        cleaned = query_lower
        for term in remove_terms:
            cleaned = cleaned.replace(term, ' ')
        
        # Extract remaining significant words
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 2]
        
        # The first significant word is usually the company
        if words:
            company_name = words[0].upper()
            return company_name, 'financial_analysis'
        
        return None, 'unknown'
    
    def search_company_ticker(self, company_name: str) -> Optional[str]:
        """
        Search for company ticker using multiple methods.
        """
        print(f"[SEARCH] Looking for ticker: {company_name}")
        
        # Method 1: Direct search via SerpAPI
        try:
            search_query = f"{company_name} stock ticker NSE BSE India"
            params = {
                "q": search_query,
                "api_key": config.SERPAPI_KEY,
                "num": 5,
                "gl": "in",
                "hl": "en"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Look for ticker in knowledge graph or featured snippet
            if 'knowledge_graph' in results:
                kg = results['knowledge_graph']
                if 'stock' in kg:
                    ticker = kg['stock']
                    print(f"[SEARCH] Found ticker in knowledge graph: {ticker}")
                    return ticker
            
            # Parse organic results for ticker mentions
            for result in results.get('organic_results', [])[:3]:
                snippet = result.get('snippet', '') + result.get('title', '')
                
                # Look for patterns like "MRF (NSE: MRF)" or "BSE: 500290"
                ticker_patterns = [
                    r'NSE:\s*([A-Z0-9]+)',
                    r'BSE:\s*([0-9]+)',
                    r'\(([A-Z]{2,10})\)',  # (MRF)
                    rf'{company_name}\s*:\s*([A-Z]{{2,10}})',
                ]
                
                for pattern in ticker_patterns:
                    match = re.search(pattern, snippet, re.IGNORECASE)
                    if match:
                        ticker = match.group(1)
                        # Add .NS suffix for NSE
                        if ticker.isalpha():
                            ticker = f"{ticker}.NS"
                        print(f"[SEARCH] Found ticker in results: {ticker}")
                        return ticker
        
        except Exception as e:
            print(f"[SEARCH] SerpAPI search failed: {e}")
        
        # Method 2: Try direct yfinance search
        try:
            # Try with .NS (NSE) suffix
            ticker_ns = f"{company_name}.NS"
            stock = yf.Ticker(ticker_ns)
            info = stock.info
            
            if info and info.get('regularMarketPrice'):
                print(f"[SEARCH] Found valid ticker: {ticker_ns}")
                return ticker_ns
        except:
            pass
        
        # Method 3: Try .BO (BSE) suffix
        try:
            ticker_bo = f"{company_name}.BO"
            stock = yf.Ticker(ticker_bo)
            info = stock.info
            
            if info and info.get('regularMarketPrice'):
                print(f"[SEARCH] Found valid ticker: {ticker_bo}")
                return ticker_bo
        except:
            pass
        
        print(f"[SEARCH] Could not find ticker for {company_name}")
        return None
    
    def fetch_yahoo_finance_comprehensive(self, ticker: str) -> Dict:
        """
        Fetch comprehensive financial data from Yahoo Finance.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Validate data
            if not info or info.get('regularMarketPrice') is None:
                return {'error': 'No data available', 'ticker': ticker}
            
            # Get historical data for growth calculations
            hist = stock.history(period="2y")
            
            data = {
                'source': 'Yahoo Finance',
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                
                # Valuation Multiples
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'peg_ratio': info.get('pegRatio'),
                
                # Profitability Metrics
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                'ebitda': info.get('ebitda'),
                'ebitda_margin': info.get('ebitdaMargins'),
                
                # Growth Metrics
                'revenue': info.get('totalRevenue'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'revenue_per_share': info.get('revenuePerShare'),
                'earnings_per_share': info.get('trailingEps'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                
                # Debt & Financial Health
                'debt_to_equity': info.get('debtToEquity'),
                'total_debt': info.get('totalDebt'),
                'total_cash': info.get('totalCash'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                
                # Returns
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'roic': info.get('returnOnCapital'),
                
                # Dividend Info
                'dividend_yield': info.get('dividendYield'),
                'dividend_rate': info.get('dividendRate'),
                'payout_ratio': info.get('payoutRatio'),
                
                # Trading Info
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'beta': info.get('beta'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                
                # Company Info
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary'),
                
                'url': f'https://finance.yahoo.com/quote/{ticker}'
            }
            
            # Calculate EBITDA/Debt ratio if possible
            if data.get('ebitda') and data.get('total_debt'):
                data['debt_ebitda_ratio'] = data['total_debt'] / data['ebitda']
            
            # Remove None values
            return {k: v for k, v in data.items() if v is not None}
        
        except Exception as e:
            print(f"[YAHOO] Error fetching {ticker}: {e}")
            return {'error': str(e), 'ticker': ticker}
    
    def search_financial_data_multi_source(self, company_name: str, query: str) -> List[Dict]:
        """
        Search for financial data across multiple sources with robust scraping.
        """
        articles = []
        
        # Build comprehensive search queries
        search_queries = [
            f"{company_name} financial results FY2024 India",
            f"{company_name} annual report 2024",
            f"{company_name} P/E ratio debt EBITDA dividend",
            f"{company_name} stock analysis Moneycontrol Screener",
            f"{company_name} quarterly results revenue growth"
        ]
        
        seen_urls = set()
        
        for search_query in search_queries:
            if len(articles) >= 5:  # Stop after getting 5 good articles
                break
            
            try:
                print(f"[SEARCH] Searching: {search_query[:50]}...")
                
                params = {
                    "q": search_query,
                    "api_key": config.SERPAPI_KEY,
                    "num": 8,
                    "gl": "in",
                    "hl": "en"
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                for result in results.get("organic_results", []):
                    url = result.get("link", "")
                    
                    # Skip duplicates and bad URLs
                    if url in seen_urls or url.endswith(('.pdf', '.doc', '.xls')):
                        continue
                    
                    seen_urls.add(url)
                    
                    # Try to scrape
                    article = self.scrape_with_fallback(url, company_name)
                    
                    if article and len(article.get('content', '')) > 300:
                        articles.append(article)
                        print(f"[SCRAPE] ✓ Scraped: {url[:60]}")
                        
                        if len(articles) >= 5:
                            break
                    
                    time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"[SEARCH] Failed: {e}")
                continue
        
        return articles
    
    def scrape_with_fallback(self, url: str, company_name: str) -> Optional[Dict]:
        """
        Scrape article with multiple fallback strategies.
        """
        strategies = [
            self._scrape_with_requests,
            self._scrape_with_cloudscraper,
            self._scrape_with_selenium
        ]
        
        for strategy in strategies:
            try:
                article = strategy(url, company_name)
                if article and len(article.get('content', '')) > 300:
                    return article
            except Exception as e:
                continue
        
        return None
    
    def _scrape_with_requests(self, url: str, company_name: str) -> Optional[Dict]:
        """Standard requests scraping"""
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            if 'text/html' not in response.headers.get('Content-Type', ''):
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract content
            article = self._extract_article_content(soup, url, company_name)
            return article
            
        except Exception as e:
            raise e
    
    def _scrape_with_cloudscraper(self, url: str, company_name: str) -> Optional[Dict]:
        """CloudScraper for sites with anti-bot protection"""
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
            
            response = scraper.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'lxml')
            
            article = self._extract_article_content(soup, url, company_name)
            return article
            
        except ImportError:
            return None
        except Exception as e:
            raise e
    
    def _scrape_with_selenium(self, url: str, company_name: str) -> Optional[Dict]:
        """Selenium for JavaScript-heavy sites"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            page_source = driver.page_source
            driver.quit()
            
            soup = BeautifulSoup(page_source, 'lxml')
            article = self._extract_article_content(soup, url, company_name)
            return article
            
        except ImportError:
            return None
        except Exception as e:
            raise e
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str, company_name: str) -> Dict:
        """Extract article content with smart parsing"""
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else "No title"
        
        # Extract date
        date_text = self._extract_date(soup)
        
        # Extract main content
        content = self._extract_main_content(soup)
        
        # Check if article is relevant
        if not self._is_relevant(content, company_name):
            return None
        
        # Extract source name
        source_name = url.split('/')[2].replace('www.', '')
        
        return {
            'title': title[:300],
            'source': source_name,
            'url': url,
            'published_date': date_text or "Unknown",
            'content': content[:5000],
            'credibility_rank': self._get_credibility_rank(source_name)
        }
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        date_selectors = [
            {'name': 'time'},
            {'attrs': {'class': re.compile(r'date|time|published', re.I)}},
            {'name': 'meta', 'attrs': {'property': 'article:published_time'}},
            {'name': 'meta', 'attrs': {'name': 'pubdate'}},
        ]
        
        for selector in date_selectors:
            elem = soup.find(**selector)
            if elem:
                date_text = elem.get('datetime') or elem.get('content') or elem.get_text(strip=True)
                if date_text:
                    return date_text
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        content = ""
        
        # Strategy 1: Article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
        
        # Strategy 2: Main content div
        if not content:
            main_content = soup.find(['main', 'div'], class_=re.compile(r'content|article|story|post-body', re.I))
            if main_content:
                paragraphs = main_content.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
        
        # Strategy 3: All paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40])
        
        # Clean content
        content = ' '.join(content.split())  # Remove extra whitespace
        
        return content
    
    def _is_relevant(self, content: str, company_name: str) -> bool:
        """Check if content is relevant to the company"""
        if not content or len(content) < 200:
            return False
        
        content_lower = content.lower()
        company_lower = company_name.lower()
        
        # Check if company name appears in content
        if company_lower in content_lower:
            return True
        
        # Check for financial keywords
        financial_keywords = ['revenue', 'profit', 'ebitda', 'p/e', 'debt', 'dividend', 'earnings']
        keyword_count = sum(1 for kw in financial_keywords if kw in content_lower)
        
        return keyword_count >= 2
    
    def _get_credibility_rank(self, source: str) -> int:
        """Rank sources by credibility"""
        rankings = {
            'reuters.com': 1,
            'bloomberg.com': 2,
            'cnbc.com': 3,
            'moneycontrol.com': 4,
            'economictimes.indiatimes.com': 5,
            'business-standard.com': 6,
            'livemint.com': 7,
            'financialexpress.com': 8,
            'screener.in': 9,
            'investing.com': 10,
            'marketwatch.com': 11,
        }
        
        for key, rank in rankings.items():
            if key in source:
                return rank
        
        return 15
    
    def gather_comprehensive_data(self, query: str) -> Dict:
        """
        Main method: Gather all financial data dynamically.
        """
        print(f"\n{'='*80}")
        print(f"DYNAMIC FINANCIAL DATA GATHERING")
        print(f"{'='*80}\n")
        
        # Extract company from query
        company_name, query_type = self.extract_company_from_query(query)
        
        if not company_name:
            return {
                'error': 'Could not extract company name from query',
                'query': query
            }
        
        print(f"[EXTRACT] Company: {company_name}")
        print(f"[EXTRACT] Query Type: {query_type}\n")
        
        # Search for ticker
        ticker = self.search_company_ticker(company_name)
        
        data = {
            'query': query,
            'company_name': company_name,
            'ticker': ticker,
            'yahoo_finance': {},
            'articles': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Fetch Yahoo Finance data
        if ticker:
            print(f"\n[YAHOO] Fetching comprehensive data for {ticker}...")
            yahoo_data = self.fetch_yahoo_finance_comprehensive(ticker)
            
            if 'error' not in yahoo_data:
                data['yahoo_finance'] = yahoo_data
                print(f"[YAHOO] ✓ Successfully fetched {len(yahoo_data)} metrics")
            else:
                print(f"[YAHOO] ✗ Error: {yahoo_data['error']}")
        else:
            print(f"[YAHOO] ✗ Skipping (no ticker found)")
        
        # Search and scrape articles
        print(f"\n[ARTICLES] Searching financial articles...")
        articles = self.search_financial_data_multi_source(company_name, query)
        data['articles'] = sorted(articles, key=lambda x: x.get('credibility_rank', 15))
        
        print(f"[ARTICLES] ✓ Found {len(articles)} relevant articles\n")
        
        print(f"{'='*80}")
        print(f"DATA GATHERING COMPLETE")
        print(f"{'='*80}\n")
        
        return data