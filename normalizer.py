from typing import Dict, Any
import re

def normalize_number(value: Any) -> str:
    """Normalize numeric values for consistency."""
    if value is None:
        return "N/A"
    
    try:
        num = float(value)
        
        # Large numbers
        if abs(num) >= 1_000_000_000_000:
            return f"{num / 1_000_000_000_000:.2f}T"
        elif abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return f"{num:.2f}"
    
    except:
        return str(value)

def normalize_percentage(value: Any) -> str:
    """Normalize percentage values."""
    if value is None:
        return "N/A"
    
    try:
        num = float(value)
        
        # If already in percentage form (0-100)
        if 0 <= abs(num) <= 1:
            return f"{num * 100:.2f}%"
        else:
            return f"{num:.2f}%"
    
    except:
        return str(value)

def normalize_ratio(value: Any) -> str:
    """Normalize ratio values."""
    if value is None:
        return "N/A"
    
    try:
        num = float(value)
        return f"{num:.2f}"
    except:
        return str(value)

def normalize_yahoo_data(yahoo_data: Dict) -> Dict:
    """Normalize Yahoo Finance data for consistency."""
    if not yahoo_data or 'error' in yahoo_data:
        return yahoo_data
    
    normalized = {
        'source': yahoo_data.get('source', 'Yahoo Finance'),
        'ticker': yahoo_data.get('ticker'),
        'company_name': yahoo_data.get('company_name'),
        
        # Valuation
        'current_price': normalize_number(yahoo_data.get('current_price')),
        'market_cap': normalize_number(yahoo_data.get('market_cap')),
        'pe_ratio': normalize_ratio(yahoo_data.get('pe_ratio')),
        'forward_pe': normalize_ratio(yahoo_data.get('forward_pe')),
        'price_to_book': normalize_ratio(yahoo_data.get('price_to_book')),
        'price_to_sales': normalize_ratio(yahoo_data.get('price_to_sales')),
        'peg_ratio': normalize_ratio(yahoo_data.get('peg_ratio')),
        
        # Profitability
        'profit_margin': normalize_percentage(yahoo_data.get('profit_margin')),
        'operating_margin': normalize_percentage(yahoo_data.get('operating_margin')),
        'gross_margin': normalize_percentage(yahoo_data.get('gross_margin')),
        'ebitda': normalize_number(yahoo_data.get('ebitda')),
        'ebitda_margin': normalize_percentage(yahoo_data.get('ebitda_margin')),
        
        # Growth
        'revenue': normalize_number(yahoo_data.get('revenue')),
        'revenue_growth': normalize_percentage(yahoo_data.get('revenue_growth')),
        'earnings_growth': normalize_percentage(yahoo_data.get('earnings_growth')),
        'revenue_per_share': normalize_number(yahoo_data.get('revenue_per_share')),
        'earnings_per_share': normalize_number(yahoo_data.get('earnings_per_share')),
        'earnings_quarterly_growth': normalize_percentage(yahoo_data.get('earnings_quarterly_growth')),
        
        # Debt & Financial Health
        'debt_to_equity': normalize_ratio(yahoo_data.get('debt_to_equity')),
        'debt_ebitda_ratio': normalize_ratio(yahoo_data.get('debt_ebitda_ratio')),
        'total_debt': normalize_number(yahoo_data.get('total_debt')),
        'total_cash': normalize_number(yahoo_data.get('total_cash')),
        'current_ratio': normalize_ratio(yahoo_data.get('current_ratio')),
        'quick_ratio': normalize_ratio(yahoo_data.get('quick_ratio')),
        
        # Returns
        'roe': normalize_percentage(yahoo_data.get('roe')),
        'roa': normalize_percentage(yahoo_data.get('roa')),
        'roic': normalize_percentage(yahoo_data.get('roic')),
        
        # Dividend
        'dividend_yield': normalize_percentage(yahoo_data.get('dividend_yield')),
        'dividend_rate': normalize_number(yahoo_data.get('dividend_rate')),
        'payout_ratio': normalize_percentage(yahoo_data.get('payout_ratio')),
        
        # Trading
        '52_week_high': normalize_number(yahoo_data.get('52_week_high')),
        '52_week_low': normalize_number(yahoo_data.get('52_week_low')),
        'beta': normalize_ratio(yahoo_data.get('beta')),
        'volume': normalize_number(yahoo_data.get('volume')),
        'avg_volume': normalize_number(yahoo_data.get('avg_volume')),
        
        # Company Info
        'sector': yahoo_data.get('sector'),
        'industry': yahoo_data.get('industry'),
        'website': yahoo_data.get('website'),
        'business_summary': yahoo_data.get('business_summary'),
        'url': yahoo_data.get('url')
    }
    
    return {k: v for k, v in normalized.items() if v != "N/A"}

def validate_data(data: Dict) -> Dict:
    """Validate and flag data quality issues."""
    
    yahoo = data.get('yahoo_finance', {})
    articles = data.get('articles', [])
    
    validation_report = {
        'has_yahoo_data': bool(yahoo and 'error' not in yahoo and len(yahoo) > 5),
        'article_count': len(articles),
        'conflicts': [],
        'warnings': []
    }
    
    # Check Yahoo Finance data quality
    if yahoo and 'error' not in yahoo:
        # Check for key metrics
        key_metrics = ['current_price', 'pe_ratio', 'market_cap']
        missing_metrics = [m for m in key_metrics if m not in yahoo or yahoo.get(m) == "N/A"]
        
        if missing_metrics:
            validation_report['warnings'].append(
                f"Missing key Yahoo metrics: {', '.join(missing_metrics)}"
            )
        
        # Check if we have enough metrics for comprehensive analysis
        if len(yahoo) < 10:
            validation_report['warnings'].append(
                f"Limited Yahoo Finance data: only {len(yahoo)} metrics available"
            )
    else:
        validation_report['warnings'].append("No valid Yahoo Finance data")
    
    # Check article quality
    if not articles:
        validation_report['warnings'].append("No articles found")
    else:
        # Check content length
        low_quality = [a for a in articles if len(a.get('content', '')) < 500]
        if low_quality:
            validation_report['warnings'].append(
                f"{len(low_quality)} articles have low content quality (< 500 chars)"
            )
        
        # Check source diversity
        sources = set(a.get('source', 'unknown') for a in articles)
        if len(sources) < 2:
            validation_report['warnings'].append(
                "Limited source diversity - all articles from similar sources"
            )
        
        # Check date freshness
        dated_articles = [a for a in articles if a.get('published_date') != "Unknown"]
        if not dated_articles:
            validation_report['warnings'].append(
                "No publication dates found - cannot verify recency"
            )
    
    # Check for complete data absence
    if not validation_report['has_yahoo_data'] and validation_report['article_count'] == 0:
        validation_report['warnings'].append(
            "⚠ CRITICAL: No data sources available - cannot generate analysis"
        )
    
    data['validation'] = validation_report
    
    return data

def normalize_and_validate(data: Dict) -> Dict:
    """Main function to normalize and validate gathered data."""
    
    # Normalize Yahoo Finance data if present
    if data.get('yahoo_finance') and 'error' not in data['yahoo_finance']:
        data['yahoo_finance'] = normalize_yahoo_data(data['yahoo_finance'])
    
    # Normalize multi-company data (for sector queries)
    if isinstance(data.get('yahoo_finance'), dict):
        # Check if it's a multi-company structure
        normalized_companies = {}
        for key, value in data['yahoo_finance'].items():
            if isinstance(value, dict) and 'ticker' in value:
                # This is company data
                normalized_companies[key] = normalize_yahoo_data(value)
            else:
                # This is a single company
                data['yahoo_finance'] = normalize_yahoo_data(data['yahoo_finance'])
                break
        
        if normalized_companies:
            data['yahoo_finance'] = normalized_companies
    
    # Validate overall data quality
    data = validate_data(data)
    
    return data