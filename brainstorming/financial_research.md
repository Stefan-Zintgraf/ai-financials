# Financial Research

## Table of Contents

1. [Goal](#goal)
2. [Source Overview](#source-overview)
3. [Specialized Financial APIs](#1-specialized-financial-apis)
4. [News Aggregators & Search Engines](#2-news-aggregators--search-engines)
5. [Alternative Data & Social Sentiment](#3-alternative-data--social-sentiment)
6. [Targeted Scraping](#4-targeted-scraping)
7. [Recommended Workflow](#recommended-workflow-for-your-agent)
8. [Summary & Decision Guide](#summary--decision-guide)
9. [Perplexity API](#perplexity-api)
10. [Conclusion](#conclusion)

---

## Goal

Receive relevant news from the current day to optimize a stock portfolio. These news items should be automatically identified by an agent (e.g. via LangSmith) and then analyzed in a second step.

**Question:** What options exist to obtain as many relevant news items as possible (general stock market, markets, companies, etc.)?

To feed your agent with high-quality data, we must distinguish between sources that provide structured financial data and those that offer general market news.

---

## Source Overview

Here is an overview of the best options for obtaining relevant news for your portfolio, categorized by source type:

---

## 1. Specialized Financial APIs

*The "Professionals"* — These sources often offer structured data (JSON) linked directly to ticker symbols, making it easy for the agent to assign news to specific stocks.

### Financial Modeling Prep (FMP)

- **Benefit:** Very developer-friendly. Offers dedicated endpoints for "Stock News", "Press Releases", and even "Sentiment Analysis".
- **Relevance:** High, since news can be filtered directly by ticker (e.g. AAPL, TSLA).

### Alpha Vantage

- **Benefit:** Provides a "News & Sentiment" endpoint that delivers not only the article but also a relevance score and a sentiment score (Bullish/Bearish) for mentioned tickers.
- **Ideal for:** Pre-filtering before the LLM performs the deep analysis.

### Polygon.io

- **Benefit:** Very fast and reliable, often used by trading bots. Offers references to news from major publishers.

### Yahoo Finance (via yfinance or APIs)

- **Benefit:** Free (via Python library yfinance) or inexpensive via RapidAPI.
- **Drawback:** Often somewhat unstructured and requires more "cleaning" by the agent.

---

## 2. News Aggregators & Search Engines

*The "Broad" Sources* — Ideal for capturing macro trends (interest rate decisions, wars, commodity prices) that move the overall market.

### SerpApi (Google News / Bing News)

- **How it works:** A wrapper for Google Search. Your agent can submit targeted queries such as "Current news about Siemens Energy" or "FED interest rate decision today".
- **Benefit:** Finds extremely current articles from thousands of sources.
- **Integration:** Integrates perfectly as a tool in LangChain (GoogleSerperAPIWrapper).

### NewsAPI.org

- **Benefit:** Scans thousands of international sources (BBC, Reuters, CNN, Spiegel, Handelsblatt). You can filter by keywords, domains, or categories (e.g. "Business").
- **Drawback:** The free version often has a time delay; the Pro version is needed for real-time trading.

### GNews API

- **Benefit:** A simple and fast API specifically for Google News results.

---

## 3. Alternative Data & Social Sentiment

*The "Mood Makers"* — Stocks often move based on rumors or sentiment on social media before official news appears.

### StockTwits API

- Excellent for capturing retail investor sentiment.

### Reddit (via API Wrappers)

- Monitoring subreddits such as r/Finanzen, r/Stocks, or r/WallStreetBets.

### Twitter / X (via API)

- Unfortunately very expensive for API access nowadays, but still the fastest source for breaking news.

---

## 4. Targeted Scraping

*The "Custom Solution"* — If you prefer specific German sources, you can use RSS feeds or targeted scraping.

### RSS Feeds

- Many sites such as Tagesschau Wirtschaft, Handelsblatt, or Onvista offer RSS feeds. A simple Python script can fetch these every 10 minutes and send new entries to the agent.

### SEC EDGAR / Company Websites

- For US stocks: Direct connection to the SEC for ad-hoc announcements (8-K filings). These are the "most authentic" news items without journalistic filtering.

---

## Recommended Workflow for Your Agent

To use LangSmith and LLMs optimally, the following architecture is recommended:

### Input (Portfolio Context)

The agent receives a list of your assets (e.g. `["MSFT", "SIE.DE", "BTC-USD"]`).

### Step 1: Retrieval (The Collector)

- Use Alpha Vantage or FMP for company-specific news (high precision).
- Use SerpApi to search for macro events ("DAX development today", "ECB meeting").

### Step 2: Filtering (The Gatekeeper)

Before the expensive LLM analyzes, a lightweight algorithm filters out duplicates and irrelevant brief news items.

### Step 3: Analysis (The Analyst)

The LLM (e.g. GPT-4o) receives the article text and your portfolio.

**Prompt example:** *"Analyze this news. What impact (Positive/Negative/Neutral) does it have specifically on my position in [Stock X]? Provide an action recommendation."*

### Monitoring

With LangSmith you can trace whether the agent hallucinates or whether the retrieved sources were actually relevant.

---

## Summary & Decision Guide

| Goal | Recommended Source | Cost Factor |
|------|--------------------|-------------|
| Maximum precision per stock | Financial Modeling Prep / Alpha Vantage | Medium |
| Broad market overview | SerpApi (Google Search) | Low |
| German news | RSS Feeds (Handelsblatt etc.) / NewsAPI | Free/Low |
| Real-time / Professional level | Bloomberg Terminal API | Very High |

---

## Perplexity API

Using the Perplexity API (especially the sonar models) fundamentally changes your agent's architecture — for the better. Instead of laboriously searching, scraping, and cleaning "raw data", you delegate the entire research step to a model built exactly for that purpose.

### Why the Perplexity API (pplx-api) Makes Sense

The Perplexity models (such as sonar or sonar-pro) are online LLMs. This means they have no training cutoff for your query; they perform a real-time search in the background, read the contents of multiple web pages, and synthesize an answer with source citations.

### Benefits for Your Use Case

**Massive pipeline simplification:**

- **Classic approach:** Google Search API → List of URLs → HTML Scraper → Text Cleaning → LLM for summarization. (Error-prone and complex.)
- **Perplexity approach:** One API call: *"Summarize the most important market-relevant news for [Company X] from today."* → Finished result.

**Noise reduction:** Search engines often return SEO spam or duplicate articles. Perplexity filters this content internally and delivers a curated summary.

**Source referencing:** The API returns citations (URLs). Your agent can not only read the news but also save the link for later manual review.

**Recency:** The models are strongly tuned for "recency" (currency), which is essential for stock market news.

### Drawbacks / Risks

- **Black box:** You have less control over which sources are scanned than if you define your own "allowlist" (e.g. only Reuters, Bloomberg).
- **Hallucinations with numbers:** Although Perplexity is very good, LLMs can make errors with specific financial figures (e.g. "revenue rose 3.4%"). For sentiment it is excellent; for hard data (earnings reports) a financial API (like FMP) is still recommended as a cross-check.

### What the New Architecture Would Look Like

Instead of a two-stage process (Search → Analyze), Perplexity merges the first part.

**Step 1: The "Research Agent" (Perplexity API)**  
Send a prompt to sonar for each position in your portfolio (or for the overall market).

**Prompt example:** *"Search for the most important financial news and analyst opinions on 'Rheinmetall' and 'NVIDIA' from today, October 25, 2023. Ignore irrelevant brief news. Give me a summary of events and cite the sources."*

**Step 2: The "Portfolio Manager" (e.g. GPT-4o or Claude 3.5)**  
Take the output from Perplexity and feed it into your analysis agent. Since the text is already cleaned and condensed, you save significantly on context window and tokens.

**Prompt example:** *"Here are the summaries of today's news for my portfolio (provided by Perplexity). Based on my 'Aggressive Growth' strategy, what adjustments do you suggest?"*

### Example Code

```python
from openai import OpenAI
import os

# Perplexity API Key
PERPLEXITY_API_KEY = "pplx-xxxxxxxxxxxxxxxxxxxx"

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
)

def get_market_news(query):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional financial researcher. "
                "Your task is to find current, market-relevant news accurately. "
                "Be factual and objective."
            ),
        },
        {
            "role": "user",
            "content": query,
        },
    ]

    # 'sonar' or 'sonar-pro' are the models with online access
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
        max_tokens=1000,
    )

    content = response.choices[0].message.content

    # Perplexity provides citations often as a separate list in the response object
    # or as numbers in the text [1].
    return content

# Example call
portfolio_news = get_market_news(
    "What are the most important news today for technology stocks, "
    "specifically Microsoft and Apple? Are there any macro news from the FED?"
)

print(portfolio_news)
```

---

## Conclusion

If you are willing to bear the modest API costs of Perplexity, this is the most modern and efficient approach for your use case. It removes 80% of the "dirty work" (web scraping & parsing) so you can focus entirely on the logic of portfolio optimization.

**Recommendation:** Use Perplexity for qualitative analysis (news, sentiment, reasons) and a classic API (such as Yahoo Finance/FMP) for quantitative data (current price, P/E ratio), and let your agent combine both data points.
