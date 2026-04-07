# InternetAgent

## Overview

`InternetAgent` is a financial research automation package that combines dynamic web scraping, financial data retrieval, and LLM-driven analysis to answer finance-related queries. It is designed as a command-line tool that accepts a query, finds the target company, gathers Yahoo Finance metrics and article sources, normalizes and validates the data, and then produces a citation-rich analysis using an LLM.

## Key Features

- Dynamic company/ticker extraction from natural queries
- Multi-source financial data gathering using Yahoo Finance and web scraping
- Article scraping with fallback strategies for robust content retrieval
- Data normalization and validation for consistent analysis
- LLM worker and checker pipeline to generate verified financial responses
- Query caching for faster repeated results

## Modules

### `main.py`
- Entry point for the application.
- Runs the pipeline: cache check, intent classification, data gathering, normalization, LLM processing, and caching.
- Prints formatted output with answer and source details.

### `config.py`
- Loads environment variables from `.env` via `python-dotenv`.
- Defines configuration keys used across the package, including:
  - `GROQ_API_KEY`
  - `SERPAPI_KEY`
  - `USER_AGENT`
  - `LLM_PROVIDER`
  - `LLM_MODEL`
- Stores `CACHE_FILE` as the JSON file used for query caching.

### `data_gatherer.py`
- Implements `DynamicFinancialScraper` for flexible financial data collection.
- Extracts the company name from the query using heuristic cleanup.
- Finds the stock ticker via SerpAPI and Yahoo Finance.
- Fetches comprehensive Yahoo Finance metrics for valuation, profitability, growth, debt, returns, dividends, trading, and company details.
- Searches and scrapes multiple financial articles, ranking sources by credibility.
- Supports multiple scraping strategies: requests, cloudscraper, and Selenium.

### `enhanced_search.py`
- Provides an alternate search strategy module for building search queries and fallback search flows.
- Uses prioritized query strategies targeting SEC filings, tier-1 news, analyst research, exchange data, and general search.
- Includes utility functions for extracting entities and deduplicating source URLs.

### `fallback_handler.py`
- Defines retry and fallback utilities used to make the pipeline resilient.
- Contains `RetryConfig`, `exponential_backoff`, and `FallbackChain` helpers.
- Provides predefined fallback chains for search, scraping, and LLM operations.
- Enables graceful recovery when a primary data source or scraping method fails.

### `intent_classifier.py`
- Uses a Groq LLM instance to classify a query into one finance-related intent.
- Supported labels:
  - `FINANCIAL_METRICS`
  - `MARKET_NEWS`
  - `MACRO`
  - `GENERIC_FINANCE_QA`
- Ensures the system can choose the correct analysis mode for the query.

### `llm_processor.py`
- Runs the LLM workflow with a worker and a checker model.
- Formats financial context for the LLM from Yahoo Finance data and scraped articles.
- The worker LLM generates an answer using explicit financial prompts.
- The checker LLM verifies claims, removes hallucinations, and enforces source citations.
- Builds the final response object including answer, sources, company, and ticker.

### `normalizer.py`
- Normalizes numeric, percentage, and ratio values for consistent output.
- Converts values into readable formats like `M`, `B`, `%`, and `₹`-style metrics.
- Validates data completeness and quality, adding warnings for missing or low-quality metrics.
- Ensures the analysis input is reliable before LLM processing.

### `cache_manager.py`
- Implements simple JSON-based query caching.
- Normalizes query text and uses MD5 hashing for cache keys.
- Loads and saves results to `query_cache.json`.
- Reduces repeated LLM and scraping costs for duplicate queries.

## Requirements

- Python 3.x
- `python-dotenv`
- `yfinance`
- `requests`
- `beautifulsoup4`
- `serpapi`
- `groq`
- Optional: `cloudscraper`, `selenium`, `duckduckgo_search` for additional fallback support.

## Setup

1. Create a `.env` file in the package folder.
2. Add your API keys and model settings:

```env
GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_key
USER_AGENT=your_user_agent
LLM_PROVIDER=groq
LLM_MODEL=your_model_name
```

3. Install dependencies:

```bash
pip install python-dotenv yfinance requests beautifulsoup4 serpapi groq
```

## Usage

```bash
python main.py "What is Apple's P/E ratio?"
```

The application will print a formatted financial report along with source citations.

## Notes

- `InternetAgent` is focused on Indian and global financial queries.
- The project relies on external APIs and web scraping, so API keys and site access are required.
- Some modules reference additional helper scripts outside this package (for example, `scripts.web_search`).
- The package is designed as a prototype for financial retrieval, normalization, and LLM-driven summarization.
