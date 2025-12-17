from groq import Groq
import config

client = Groq(api_key=config.GROQ_API_KEY)

INTENT_LABELS = [
    "FINANCIAL_METRICS",
    "MARKET_NEWS",
    "MACRO",
    "GENERIC_FINANCE_QA"
]

def classify_intent(query: str) -> str:
    """Classify user query into exactly one intent label."""
    
    prompt = f"""You are a financial query classifier. Classify the following query into EXACTLY ONE category.

Rules:
- FINANCIAL_METRICS: Questions about ratios, valuation, balance sheet, income statement, company financial analysis, P/E ratio, revenue, profit margins, debt, equity, ROE, ROA, etc.
- MARKET_NEWS: Questions about recent news, events, stock price movements, market reactions, why a stock went up/down, recent announcements
- MACRO: Questions about economy, inflation, interest rates, GDP, monetary policy, fiscal policy, economic indicators, Fed decisions
- GENERIC_FINANCE_QA: Questions asking for definitions, explanations of financial concepts, how things work in finance

Query: {query}

Output ONLY the label. No explanation. No formatting."""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=config.LLM_MODEL,
        temperature=0,
        max_tokens=50
    )
    
    intent = response.choices[0].message.content.strip()
    
    # Validate and clean
    for label in INTENT_LABELS:
        if label in intent.upper():
            return label
    
    # Default fallback
    return "GENERIC_FINANCE_QA"