#!/usr/bin/env python3
"""
Financial RAG System - Main Entry Point (Updated for Dynamic Scraper)

Usage:
    python main.py "What is Apple's P/E ratio?"
    python main.py "analyze MRF tyres FY2024"
"""

import sys
import json
from intent_classifier import classify_intent
from data_gatherer import DynamicFinancialScraper
from normalizer import normalize_and_validate
from llm_processor import process_with_llm
from cache_manager import get_cached_response, cache_response

def format_output(result: dict) -> str:
    """Format the final output for display."""
    
    output = []
    output.append("=" * 80)
    output.append("FINANCIAL RAG SYSTEM RESPONSE")
    output.append("=" * 80)
    output.append("")
    
    output.append(f"Query: {result['query']}")
    output.append(f"Intent: {result['intent']}")
    output.append("")
    
    output.append("ANSWER:")
    output.append("-" * 80)
    output.append(result['answer'])
    output.append("")
    
    output.append("SOURCES:")
    output.append("-" * 80)
    for idx, source in enumerate(result['sources'], 1):
        output.append(f"{idx}. {source.get('name', 'Unknown')}")
        if 'title' in source:
            output.append(f"   Title: {source['title']}")
        output.append(f"   URL: {source.get('url', 'Unknown')}")
        output.append("")
    
    output.append("=" * 80)
    output.append("DISCLAIMER: This response is generated from available data sources.")
    output.append("Always verify critical financial information with official sources.")
    output.append("=" * 80)
    
    return "\n".join(output)

def main(query: str):
    """Main pipeline execution with dynamic scraper."""
    
    print(f"\n{'='*80}")
    print(f"FINANCIAL RAG PIPELINE")
    print(f"{'='*80}")
    print(f"Query: {query}\n")
    
    # Step 1: Check cache
    print("[1/6] Checking cache...")
    cached = get_cached_response(query)
    if cached:
        print("      ✓ Cache hit! Returning cached response\n")
        print(format_output(cached))
        return
    print("      - Cache miss, proceeding with fresh analysis\n")
    
    # Step 2: Intent classification
    print("[2/6] Classifying intent...")
    intent = classify_intent(query)
    print(f"      ✓ Intent: {intent}\n")
    
    # Step 3: Dynamic data gathering
    print("[3/6] Gathering data dynamically...")
    print("-" * 80)
    
    scraper = DynamicFinancialScraper()
    data = scraper.gather_comprehensive_data(query)
    
    # Check if we got an error
    if 'error' in data:
        print(f"\n      ✗ Error: {data['error']}")
        print(f"\nPlease try rephrasing your query to include the company name more clearly.\n")
        sys.exit(1)
    
    print("-" * 80)
    print(f"      ✓ Data gathering complete")
    print(f"      - Company: {data.get('company_name', 'Unknown')}")
    print(f"      - Ticker: {data.get('ticker', 'Not found')}")
    print(f"      - Yahoo Finance Metrics: {len(data.get('yahoo_finance', {}))}")
    print(f"      - Articles Scraped: {len(data.get('articles', []))}\n")
    
    # Step 4: Normalization & validation
    print("[4/6] Normalizing and validating data...")
    data = normalize_and_validate(data)
    
    validation = data.get('validation', {})
    print(f"      ✓ Validation complete")
    print(f"      - Yahoo Finance data: {'✓' if validation.get('has_yahoo_data') else '✗'}")
    print(f"      - Articles validated: {validation.get('article_count', 0)}")
    
    if validation.get('warnings'):
        for warning in validation['warnings']:
            print(f"      ⚠ {warning}")
    print()
    
    # Check if we have enough data
    if not data.get('yahoo_finance') and not data.get('articles'):
        print(f"      ✗ Insufficient data gathered")
        print(f"\nUnable to generate analysis - no financial data found for {data.get('company_name')}.")
        print(f"This could mean:")
        print(f"  1. The company name was not recognized correctly")
        print(f"  2. The company is not publicly traded")
        print(f"  3. Data sources are temporarily unavailable\n")
        sys.exit(1)
    
    # Step 5: LLM processing
    print("[5/6] Processing with LLM (Worker + Checker)...")
    result = process_with_llm(query, intent, data)
    print("      ✓ LLM processing complete\n")
    
    # Step 6: Cache result
    print("[6/6] Caching result for future queries...")
    cache_response(query, result)
    print("      ✓ Cached successfully\n")
    
    # Display result
    print(format_output(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("FINANCIAL RAG SYSTEM - Usage")
        print("="*80)
        print("\nUsage: python main.py \"Your financial query here\"")
        print("\nExamples:")
        print("  python main.py \"What is Apple's P/E ratio?\"")
        print("  python main.py \"Analyze MRF tyres FY2024 financial metrics\"")
        print("  python main.py \"Why did Tesla stock drop today?\"")
        print("  python main.py \"Give me Reliance debt to equity ratio\"")
        print("  python main.py \"What is the current inflation rate?\"")
        print("  python main.py \"Explain what EBITDA means\"")
        print("\n" + "="*80 + "\n")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    try:
        main(query)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"ERROR")
        print(f"{'='*80}")
        print(f"\n{e}\n")
        
        import traceback
        print("Technical Details:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        print()
        sys.exit(1)