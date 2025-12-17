from groq import Groq
import config
from typing import Dict
import json

client = Groq(api_key=config.GROQ_API_KEY)

def format_data_for_llm(data: Dict) -> str:
    """Format gathered data into a clear context for the LLM."""
    
    context_parts = []
    
    # Add company and query info
    if data.get('company_name'):
        context_parts.append(f"=== COMPANY INFORMATION ===")
        context_parts.append(f"Company Name: {data['company_name']}")
        context_parts.append(f"Ticker Symbol: {data.get('ticker', 'Not Found')}")
        context_parts.append("")
    
    # Add Yahoo Finance data
    yahoo = data.get('yahoo_finance', {})
    if yahoo and 'error' not in yahoo:
        context_parts.append("=== YAHOO FINANCE DATA ===")
        context_parts.append(f"Data Source: Yahoo Finance")
        context_parts.append(f"URL: {yahoo.get('url', 'https://finance.yahoo.com')}")
        context_parts.append("")
        
        # Organize metrics by category
        if yahoo.get('company_name'):
            context_parts.append(f"Company: {yahoo['company_name']}")
        
        # Valuation Multiples
        context_parts.append("\n--- Valuation Multiples ---")
        if yahoo.get('current_price'):
            context_parts.append(f"Current Price: ₹{yahoo['current_price']}")
        if yahoo.get('market_cap'):
            context_parts.append(f"Market Cap: {yahoo['market_cap']}")
        if yahoo.get('pe_ratio'):
            context_parts.append(f"P/E Ratio (Trailing): {yahoo['pe_ratio']}")
        if yahoo.get('forward_pe'):
            context_parts.append(f"P/E Ratio (Forward): {yahoo['forward_pe']}")
        if yahoo.get('price_to_book'):
            context_parts.append(f"P/B Ratio: {yahoo['price_to_book']}")
        if yahoo.get('price_to_sales'):
            context_parts.append(f"P/S Ratio: {yahoo['price_to_sales']}")
        if yahoo.get('peg_ratio'):
            context_parts.append(f"PEG Ratio: {yahoo['peg_ratio']}")
        
        # Profitability Metrics
        context_parts.append("\n--- Profitability Metrics ---")
        if yahoo.get('ebitda'):
            context_parts.append(f"EBITDA: {yahoo['ebitda']}")
        if yahoo.get('ebitda_margin'):
            context_parts.append(f"EBITDA Margin: {yahoo['ebitda_margin']}")
        if yahoo.get('profit_margin'):
            context_parts.append(f"Profit Margin: {yahoo['profit_margin']}")
        if yahoo.get('operating_margin'):
            context_parts.append(f"Operating Margin: {yahoo['operating_margin']}")
        if yahoo.get('gross_margin'):
            context_parts.append(f"Gross Margin: {yahoo['gross_margin']}")
        
        # Growth Metrics
        context_parts.append("\n--- Growth Metrics ---")
        if yahoo.get('revenue'):
            context_parts.append(f"Total Revenue: {yahoo['revenue']}")
        if yahoo.get('revenue_growth'):
            context_parts.append(f"Revenue Growth: {yahoo['revenue_growth']}")
        if yahoo.get('earnings_per_share'):
            context_parts.append(f"EPS (Earnings Per Share): {yahoo['earnings_per_share']}")
        if yahoo.get('earnings_growth'):
            context_parts.append(f"Earnings Growth: {yahoo['earnings_growth']}")
        if yahoo.get('earnings_quarterly_growth'):
            context_parts.append(f"Quarterly Earnings Growth: {yahoo['earnings_quarterly_growth']}")
        if yahoo.get('revenue_per_share'):
            context_parts.append(f"Revenue Per Share: {yahoo['revenue_per_share']}")
        
        # Debt & Financial Health
        context_parts.append("\n--- Debt & Financial Health ---")
        if yahoo.get('debt_to_equity'):
            context_parts.append(f"Debt-to-Equity Ratio: {yahoo['debt_to_equity']}")
        if yahoo.get('debt_ebitda_ratio'):
            context_parts.append(f"Debt/EBITDA Ratio: {yahoo['debt_ebitda_ratio']}")
        if yahoo.get('total_debt'):
            context_parts.append(f"Total Debt: {yahoo['total_debt']}")
        if yahoo.get('total_cash'):
            context_parts.append(f"Total Cash: {yahoo['total_cash']}")
        if yahoo.get('current_ratio'):
            context_parts.append(f"Current Ratio: {yahoo['current_ratio']}")
        if yahoo.get('quick_ratio'):
            context_parts.append(f"Quick Ratio: {yahoo['quick_ratio']}")
        
        # Returns
        context_parts.append("\n--- Return Metrics ---")
        if yahoo.get('roe'):
            context_parts.append(f"ROE (Return on Equity): {yahoo['roe']}")
        if yahoo.get('roa'):
            context_parts.append(f"ROA (Return on Assets): {yahoo['roa']}")
        if yahoo.get('roic'):
            context_parts.append(f"ROIC (Return on Invested Capital): {yahoo['roic']}")
        
        # Dividend Info
        context_parts.append("\n--- Dividend Information ---")
        if yahoo.get('dividend_yield'):
            context_parts.append(f"Dividend Yield: {yahoo['dividend_yield']}")
        if yahoo.get('dividend_rate'):
            context_parts.append(f"Dividend Rate: {yahoo['dividend_rate']}")
        if yahoo.get('payout_ratio'):
            context_parts.append(f"Payout Ratio: {yahoo['payout_ratio']}")
        
        # Trading Info
        context_parts.append("\n--- Trading Information ---")
        if yahoo.get('52_week_high'):
            context_parts.append(f"52-Week High: {yahoo['52_week_high']}")
        if yahoo.get('52_week_low'):
            context_parts.append(f"52-Week Low: {yahoo['52_week_low']}")
        if yahoo.get('beta'):
            context_parts.append(f"Beta: {yahoo['beta']}")
        if yahoo.get('volume'):
            context_parts.append(f"Volume: {yahoo['volume']}")
        
        # Company Details
        context_parts.append("\n--- Company Details ---")
        if yahoo.get('sector'):
            context_parts.append(f"Sector: {yahoo['sector']}")
        if yahoo.get('industry'):
            context_parts.append(f"Industry: {yahoo['industry']}")
        if yahoo.get('website'):
            context_parts.append(f"Website: {yahoo['website']}")
        if yahoo.get('business_summary'):
            summary = yahoo['business_summary'][:500]
            context_parts.append(f"Business Summary: {summary}...")
        
        context_parts.append("\n")
    
    # Add articles
    articles = data.get('articles', [])
    for idx, article in enumerate(articles, 1):
        context_parts.append(f"=== ARTICLE {idx} ===")
        context_parts.append(f"Title: {article.get('title', 'N/A')}")
        context_parts.append(f"Source: {article.get('source', 'N/A')}")
        context_parts.append(f"Date: {article.get('published_date', 'N/A')}")
        context_parts.append(f"URL: {article.get('url', 'N/A')}")
        context_parts.append(f"Credibility Rank: {article.get('credibility_rank', 'N/A')}/15")
        context_parts.append(f"\nContent Preview:")
        context_parts.append(f"{article.get('content', 'N/A')[:2500]}")
        context_parts.append("")
    
    return "\n".join(context_parts)

def worker_llm(query: str, intent: str, data: Dict) -> str:
    """Worker LLM that analyzes data and generates response."""
    
    context = format_data_for_llm(data)
    
    system_prompt = """You are an expert financial analyst AI. Your job is to provide comprehensive, accurate analysis using ONLY the provided data.

CRITICAL RULES:
1. Use ONLY information from the provided context - never use outside knowledge
2. Cite sources for EVERY claim with exact format: "According to [Source Name]..." or "[Source] reports..."
3. For numeric data, always cite Yahoo Finance explicitly
4. If asked for specific metrics and they're available, provide them clearly with proper formatting
5. If data is unavailable, state it explicitly: "This metric is not available in the provided data"
6. Never hallucinate or make up numbers
7. Be precise with financial terminology
8. Format numbers clearly (₹ for Indian stocks, use M/B for millions/billions)
9. If multiple sources provide conflicting information, mention the conflict
10. Structure your response clearly with headers for different metrics

For financial analysis queries:
- Organize response by the metrics requested (P/E, P/B, Growth, Margins, etc.)
- Compare metrics to industry averages if that data is available
- Provide context for what the numbers mean (is a P/E of 30 high or low?)
- Highlight any red flags or positive indicators"""

    user_prompt = f"""Query: {query}
Intent: {intent}
Company: {data.get('company_name', 'Unknown')}

Available Financial Data:
{context}

Provide a comprehensive analysis addressing all aspects of the query. Structure your response clearly with sections for each requested metric. Always cite your sources."""

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=config.LLM_MODEL,
        temperature=0.1,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def checker_llm(query: str, worker_response: str, data: Dict) -> str:
    """Checker LLM that verifies claims and removes unsupported statements."""
    
    context = format_data_for_llm(data)
    
    system_prompt = """You are a rigorous fact-checker AI specialized in financial data verification.

YOUR TASK:
1. Verify EVERY numeric claim against the source data
2. Check that EVERY claim has a proper source citation
3. Remove any statements not supported by the provided data
4. Flag and remove any potential hallucinations
5. Ensure financial terminology is used correctly
6. Verify that metric calculations are accurate
7. Return ONLY the corrected, verified response

VERIFICATION CHECKLIST:
✓ Every number has a source citation
✓ Every claim is backed by the provided data
✓ No outside knowledge is used
✓ Financial terms are used correctly
✓ Calculations are accurate
✓ Response addresses the user's specific questions

If the worker response contains unsupported claims, remove them and note what was removed."""

    user_prompt = f"""Original Query: {query}

Worker Response to Verify:
{worker_response}

Source Data to Verify Against:
{context}

Task: Carefully verify every claim in the worker response. Remove anything unsupported. Return the corrected response.

If metrics are missing, keep the statement that they're unavailable. Only remove claims that are fabricated or not backed by data."""

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=config.LLM_MODEL,
        temperature=0,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def process_with_llm(query: str, intent: str, data: Dict) -> Dict:
    """Process data through worker and checker LLMs."""
    
    print("      → Worker LLM analyzing data...")
    worker_response = worker_llm(query, intent, data)
    
    print("      → Checker LLM verifying response...")
    checked_response = checker_llm(query, worker_response, data)
    
    return {
        'query': query,
        'intent': intent,
        'company': data.get('company_name', 'Unknown'),
        'ticker': data.get('ticker', 'Unknown'),
        'answer': checked_response,
        'sources': extract_sources(data),
        'timestamp': data.get('timestamp')
    }

def extract_sources(data: Dict) -> list:
    """Extract list of sources used."""
    sources = []
    
    yahoo = data.get('yahoo_finance', {})
    if yahoo and 'error' not in yahoo:
        sources.append({
            'name': 'Yahoo Finance',
            'url': yahoo.get('url', 'https://finance.yahoo.com'),
            'type': 'Financial Data Provider'
        })
    
    for article in data.get('articles', []):
        sources.append({
            'name': article.get('source', 'Unknown'),
            'url': article.get('url', 'Unknown'),
            'title': article.get('title', 'Unknown'),
            'type': 'News Article',
            'date': article.get('published_date', 'Unknown')
        })
    
    return sources