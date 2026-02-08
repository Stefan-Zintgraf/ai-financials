# AI-Driven Portfolio Management — Research & Architecture

## Table of Contents

1. [Goal](#goal)
   - [General Overview](#general-overview)
   - [System Overview](#system-overview)
2. [Architecture Overview](#architecture-overview)
3. [Part I: Investment Universe & Asset Selection](#part-i-investment-universe--asset-selection)
   - [Universe Sources & Composition](#universe-sources--composition)
   - [Master Allow-List (Optional Constraint Layer)](#master-allow-list-optional-constraint-layer)
   - [Continuous Universe Updates](#continuous-universe-updates)
   - [Universe: Optimization & Review](#universe-optimization--review)
4. [Part II: News Retrieval](#part-ii-news-retrieval)
   - [Specialized Financial APIs](#specialized-financial-apis)
   - [News Aggregators & Search Engines](#news-aggregators--search-engines)
   - [AI-Native Search APIs](#ai-native-search-apis)
   - [Alternative Data & Social Sentiment](#alternative-data--social-sentiment)
   - [Regulatory Filings & Targeted Scraping](#regulatory-filings--targeted-scraping)
   - [Data Latency & Real-Time Considerations](#data-latency--real-time-considerations)
   - [Retrieval: Optimization & Review](#retrieval-optimization--review)
5. [Part III: News Evaluation](#part-iii-news-evaluation)
   - [Pre-Filtering](#1-pre-filtering-the-gatekeeper)
   - [Sentiment Analysis](#2-sentiment-analysis)
   - [Portfolio-Specific Impact Assessment](#3-portfolio-specific-impact-assessment)
   - [Noise Reduction Strategies](#4-noise-reduction-strategies)
   - [Evaluation: Optimization & Review](#evaluation-optimization--review)
6. [Part IV: Data Preparation for AI](#part-iv-data-preparation-for-ai)
   - [Structured News Schema](#1-structured-news-schema)
   - [Text Cleaning & Normalization](#2-text-cleaning--normalization)
   - [Vector Databases & Embeddings](#3-vector-databases--embeddings)
   - [Document Chunking Strategies](#4-document-chunking-strategies)
   - [Caching & Incremental Updates](#5-caching--incremental-updates)
   - [Preparation: Optimization & Review](#preparation-optimization--review)
7. [Part V: Portfolio Context & Quantitative Data](#part-v-portfolio-context--quantitative-data)
   - [Context: Optimization & Review](#context-optimization--review)
8. [Part VI: AI-Powered Analysis & Decision Making](#part-vi-ai-powered-analysis--decision-making)
   - [Decision Documentation & Anti-Hallucination](#decision-documentation--anti-hallucination)
   - [Analysis: Optimization & Review](#analysis-optimization--review)
9. [Part VII: Possible Workflows](#part-vii-possible-workflows)
   - [Workflow A: One-Shot LLM](#workflow-a-one-shot-llm-zero-infrastructure)
   - [Workflow B: Research API-First](#workflow-b-research-api-first-simplified-pipeline)
   - [Workflow C: Classic Pipeline](#workflow-c-classic-pipeline)
   - [Workflow D: Multi-Agent Architecture](#workflow-d-multi-agent-architecture-langgraph)
   - [Workflow E: Mandate-Driven Autonomous Agent](#workflow-e-mandate-driven-autonomous-agent)
   - [Monitoring & Observability](#monitoring--observability)
10. [Part VIII: Evaluation & Optimization Framework](#part-viii-evaluation--optimization-framework)
    - [Review Document Standard](#review-document-standard)
    - [Experiment Tracking](#experiment-tracking)
    - [Human Review Workflow](#human-review-workflow)
    - [AI-Assisted Optimization](#ai-assisted-optimization)
    - [Backtesting Framework](#backtesting-framework)
    - [A/B Testing Pipeline Configurations](#ab-testing-pipeline-configurations)
    - [Optimization Cadence](#optimization-cadence)
    - [Decision Audit Integration](#decision-audit-integration)
11. [Part IX: Continuous Self-Optimization](#part-ix-continuous-self-optimization)
    - [Counterfactual Analysis Engine](#1-counterfactual-analysis-engine)
    - [Parameter Staleness Detection](#2-parameter-staleness-detection)
    - [Drift Detection & Market Regime Awareness](#3-drift-detection--market-regime-awareness)
    - [Shadow Mode (Canary Testing)](#4-shadow-mode-canary-testing)
    - [Automated Parameter Rollout](#5-automated-parameter-rollout)
    - [Self-Optimization Safety Rails](#6-self-optimization-safety-rails)
    - [Self-Optimization Architecture](#self-optimization-architecture)
12. [Source Decision Guide](#source-decision-guide)
13. [Appendix A: Online Research LLMs — Deep Dive](#appendix-a-online-research-llms--deep-dive)
14. [Appendix B: Implementation Guide](#appendix-b-implementation-guide)
    - [Programming Language](#programming-language)
    - [Core Libraries & Frameworks](#core-libraries--frameworks)
    - [MCP Servers for Financial Data](#mcp-servers-for-financial-data)
    - [Modular Architecture](#modular-architecture)
    - [Testing Strategy](#testing-strategy)
    - [Test-Driven Development (TDD)](#test-driven-development-tdd)
    - [Architectural Guides & Coding Conventions](#architectural-guides--coding-conventions)
    - [Additional Guardrails](#additional-guardrails)
15. [Appendix C: Implementation Resources & Reference Materials](#appendix-c-implementation-resources--reference-materials)
    - [Primary Resources (User-Provided)](#primary-resources-user-provided)
    - [Additional Recommended Resources](#additional-recommended-resources)
    - [Pre-Implementation Reference File Strategy](#pre-implementation-reference-file-strategy)
16. [Legal & Compliance Considerations](#legal--compliance-considerations)
17. [Conclusion](#conclusion)

---

## Goal

**Manage a stock portfolio using AI-driven analysis.** An autonomous agent continuously collects market information, evaluates it against the current portfolio, and recommends concrete actions — buy, sell, hold, or rebalance — with documented reasoning. The system is designed to be self-improving: every pipeline stage produces auditable artifacts and tunable parameters whose optimal values are discovered through systematic experimentation.

### General Overview

The system follows a structured investment process: define which assets to watch, gather relevant market information, filter and evaluate it, then produce actionable recommendations — buy, sell, hold, or rebalance. Five workflows of increasing sophistication are available, ranging from a simple AI prompt all the way to a fully autonomous multi-agent system. Alternatively, the entire process can be delegated to a single AI agent guided by a mandate document that describes investment goals and constraints in plain language.

Regardless of the chosen workflow, three principles apply throughout:

- **Transparency** — every AI decision is documented with its reasoning, evidence, and confidence level.
- **Human oversight** — a review and evaluation framework lets humans audit the system, run backtests, and compare configurations.
- **Continuous improvement** — the system monitors its own performance and proposes parameter adjustments, subject to safety guardrails.

### System Overview

The pipeline consists of nine interconnected parts, forming a continuous feedback loop:

| Stage | Purpose | Key Inputs / Outputs |
|-------|---------|---------------------|
| **Part I — Investment Universe** | Maintain a dynamic list of candidate assets (stocks, ETFs, crypto, commodities) filtered by an optional master allow-list | Indices, screeners, watchlists → active ticker list |
| **Part II — Data Collection** | Gather financial news, market data, sentiment, and regulatory filings | Ticker list → raw articles, headlines, filings |
| **Part III — Evaluation** | Deduplicate, score relevance, assess sentiment and impact | Raw data → filtered, scored news items |
| **Part IV — Data Preparation** | Structure data for AI consumption via embeddings, vector storage, chunking | Scored items → optimized context documents |
| **Part V — Portfolio Context** | Enrich with current holdings, prices, fundamentals, and technical indicators | Context documents + portfolio state → complete analysis context |
| **Part VI — Analysis & Decision** | LLM-powered analysis producing buy/sell/hold/rebalance recommendations with confidence levels and documented reasoning | Complete context → documented recommendations |
| **Part VII — Workflows** | Five concrete implementation architectures (A–E) from simplest to most agentic | — |
| **Part VIII — Evaluation & Optimization** | Human-driven experiment tracking, review cadences, backtesting, and A/B testing across all stages | Review docs from all parts → parameter adjustments |
| **Part IX — Self-Optimization** | Autonomous counterfactual analysis, staleness detection, drift monitoring, shadow-mode testing, and guardrailed parameter rollout | Run data + market outcomes → continuous parameter updates |

Data flows top-down from universe definition through analysis, while evaluation and self-optimization feed adjustments back into every stage. News retrieval (Part II) is one of several data streams — alongside price data, fundamentals, technical indicators, and strategy constraints — that feed the analysis engine. The investment universe (Part I), together with the current portfolio and available liquidity, forms the basis for all decisions.

**Workflows at a glance:**

| Workflow | Approach | Complexity | When to use |
|----------|----------|-----------|-------------|
| **A — One-Shot LLM** | Single prompt to an LLM with web search | Minimal | Prompt prototyping, baseline |
| **B — Research API-First** | Online research LLM + separate analysis LLM | Low | First production-grade pipeline |
| **C — Classic Pipeline** | Discrete modules for each Part (I–VI) | Medium | Full control over every stage |
| **D — Multi-Agent (LangGraph)** | Specialized agents collaborating via LangGraph | High | Maximum flexibility and parallelism |
| **E — Mandate-Driven Agent** | Single mandate document → autonomous agent | Variable (L1: low, L2: high) | Delegate entire process to agent |

Workflows A–D implement the explicit pipeline; Workflow E replaces it with a mandate-driven agent. Workflow E Level 1 is implementable right after Workflow B; Level 2 requires the infrastructure from Workflow D.

---

## Architecture Overview

The following diagram shows how the major parts of this system connect:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PORTFOLIO CONTEXT                            │
│  Current holdings, strategy rules, risk constraints, cash position  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  PART I: INVESTMENT UNIVERSE & ASSET SELECTION   📋 Review Doc   │
│  Candidate assets · Master allow-list · Continuous updates       │
│  Index members (S&P 500, DAX, Nasdaq...) · Crypto · Commodities ├──┐
│  ← Optional master constraint: "only DAX + S&P 500, no crypto"  │  │
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ active universe (ticker list)        │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART II: NEWS RETRIEVAL                         📋 Review Doc   │  │
│  Financial APIs · Aggregators · AI Search · Social · Regulatory ├──┤
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ raw articles, headlines, filings     │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART III: NEWS EVALUATION                       📋 Review Doc   │  │
│  Deduplication · Relevance scoring · Sentiment · Impact         ├──┤
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ filtered, scored news items          │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART IV: DATA PREPARATION FOR AI                📋 Review Doc   │  │
│  Structured schema · Embeddings · Vector DB · Chunking          ├──┤
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ optimized context documents          │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART V: PORTFOLIO CONTEXT & QUANTITATIVE DATA   📋 Review Doc   │  │
│  Prices · Fundamentals · Technical indicators · Strategy rules  ├──┤
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ complete analysis context            │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART VI: AI-POWERED ANALYSIS & DECISION MAKING  📋 Review Doc   │  │
│  LLM analysis · Prompt engineering · Confidence · Actions       │  │
│  📝 Decision Documentation · Anti-Hallucination Checks          ├──┤
└──────────────────────────────┬───────────────────────────────────┘  │
                               │ documented recommendations           │
                               ▼                                      │
                        ┌──────────────┐                              │
                        │   OUTPUT     │                              │
                        │  Buy / Sell  │                              │
                        │  Hold / Wait │                              │
                        │  Rebalance   │                              │
                        └──────┬───────┘                              │
                               │                                      │
                               ▼                                      │
┌──────────────────────────────────────────────────────────────────┐  │
│  PART VIII: EVALUATION & OPTIMIZATION FRAMEWORK (human-driven)   │  │
│  Experiment tracking · Human/AI review · Backtesting · A/B tests │◄─┘
│  Collects review docs from ALL steps. Human reviews on cadence.  │
│  📝 Decision Audit: reviews hallucination rate & reasoning quality│
└──────────────────────────────┬───────────────────────────────────┘
                               │ accumulated run data + market outcomes
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  PART IX: CONTINUOUS SELF-OPTIMIZATION (autonomous)              │
│  Counterfactual simulation · Staleness detection · Drift alerts  │
│  Shadow mode testing · Automated parameter rollout (guardrailed) │
│                                                                  │
│  Runs continuously. Asks: "What would have happened with         │
│  different parameters?" Proposes + applies changes safely.       │
│  Monitors decision documentation for hallucination trends.       │
└──────────────────────────────┬───────────────────────────────────┘
                               │ parameter adjustments
                               │ (auto-applied within guardrails,
                               │  or escalated for human approval)
                               ▼
                     ┌───────────────────┐
                     │  FEEDBACK LOOP    │
                     │  → Back to Parts  │
                     │    I through VI   │
                     └───────────────────┘
```

Each part is described in detail below. Every part includes an **"Optimization & Review"** subsection that defines the review artifact it produces and the tunable parameters for that step. **Part VII** presents concrete workflows. **Part VIII** describes the human-driven evaluation and optimization framework. **Part IX** adds the autonomous self-optimization layer that continuously evaluates and adjusts the pipeline without waiting for human intervention. **All AI decisions are documented with reasoning, evidence, and anti-hallucination checks** (see Part VI) — these decision records feed into both the evaluation framework (Part VIII) and the self-optimization loop (Part IX).

---

## Part I: Investment Universe & Asset Selection

Before the system can retrieve news, evaluate sentiment, or recommend trades, it must know **which assets to consider**. The investment universe is a dynamic, continuously updated list of candidate assets that defines the scope of the entire pipeline.

### Core Concept

The investment universe serves three purposes:

1. **Scope definition:** Which assets does the system actively monitor and analyze? This list feeds into Part II (which tickers to search for), Part V (which prices and fundamentals to gather), and Part VI (which assets to include in recommendations).
2. **Opportunity identification:** The universe should extend beyond current holdings — it includes assets the system *might* recommend buying. An agent that only monitors what it already holds cannot discover new opportunities.
3. **Constraint enforcement:** An optional master allow-list ensures the system never recommends asset classes or instruments that the investor has excluded (e.g. "no crypto", "only US large-cap").

### Universe Sources & Composition

The universe can be composed from multiple sources:

**Index-based selection:**

| Index / Category | Typical Assets | Notes |
|------------------|----------------|-------|
| **S&P 500** | 500 US large-cap stocks | Broad US market exposure; most liquid |
| **Dow Jones Industrial Average** | 30 blue-chip US stocks | Conservative, well-established companies |
| **Nasdaq 100** | 100 tech-heavy US stocks | Growth/tech oriented |
| **DAX 40** | 40 German large-cap stocks | European/German market exposure |
| **MDAX / SDAX / TecDAX** | German mid/small-cap, tech | Broader German market coverage |
| **EURO STOXX 50** | 50 Eurozone blue chips | Pan-European exposure |
| **FTSE 100** | 100 UK large-cap stocks | UK market exposure |
| **Nikkei 225 / Hang Seng** | Japanese / Hong Kong large-cap | Asian market exposure |

**Alternative asset classes (optional):**

| Asset Class | Examples | Data Sources |
|-------------|----------|-------------|
| **Cryptocurrencies** | BTC, ETH, SOL, top-20 by market cap | CoinGecko API, CoinMarketCap, Binance API |
| **Precious metals** | Gold (XAU), Silver (XAG), Platinum | Alpha Vantage, FMP, commodity APIs |
| **Commodities** | Crude oil (WTI/Brent), Natural Gas | Commodity-specific APIs, futures data |
| **ETFs** | Sector ETFs (XLK, XLF), bond ETFs, commodity ETFs | Same APIs as equities (yfinance, FMP) |
| **REITs** | Real estate investment trusts | Standard equity APIs |

**Custom / thematic lists:**

- Manually curated watchlists (e.g. "AI companies", "green energy", "dividend aristocrats")
- Screener-based lists (e.g. all stocks with P/E < 15 and dividend yield > 3%)
- Sector-specific lists derived from GICS or ICB classifications

### Master Allow-List (Optional Constraint Layer)

The master allow-list is a **human-defined policy** that acts as a hard constraint on the universe. It defines what the system is *permitted* to consider, regardless of what the universe update logic might suggest.

**Examples:**

```json
{
  "master_allow_list": {
    "description": "Conservative European equity strategy",
    "allowed_asset_classes": ["equities"],
    "allowed_indices": ["DAX", "EURO_STOXX_50"],
    "excluded_asset_classes": ["crypto", "commodities", "derivatives"],
    "excluded_sectors": ["gambling", "tobacco"],
    "max_universe_size": 100,
    "min_market_cap_eur": 1000000000,
    "min_avg_daily_volume": 500000
  }
}
```

```json
{
  "master_allow_list": {
    "description": "Aggressive global growth with crypto exposure",
    "allowed_asset_classes": ["equities", "crypto", "etfs"],
    "allowed_indices": ["S&P_500", "NASDAQ_100", "DAX"],
    "allowed_crypto": ["BTC", "ETH", "SOL"],
    "excluded_asset_classes": ["commodities"],
    "max_universe_size": 200,
    "min_market_cap_usd": 500000000
  }
}
```

**The master allow-list is the one element that should NOT be auto-optimized** (see Part IX). It reflects the investor's personal risk tolerance, regulatory constraints, and ethical preferences. Changes require explicit human approval.

### Continuous Universe Updates

The universe is not static. The agent should periodically re-evaluate which assets belong in the universe based on:

**Index rebalancing events:**
- Indices like the S&P 500 and DAX periodically add/remove constituents. The agent should detect these changes and update the universe accordingly.
- Data sources: Index provider announcements, FMP index constituents endpoint, Polygon.io reference data.

**Screening criteria changes:**
- If the universe includes screener-based assets (e.g. "all stocks with market cap > $10B"), the set of qualifying assets changes as market caps fluctuate. Re-run screens periodically (e.g. weekly).

**Emerging opportunities:**
- The agent can use AI-native search APIs to identify emerging sectors or trending assets that might warrant inclusion (e.g. "Which sectors are seeing unusual institutional buying this month?").
- Social sentiment analysis (Part II) may surface assets not currently in the universe that are attracting significant retail attention.

**Removal triggers:**
- Delisting, bankruptcy, or suspension of trading
- Persistent failure to meet minimum liquidity or market cap thresholds
- Sector reclassification that moves the asset outside allowed categories

**Update frequency:**

| Trigger | Frequency | Action |
|---------|-----------|--------|
| Index rebalancing | Quarterly (or on announcement) | Add/remove constituents |
| Screener re-run | Weekly | Refresh qualifying assets |
| Liquidity check | Weekly | Remove illiquid assets |
| Emerging opportunity scan | Bi-weekly | Flag candidates for human review |
| Master allow-list change | On human request only | Re-filter entire universe |

### Universe: Optimization & Review

Each universe update should produce a **Universe Update Log** — a reviewable document that captures what changed and why.

**Review artifact — Universe Update Log:**

```json
{
  "run_id": "2026-02-07-universe-update",
  "timestamp": "2026-02-07T06:00:00Z",
  "universe_size_before": 142,
  "universe_size_after": 145,
  "assets_added": [
    {"ticker": "PLTR", "reason": "Added to S&P 500 index", "source": "index_rebalance"},
    {"ticker": "ARM", "reason": "Passed market cap screen ($150B+)", "source": "weekly_screen"},
    {"ticker": "RHEINMETALL.DE", "reason": "Emerging defense sector interest", "source": "ai_opportunity_scan"}
  ],
  "assets_removed": [
    {"ticker": "LUMN", "reason": "Below minimum market cap threshold", "source": "weekly_screen"}
  ],
  "master_allow_list_violations_blocked": [
    {"ticker": "DOGE", "reason": "Crypto not in allowed_asset_classes", "source": "social_sentiment"}
  ],
  "universe_composition": {
    "equities_us": 95,
    "equities_eu": 40,
    "etfs": 10,
    "total": 145
  }
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Index sources | Which indices to include | `[S&P_500, DAX]` / `[S&P_500, NASDAQ_100, DAX, EURO_STOXX_50]` |
| Screener criteria | Market cap, volume, sector filters | `min_cap: $1B, min_volume: 100K` / `min_cap: $10B` |
| Update frequency | How often to re-evaluate | Daily / weekly / on-event |
| Opportunity scan model | AI model for emerging opportunity detection | `gpt-4o-mini` / `sonar-pro` |
| Max universe size | Hard cap on total assets monitored | 50 / 100 / 200 / 500 |
| Alternative assets | Whether to include crypto, commodities, ETFs | `[equities_only]` / `[equities, etfs, crypto]` |

**Key optimization question:** *"Is the universe comprehensive enough to capture opportunities, but focused enough to keep the pipeline efficient?"* — Track missed opportunities: when an asset outside the universe makes a significant move that the portfolio could have benefited from, assess whether it should have been in the universe. Conversely, if the universe is so large that most assets never generate actionable recommendations, consider tightening the criteria.

---

## Part II: News Retrieval

This part covers **where** and **how** to obtain raw news and information. Sources are categorized by type.

### Specialized Financial APIs

*The "Professionals"* — These sources offer structured data (JSON) linked directly to ticker symbols, making it easy for the agent to assign news to specific stocks.

#### Financial Modeling Prep (FMP)

- **Benefit:** Very developer-friendly. Offers dedicated endpoints for "Stock News", "Press Releases", and even "Sentiment Analysis".
- **Relevance:** High, since news can be filtered directly by ticker (e.g. AAPL, TSLA).

#### Alpha Vantage

- **Benefit:** Provides a "News & Sentiment" endpoint that delivers not only the article but also a relevance score and a sentiment score (Bullish/Bearish) for mentioned tickers.
- **AI-Native:** Launched an official MCP (Model Context Protocol) server in 2025, allowing AI agents to query market data directly without custom integration code.
- **Ideal for:** Pre-filtering before the LLM performs the deep analysis.

#### Polygon.io

- **Benefit:** Very fast and reliable, often used by trading bots. Offers references to news from major publishers. WebSocket support for real-time streaming.

#### Finnhub

- **Benefit:** Generous free tier with real-time market news, company news, press releases, and a dedicated news sentiment endpoint. WebSocket support for streaming data.
- **Ideal for:** Developers who want a low-cost entry point with broad coverage and real-time capabilities.

#### Benzinga

- **Benefit:** Institutional-grade financial news API. Standout feature: "Why Is It Moving" (WIM) — explains price movements with structured metadata. Also offers analyst insights, earnings transcripts, and unusual options activity.
- **Drawback:** Higher price point; primarily focused on North American markets.
- **Ideal for:** Trading systems that need structured, actionable news with context for price movements.

#### EOD Historical Data (EODHD)

- **Benefit:** Strong coverage of international markets (70+ exchanges). Provides financial news, fundamentals, and historical data.
- **Ideal for:** Portfolios with significant international exposure beyond US markets.

#### Yahoo Finance (via yfinance or APIs)

- **Benefit:** Free (via Python library yfinance) or inexpensive via RapidAPI.
- **Drawback:** Often somewhat unstructured and requires more "cleaning" by the agent.

> **Note:** IEX Cloud, formerly a popular developer-friendly API, shut down on August 31, 2024. If you encounter references to it elsewhere, be aware that migration to alternatives is necessary.

---

### News Aggregators & Search Engines

*The "Broad" Sources* — Ideal for capturing macro trends (interest rate decisions, geopolitics, commodity prices) that move the overall market.

#### SerpApi (Google News / Bing News)

- **How it works:** A wrapper for Google Search. Your agent can submit targeted queries such as "Current news about Siemens Energy" or "FED interest rate decision today".
- **Benefit:** Finds extremely current articles from thousands of sources.
- **Integration:** Integrates perfectly as a tool in LangChain (`GoogleSerperAPIWrapper`).

#### NewsAPI.org

- **Benefit:** Scans thousands of international sources (BBC, Reuters, CNN, Spiegel, Handelsblatt). You can filter by keywords, domains, or categories (e.g. "Business").
- **Drawback:** The free version often has a time delay; the Pro version is needed for real-time trading.

#### GNews API

- **Benefit:** A simple and fast API specifically for Google News results.

---

### AI-Native Search APIs

*The "Smart Researchers"* — Purpose-built for AI agents, combining search, extraction, and summarization into a single step. These can dramatically simplify the pipeline by merging retrieval and parts of evaluation.

#### Tavily

- **Benefit:** A search engine designed specifically for AI agents. Provides endpoints for Search, Extract, Crawl, and deep Research. Native LangChain integration via `langchain-tavily` package.
- **Ideal for:** LangChain/LangGraph-based agent architectures where you want a drop-in search tool without building a custom scraping pipeline.
- **Cost:** Free tier available; paid plans for higher usage.

#### Perplexity API (Sonar Models)

- **Benefit:** Online LLMs that perform real-time search, read web pages, and return synthesized answers with citations. Eliminates the need for separate search → scrape → clean → summarize steps. Supports `search_domain_filter` to restrict sources.
- **Cost:** `sonar` at $1/1M tokens; `sonar-pro` for multi-step queries with double citations.

#### Exa.ai

- **Benefit:** Neural search engine with highest accuracy on factuality benchmarks (94.9% SimpleQA). Offers a "Research Pro" mode for deep, multi-source research. Returns structured data with semantic understanding of queries.
- **Ideal for:** Use cases where factual accuracy is paramount (e.g. earnings figures, specific financial data points).

#### YOU.com API

- **Benefit:** Fast (< 500ms for standard queries) and cost-effective. Flexible endpoints offering speed vs. depth tradeoffs. Web-scale search specifically designed for LLM consumption.
- **Ideal for:** High-volume, latency-sensitive use cases where cost matters.

#### Google Gemini with Grounding

- **Benefit:** Gemini models can be grounded in Google Search results, providing real-time information with citations. Starting with Gemini 2.0, the model can autonomously decide when to search.
- **Drawback:** Pricing at $35 per 1,000 grounded queries can be expensive at scale.
- **Ideal for:** Projects already in the Google Cloud ecosystem.

> See the [Appendix: Online Research LLMs — Deep Dive](#appendix-online-research-llms--deep-dive) for a detailed comparison and architecture guidance.

---

### Alternative Data & Social Sentiment

*The "Mood Makers"* — Stocks often move based on rumors or sentiment on social media before official news appears.

#### StockTwits API

- Excellent for capturing retail investor sentiment.

#### Reddit (via API Wrappers)

- Monitoring subreddits such as r/Finanzen, r/Stocks, or r/WallStreetBets.

#### Twitter / X (via API)

- Unfortunately very expensive for API access nowadays, but still the fastest source for breaking news.

---

### Regulatory Filings & Targeted Scraping

*The "Official Sources"* — For the most authentic, unfiltered information directly from regulators and companies.

#### RSS Feeds

- Many sites such as Tagesschau Wirtschaft, Handelsblatt, or Onvista offer RSS feeds. A simple Python script can fetch these every 10 minutes and send new entries to the agent.

#### SEC EDGAR / Company Websites

- For US stocks: Direct connection to the SEC for ad-hoc announcements (8-K filings). These are the "most authentic" news items without journalistic filtering.
- The EDGAR Full-Text Search System (EFTS) allows searching across all filings. Structured XBRL data is also available for programmatic extraction of financial figures.

#### EQS News / DGAP (European Regulatory Filings)

- **For German and European stocks:** EQS News (formerly DGAP — Deutsche Gesellschaft für Ad-hoc-Publizität) is the primary platform for mandatory ad-hoc announcements, regulatory disclosures, and corporate news across DAX, MDAX, TecDAX, SDAX, and smaller segments.
- **This is the European equivalent of SEC EDGAR 8-K filings.** Companies listed on German exchanges are legally required to publish material information here.
- Available at eqs-news.com with filtering by news type (ad-hoc, reports, research) and company watchlists.

---

### Data Latency & Real-Time Considerations

When building a trading-oriented agent, data freshness is critical. Not all sources deliver data at the same speed:

| Latency Tier | Sources | Notes |
|--------------|---------|-------|
| **Real-time** (seconds) | Polygon.io, Finnhub (WebSocket), Benzinga, Bloomberg | WebSocket/streaming connections; best for intraday strategies |
| **Near real-time** (minutes) | Alpha Vantage, FMP, SerpApi, Tavily | REST API polling; suitable for daily rebalancing |
| **Delayed** (15-30 min+) | Yahoo Finance (free tier), NewsAPI (free tier) | Adequate for end-of-day analysis; not suitable for active trading |
| **Batch** (hours) | RSS feeds, SEC EDGAR, EQS News | Manual or scheduled polling; best for overnight analysis |

**Key consideration:** If your strategy requires intraday reactions, prioritize sources with WebSocket or streaming support (Polygon.io, Finnhub, Benzinga). For daily portfolio rebalancing, near real-time REST APIs are sufficient and significantly cheaper.

---

### Retrieval: Optimization & Review

Each pipeline run should produce a **Retrieval Log** — a reviewable document that captures what happened during the retrieval step.

**Review artifact — Retrieval Log:**

```json
{
  "run_id": "2026-02-07-14:30",
  "sources_queried": ["alpha_vantage", "serpapi", "eqs_news"],
  "queries_sent": [
    {"source": "alpha_vantage", "ticker": "NVDA", "articles_returned": 12, "latency_ms": 340},
    {"source": "serpapi", "query": "ECB interest rate decision", "articles_returned": 8, "latency_ms": 520}
  ],
  "total_articles_retrieved": 47,
  "errors": [],
  "coverage_gaps": ["No results for SIE.DE from alpha_vantage — consider adding EODHD as fallback"]
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Source selection | Which APIs to query | `[alpha_vantage, serpapi]` vs. `[fmp, tavily, finnhub]` |
| Polling frequency | How often to fetch new articles | Every 10 min / 30 min / 2 hours |
| Query terms | Keywords and tickers used for search | Ticker-only vs. ticker + sector + competitors |
| Source allowlist | Trusted domains for aggregators | `[reuters.com, bloomberg.com, handelsblatt.com]` |
| Timeout / retry | How long to wait, how many retries | 5s timeout, 2 retries |

**Key optimization question:** *"Did we retrieve all news that turned out to be relevant? Did we miss anything important?"* — Answer this by comparing the retrieval log against post-hoc market movements. If a stock moved significantly and the retrieval step found no related news, there is a coverage gap.

---

## Part III: News Evaluation

Raw news from Part II is noisy — duplicates, irrelevant items, varying quality. This part covers how to **filter, score, and assess** news before it consumes expensive LLM tokens.

### 1. Pre-Filtering (The Gatekeeper)

The first line of defense, applied before any LLM involvement:

- **Deduplication:** Articles from multiple sources often cover the same event. Use similarity hashing (e.g. MinHash / SimHash on headlines) or simple URL deduplication to collapse duplicates.
- **Relevance filtering:** Discard articles that don't mention any portfolio ticker or relevant sector keywords. This can be done with simple string matching or a lightweight classifier.
- **Recency check:** Discard articles older than the analysis window (e.g. older than 24 hours for daily rebalancing).
- **Source quality scoring:** Maintain a configurable allowlist/blocklist of sources. Prioritize Reuters, Bloomberg, official filings over SEO blogs and clickbait.
- **Minimum length filter:** Very short items (< 100 words) are often teasers or ads; filter or flag them.

### 2. Sentiment Analysis

Two approaches, which can be layered:

**API-provided sentiment** (cheap, fast, pre-computed):
- Alpha Vantage delivers a sentiment score (Bullish/Bearish/Neutral) and a relevance score per ticker with each article.
- Finnhub provides a news sentiment endpoint.
- Benzinga's WIM data implicitly encodes sentiment through price-movement context.

**LLM-based sentiment** (more nuanced, more expensive):
- For articles that pass pre-filtering, an LLM can provide richer analysis: degree of sentiment, affected sectors, time horizon (short-term catalyst vs. long-term trend).
- Can be done with a lightweight model (e.g. GPT-4o-mini, Claude Haiku) to keep costs low.

**Recommendation:** Use API-provided sentiment as a first pass. Reserve LLM-based sentiment for high-relevance articles that directly affect portfolio holdings.

### 3. Portfolio-Specific Impact Assessment

Not all "positive news" matters equally. Impact must be assessed relative to the portfolio:

- **Direct impact:** News mentioning a held stock (e.g. "NVIDIA reports record earnings") → high relevance.
- **Sector impact:** News affecting an entire sector (e.g. "EU tightens chip export controls") → medium relevance for all semiconductor holdings.
- **Macro impact:** Central bank decisions, geopolitical events, commodity price swings → assessed against portfolio exposure (e.g. a rate hike affects high-growth tech more than defensive utilities).
- **Correlation-based impact:** News about a company not in the portfolio but highly correlated to a holding (e.g. AMD earnings affecting NVIDIA sentiment).

This assessment is ideally performed by the LLM in Part VI, but a lightweight pre-scorer can prioritize which articles get expensive analysis first.

### 4. Noise Reduction Strategies

- **Time-windowed batching:** Instead of analyzing every article as it arrives, batch articles into time windows (e.g. every 30 minutes or every 2 hours). This naturally deduplicates and allows the agent to see the "full picture" for a given period.
- **Event clustering:** Group articles about the same event (e.g. 15 articles about an FDA approval). Present the cluster as a single event with the best source, rather than 15 separate analyses.
- **Confidence thresholds:** Only escalate news to LLM analysis if the pre-filter relevance score exceeds a configurable threshold.

### Evaluation: Optimization & Review

Each pipeline run should produce an **Evaluation Report** — showing exactly what was kept, what was filtered, and why.

**Review artifact — Evaluation Report:**

```json
{
  "run_id": "2026-02-07-14:30",
  "input_articles": 47,
  "after_dedup": 31,
  "after_relevance_filter": 18,
  "after_recency_filter": 16,
  "after_quality_filter": 14,
  "final_articles_passed": 14,
  "filtered_articles": [
    {"headline": "10 Best Stocks to Buy Now", "reason": "source_quality_blocklist", "source": "seo-blog.com"},
    {"headline": "NVIDIA Q4 Results (duplicate)", "reason": "dedup_simhash", "similar_to": "article-id-003"}
  ],
  "sentiment_distribution": {"Bullish": 6, "Neutral": 5, "Bearish": 3},
  "highest_relevance": {"headline": "NVIDIA Reports Record Q4 Revenue", "score": 0.95},
  "lowest_passed": {"headline": "Semiconductor Sector Overview", "score": 0.61}
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Relevance threshold | Minimum score to pass filtering | 0.5 / 0.6 / 0.7 |
| Dedup sensitivity | SimHash similarity threshold | 0.8 (lenient) / 0.9 (strict) |
| Recency window | Max article age | 6h / 12h / 24h |
| Min article length | Minimum word count | 50 / 100 / 200 words |
| Sentiment model | API-provided vs. LLM | `alpha_vantage` / `gpt-4o-mini` |
| Batch window | Time-windowed grouping | 30 min / 2h / 4h |

**Key optimization question:** *"Was the filter too aggressive (missed important articles) or too lenient (wasted LLM tokens on noise)?"* — Review the `filtered_articles` list after each run. If a filtered article later proved relevant (market moved on that news), lower the threshold. If too many low-quality articles pass through, raise it.

---

## Part IV: Data Preparation for AI

Before news data reaches the LLM for analysis, it must be transformed into a format that maximizes AI effectiveness while minimizing token costs.

### 1. Structured News Schema

Define a consistent JSON schema for all news items, regardless of source. This normalizes heterogeneous data into a unified format:

```json
{
  "id": "uuid-or-hash",
  "source": "alpha_vantage",
  "published_at": "2026-02-07T14:30:00Z",
  "retrieved_at": "2026-02-07T14:32:15Z",
  "headline": "NVIDIA Reports Record Q4 Revenue",
  "summary": "NVIDIA announced Q4 revenue of $22.1B, beating estimates...",
  "full_text": "...",
  "url": "https://...",
  "tickers": ["NVDA"],
  "sectors": ["Technology", "Semiconductors"],
  "sentiment": {
    "score": 0.85,
    "label": "Bullish",
    "source": "alpha_vantage"
  },
  "relevance_score": 0.92,
  "event_cluster_id": "nvidia-q4-earnings-2026"
}
```

### 2. Text Cleaning & Normalization

Raw article text often contains noise that wastes tokens:

- **Strip boilerplate:** Remove cookie notices, navigation text, ads, "Related articles" sections.
- **Normalize encoding:** Consistent UTF-8, resolve HTML entities.
- **Extractive summarization:** For long articles (> 500 words), extract the most relevant paragraphs before embedding or LLM analysis. This can be done with a lightweight model or heuristics (first 2 paragraphs + any paragraph mentioning portfolio tickers).
- **Metadata enrichment:** Add ticker tags, sector tags, and source-quality labels during cleaning.

### 3. Vector Databases & Embeddings

For agents that need to reason over historical news or find similar past events, a vector database is essential:

**Why vector storage?**
- Enables semantic search: "Find past news similar to this FDA approval pattern"
- Supports RAG (Retrieval-Augmented Generation): The LLM retrieves relevant past context to improve analysis
- Allows trend detection: "Has this company been in the news increasingly over the past week?"

**Embedding models:**
- **OpenAI `text-embedding-3-small` / `text-embedding-3-large`:** Good general-purpose embeddings. Small variant is cost-effective for high-volume news.
- **Cohere `embed-v3`:** Strong multilingual support, useful for German/English mixed portfolios.
- **Open-source (e.g. `all-MiniLM-L6-v2` via sentence-transformers):** Free, runs locally, good for prototyping.

**Vector database options:**

| Database | Type | Best For |
|----------|------|----------|
| **ChromaDB** | Embedded (local) | Prototyping, small datasets |
| **Pinecone** | Cloud-managed | Production, fully managed, low ops |
| **Weaviate** | Self-hosted or cloud | Hybrid search (vector + keyword) |
| **Qdrant** | Self-hosted or cloud | High performance, rich filtering |
| **pgvector** | PostgreSQL extension | If you already use PostgreSQL |

**Recommended approach:** Start with ChromaDB for prototyping. Migrate to Pinecone or Qdrant for production. Embed the `headline + summary` (not full text) to keep embedding costs low and retrieval precise.

### 4. Document Chunking Strategies

When full articles are stored for RAG retrieval, chunking strategy matters:

- **By paragraph:** Natural boundaries, preserves context. Best for news articles.
- **Fixed-size with overlap:** 500 tokens per chunk, 50-token overlap. Predictable but can split sentences.
- **Semantic chunking:** Split based on topic shifts. More sophisticated, better retrieval quality.

**For financial news specifically:** Paragraph-based chunking usually works best because news articles are already structured with one key point per paragraph.

### 5. Caching & Incremental Updates

Avoid re-processing data that hasn't changed:

- **Article-level deduplication cache:** Store article hashes to skip already-processed items.
- **Embedding cache:** Don't re-embed articles already in the vector DB. Check by `id` before embedding.
- **TTL (Time-to-Live):** Expire old news from the vector DB based on your strategy's time horizon (e.g. 7 days for swing trading, 30 days for position trading).
- **Incremental retrieval:** Use "since" timestamps when polling APIs (most financial APIs support `from_date` parameters) to only fetch new articles.

### Preparation: Optimization & Review

Each pipeline run should produce a **Preparation Report** — documenting how data was transformed and stored.

**Review artifact — Preparation Report:**

```json
{
  "run_id": "2026-02-07-14:30",
  "articles_processed": 14,
  "articles_embedded": 11,
  "articles_skipped_cached": 3,
  "embedding_model": "text-embedding-3-small",
  "avg_chunk_size_tokens": 185,
  "chunks_created": 28,
  "vector_db_total_entries": 1243,
  "ttl_expired_entries": 17,
  "rag_retrieval_test": {
    "query": "NVIDIA earnings impact on semiconductor sector",
    "top_3_results": ["article-003", "article-127", "article-089"],
    "relevance_assessment": "2/3 highly relevant, 1/3 tangentially related"
  }
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Embedding model | Which model to use | `text-embedding-3-small` / `embed-v3` / `all-MiniLM-L6-v2` |
| Fields embedded | Which article fields to embed | `headline + summary` / `full_text` / `headline only` |
| Chunk strategy | How to split long articles | Paragraph / fixed-500-token / semantic |
| Chunk overlap | Overlap between chunks | 0 / 50 / 100 tokens |
| TTL | Expiration of old entries | 7d / 14d / 30d |
| Vector DB | Storage backend | ChromaDB / Pinecone / Qdrant |

**Key optimization question:** *"When the LLM retrieves context via RAG, does it get the most relevant documents?"* — Run periodic retrieval tests: for known important articles, check whether RAG retrieval finds them. If recall is poor, experiment with different embedding models, chunk sizes, or embedded fields.

---

## Part V: Portfolio Context & Quantitative Data

News alone is insufficient for portfolio optimization. The AI needs the full picture of the portfolio and current market state.

### Current Holdings & Strategy

The agent must know:

- **Holdings:** Ticker, quantity, average cost basis, current weight in portfolio.
- **Strategy type:** Conservative income, balanced growth, aggressive growth, sector-specific, etc. This governs how the agent interprets news (e.g. an aggressive strategy might see a dip as a buying opportunity; a conservative one as a warning).
- **Risk constraints:** Maximum position size, sector concentration limits, stop-loss levels, cash reserve requirements.
- **Investment horizon:** Day trading, swing trading (days–weeks), position trading (months), long-term (years). This determines which news is actionable.

### Price & Market Data

- **Current prices:** Real-time or delayed quotes via yfinance (free), Alpha Vantage, Polygon.io, or Finnhub.
- **Historical prices:** For trend analysis, support/resistance levels, and technical indicators.
- **Market indices:** DAX, S&P 500, NASDAQ — for benchmarking and macro context.

### Fundamental Data

- **Earnings data:** EPS, revenue, margins — via FMP, Alpha Vantage, or EODHD.
- **Valuation metrics:** P/E ratio, P/B ratio, PEG, dividend yield.
- **Analyst estimates:** Consensus price targets, recommendation distributions.
- **Useful for:** Contextualizing news (e.g. "revenue missed estimates by 5%" is more meaningful when the agent knows the actual estimate).

### Technical Indicators

Consider providing pre-computed indicators alongside news:

- Moving averages (SMA/EMA 20, 50, 200)
- RSI (Relative Strength Index)
- MACD
- Volume anomalies

Libraries like `ta` (Python) or `pandas-ta` can compute these from historical price data. These give the LLM a quantitative anchor alongside qualitative news.

### Context: Optimization & Review

Each pipeline run should produce a **Context Snapshot** — a complete record of what data was provided to the analysis LLM.

**Review artifact — Context Snapshot:**

```json
{
  "run_id": "2026-02-07-14:30",
  "portfolio_snapshot": {
    "holdings": ["MSFT", "NVDA", "SIE.DE"],
    "total_value": 125000,
    "cash_position": 15000,
    "strategy": "Aggressive Growth"
  },
  "price_data_provided": {
    "NVDA": {"current": 745.20, "sma_50": 710.35, "rsi_14": 68.2},
    "MSFT": {"current": 392.10, "sma_50": 385.00, "rsi_14": 55.1}
  },
  "fundamentals_provided": ["P/E", "EPS_estimate", "next_earnings_date"],
  "indicators_provided": ["SMA_50", "SMA_200", "RSI_14", "MACD"],
  "news_items_included": 14,
  "total_context_tokens": 4850,
  "context_window_utilization": "38%"
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Indicators included | Which technical indicators | `[SMA_50, RSI]` / `[SMA_50, SMA_200, RSI, MACD, Volume]` |
| Lookback period | Historical data depth | 30 / 60 / 90 / 200 days |
| Fundamental fields | Which financials to include | Minimal (P/E only) / Full (P/E, PEG, margins, estimates) |
| Price data freshness | Real-time vs. delayed | Real-time / 15-min delayed / closing prices |
| Context budget | Max tokens allocated to context | 3000 / 5000 / 10000 tokens |

**Key optimization question:** *"Did the LLM have all the information it needed to make a good recommendation? Was anything missing that would have changed the outcome?"* — When a recommendation turns out poorly, review the context snapshot: was a critical piece of data absent (e.g. earnings date was tomorrow, but the agent didn't know)?

---

## Part VI: AI-Powered Analysis & Decision Making

This is the core of the system — where prepared data is synthesized into actionable portfolio recommendations.

### Model Selection

| Model | Strengths | Cost | Best For |
|-------|-----------|------|----------|
| **GPT-4o** | Strong reasoning, reliable instruction following | Medium | Primary analysis agent |
| **Claude 4 (Opus/Sonnet)** | Excellent at nuanced text analysis, long context | Medium–High | Complex multi-article synthesis |
| **Gemini 2** | Large context window, multimodal | Medium | Processing many articles at once |
| **GPT-4o-mini / Claude Haiku** | Fast, cheap | Low | Pre-filtering, sentiment scoring |
| **Online Research LLMs** (Perplexity Sonar, Exa, YOU.com, Gemini Grounding) | Built-in web search | Low–Medium | Research agent (retrieval + summary) |

**Recommendation:** Use a lightweight model for high-volume pre-filtering (Part III), and a capable model for the final portfolio analysis.

### Prompt Engineering

The analysis prompt should include:

1. **Portfolio context:** Current holdings, strategy, constraints (from Part V)
2. **Prepared news:** Filtered, scored, summarized news items (from Parts II–IV)
3. **Quantitative data:** Key price levels, recent performance, relevant indicators (from Part V)
4. **Explicit output format:** Structured JSON for reliable downstream processing

**Example analysis prompt:**

```
You are a portfolio analyst. Analyze the following news in the context of my portfolio.

PORTFOLIO:
- MSFT: 50 shares @ $380 avg (12% of portfolio)
- NVDA: 30 shares @ $720 avg (18% of portfolio)
- SIE.DE: 100 shares @ €165 avg (15% of portfolio)
Strategy: Aggressive Growth | Horizon: 3-6 months | Max position: 25%

TODAY'S NEWS (pre-filtered, high-relevance):
[... prepared news items ...]

MARKET DATA:
[... current prices, key indicators ...]

For each holding affected by today's news, provide:
1. Impact assessment (Positive / Negative / Neutral)
2. Magnitude (Low / Medium / High)
3. Time horizon (Immediate / Short-term / Long-term)
4. Recommended action (Buy more / Hold / Trim / Sell / No action)
5. Confidence level (0.0 - 1.0)
6. Reasoning (2-3 sentences)

Respond in JSON format.
```

### Output Format & Confidence Scoring

Structure the LLM output as JSON for reliable programmatic processing:

```json
{
  "analysis_date": "2026-02-07",
  "market_summary": "Tech sector rallied on strong earnings...",
  "recommendations": [
    {
      "ticker": "NVDA",
      "impact": "Positive",
      "magnitude": "High",
      "time_horizon": "Short-term",
      "action": "Hold",
      "confidence": 0.85,
      "reasoning": "Record Q4 earnings beat estimates. Strong guidance for next quarter. Current position already at 18%, near max allocation — hold rather than add."
    }
  ],
  "portfolio_level": {
    "overall_sentiment": "Bullish",
    "rebalancing_needed": false,
    "risk_flags": []
  }
}
```

### Guardrails

- **Never auto-execute trades** without human review (at least in early iterations).
- **Confidence thresholds:** Only surface recommendations above a minimum confidence (e.g. > 0.6).
- **Contradiction detection:** If multiple news items for the same ticker conflict, flag for human review rather than choosing one.
- **Hallucination checks:** Cross-reference LLM-cited numbers (earnings, percentages) against quantitative API data from Part V.

### Decision Documentation & Anti-Hallucination

**Every AI-generated decision must be documented, traceable, and verifiable.** This is not just good practice — it is the foundation for the evaluation framework (Part VIII) and the self-optimization loop (Part IX). Undocumented decisions cannot be audited, and hallucination-based decisions cannot be detected retroactively.

#### Decision Record Schema

Every recommendation produced by the analysis LLM must include a structured decision record:

```json
{
  "decision_id": "dec-2026-02-07-14:30-NVDA",
  "run_id": "2026-02-07-14:30",
  "ticker": "NVDA",
  "action": "Hold",
  "confidence": 0.85,
  "reasoning": {
    "summary": "Record Q4 earnings beat estimates. Strong guidance. Position near max allocation.",
    "evidence_sources": [
      {"type": "news", "id": "article-003", "headline": "NVIDIA Reports Record Q4 Revenue", "source": "reuters.com"},
      {"type": "news", "id": "article-007", "headline": "NVIDIA Guidance Exceeds Expectations", "source": "bloomberg.com"},
      {"type": "quantitative", "field": "current_position_pct", "value": 18.2, "source": "portfolio_context"}
    ],
    "key_factors": [
      {"factor": "Earnings beat", "direction": "positive", "weight": "high"},
      {"factor": "Position size near limit", "direction": "constraining", "weight": "high"},
      {"factor": "RSI at 68.2 (approaching overbought)", "direction": "cautionary", "weight": "medium"}
    ]
  },
  "hallucination_check": {
    "claims_verified": [
      {"claim": "Q4 revenue of $22.1B", "verified_against": "fmp_earnings_api", "match": true},
      {"claim": "Beat estimates", "verified_against": "alpha_vantage_estimates", "match": true}
    ],
    "claims_unverifiable": [],
    "claims_failed": [],
    "hallucination_risk": "low"
  },
  "alternative_actions_considered": [
    {"action": "Buy more", "rejected_because": "Position already at 18.2%, max is 25%. Risk of over-concentration."},
    {"action": "Sell", "rejected_because": "Strong positive earnings with forward guidance. No negative catalysts."}
  ]
}
```

#### Anti-Hallucination Framework

LLMs can confidently state incorrect financial figures — a dangerous failure mode in portfolio optimization. The system must systematically detect and flag hallucinations.

**Verification layers:**

1. **Automated fact-checking:** After each analysis, extract all quantitative claims (earnings figures, percentages, price levels, dates) and cross-reference against the structured data from Part V (prices, fundamentals, analyst estimates). Flag any mismatches.

2. **Source attribution verification:** Every claim in the reasoning must trace back to a specific news article (from Parts II–IV) or quantitative data point (from Part V). If the LLM cites information not present in its input context, flag it as a potential hallucination.

3. **Consistency checks:** Compare the LLM's stated reasoning against its recommended action. If the reasoning describes negative news but the action is "Buy," flag the inconsistency.

4. **Temporal coherence:** Ensure the LLM is not confusing current data with historical data (e.g. citing last quarter's earnings as this quarter's).

5. **Cross-model validation (optional):** For high-stakes decisions (large position changes, confidence > 0.9), run the same analysis through a second LLM and compare. Significant divergence warrants human review.

**Hallucination severity levels:**

| Level | Description | Action |
|-------|-------------|--------|
| **None** | All claims verified | Proceed normally |
| **Low** | Minor unverifiable claims (opinions, qualitative assessments) | Log and proceed |
| **Medium** | Quantitative claim mismatch (e.g. wrong percentage) | Flag for review, reduce confidence by 0.1 |
| **High** | Material factual error (wrong earnings, wrong direction of movement) | Block recommendation, escalate to human review |
| **Critical** | Reasoning contradicts recommended action | Block recommendation, log as pipeline failure |

**Decision documentation feeds into optimization:**

- **Part VIII (Evaluation):** Decision records are reviewed during the human review cadence. Track hallucination rates over time. A rising hallucination rate may indicate model degradation or inadequate context.
- **Part IX (Self-Optimization):** The counterfactual engine can test whether decisions with higher hallucination risk correlated with worse outcomes. Parameter changes that reduce hallucination rates can be detected and promoted automatically.

### Analysis: Optimization & Review

This is the most critical review point — the final output of the pipeline. Each run should produce an **Analysis Log** that captures the full LLM interaction.

**Review artifact — Analysis Log:**

```json
{
  "run_id": "2026-02-07-14:30",
  "model": "gpt-4o",
  "temperature": 0.2,
  "prompt_tokens": 4850,
  "completion_tokens": 1200,
  "latency_ms": 3400,
  "cost_usd": 0.042,
  "prompt_template_version": "v2.3",
  "full_prompt": "[...complete prompt sent to LLM...]",
  "full_response": "[...complete LLM response...]",
  "recommendations": [
    {
      "ticker": "NVDA",
      "action": "Hold",
      "confidence": 0.85,
      "reasoning": "Record Q4 earnings beat estimates..."
    }
  ],
  "market_outcome_7d": {
    "NVDA": {"recommended": "Hold", "actual_move": "+4.2%", "outcome": "Correct"}
  }
}
```

**Tunable parameters:**

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| Model | Which LLM for final analysis | `gpt-4o` / `claude-4-sonnet` / `gemini-2` |
| Temperature | LLM creativity vs. consistency | 0.0 / 0.2 / 0.5 |
| Prompt template | Structure and wording of prompt | v1.0 / v2.3 / v3.0-experimental |
| Confidence threshold | Minimum to surface recommendation | 0.5 / 0.6 / 0.7 |
| Output schema | JSON structure of response | Minimal / Detailed / With-alternatives |
| Max tokens | Response length limit | 1000 / 2000 / 4000 |

**Key optimization question:** *"Were the recommendations correct? Was the reasoning sound?"* — The `market_outcome_7d` field (filled in retrospectively) is the ground truth. Over time, track the hit rate: what percentage of recommendations aligned with actual market movements? When the LLM was wrong, review the full prompt and reasoning to understand where the analysis failed.

---

## Part VII: Possible Workflows

The parts above can be assembled into different end-to-end workflows depending on complexity, budget, and real-time requirements. The workflows below are ordered from simplest (A) to most sophisticated (E).

### Workflow A: One-Shot LLM (Zero Infrastructure)

The absolute simplest approach. Send a single prompt to a powerful LLM that has built-in web search capabilities and let it handle everything — research, analysis, and recommendations — in one API call. No pipeline, no agent framework, no vector database, no infrastructure at all.

This workflow is ideal as a **starting point for prompt crafting**: begin with a very small asset list (e.g., 3–5 stocks), iterate on the prompt, and observe what the model does well and where it falls short. Those observations inform which of the more structured workflows (B–E) to adopt later.

```
┌───────────────────────────────────────────────────────────────┐
│  PROMPT (the only input)                                      │
│                                                               │
│  "You are a portfolio advisor. I hold the following assets:   │
│   MSFT (12%), NVDA (8%), JNJ (6%), cash 18%.                 │
│   My goal is long-term growth with moderate risk.             │
│   I only consider S&P 500 stocks.                             │
│                                                               │
│   Research the latest financial news for my holdings.         │
│   Also check if there are better opportunities in the         │
│   S&P 500 that I should consider.                             │
│                                                               │
│   For each holding and each new candidate, tell me:           │
│   - What to do (buy / sell / hold) and why                    │
│   - What news or data you based this on (with sources)        │
│   - Your confidence level (low / medium / high)               │
│   - Any risks I should be aware of"                           │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│  SEARCH-ENABLED LLM (single API call)                         │
│                                                               │
│  The model internally:                                        │
│   • Searches the web for recent news on each ticker           │
│   • Looks up general market conditions                        │
│   • Reasons about the portfolio in light of findings          │
│   • Formulates recommendations                                │
│                                                               │
│  Suitable models:                                             │
│   • Perplexity Sonar Pro (best for web research, cites        │
│     sources, domain filtering)                                │
│   • GPT-4o with browsing (strong reasoning + search)          │
│   • Gemini with Google Grounding (Google Search quality,      │
│     large context window)                                     │
│   • Claude with web search (strong reasoning)                 │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│  RESPONSE (plain text or lightly structured)                  │
│                                                               │
│  Recommendations + reasoning + sources, as returned by the    │
│  model. No guaranteed schema — format depends on the prompt   │
│  and the model's interpretation.                              │
└───────────────────────────────────────────────────────────────┘
```

**What works well:**
- Qualitative research — the model searches for and summarizes recent news effectively.
- General market sentiment assessment.
- Small portfolios (5–15 positions) where a weekly sanity check is sufficient.
- Prompt iteration — fast feedback loop for refining what you ask and how you ask it.

**What does NOT work well:**
- **Numerical precision** — the model may report approximate or stale prices ("NVDA trades around $850") rather than exact current values. It cannot reliably fetch real-time prices.
- **Portfolio state** — you must paste your current holdings into every prompt manually. There is no programmatic broker integration.
- **Statelessness** — each call starts from zero. The model does not know what it recommended last time, whether you acted on it, or what happened since.
- **Reproducibility** — the same prompt may produce different recommendations on different runs due to different web search results and model temperature.
- **Source verification** — you cannot programmatically confirm that the model actually searched for an article vs. used training data.
- **No structured output** — the response format is not guaranteed. You may get JSON one time and prose the next.
- **No feedback loop** — there is no systematic evaluation, no counterfactual analysis, no self-optimization. You improve the prompt manually based on gut feel.

**Pros:** Zero infrastructure, zero code, zero cost beyond the API call. Can be done today in 5 minutes. Excellent for learning what a good prompt looks like and what information the model needs.
**Cons:** No auditability, no reproducibility, no systematic improvement, no precise data. Quality ceiling is the model's own reasoning and web search capability.
**Best for:** Day-one prototyping, prompt crafting, validating the concept before investing in infrastructure. Also useful as a permanent lightweight "second opinion" alongside more structured workflows.

**Natural evolution path:**

The one-shot approach is step 1 of a natural progression:

| Step | Workflow | What you add | Why |
|---|---|---|---|
| 1 | **A (One-Shot)** | Nothing — just a prompt and an API call | Validate the concept, learn prompt crafting |
| 2 | **B (Research API-First)** | Separate research from analysis; add quantitative data (yfinance/FMP) | You discover the model uses stale prices or misses key data |
| 3 | **E Level 1 (Simple Mandate)** | Mandate document + simple agent using B's tools | You want to validate the mandate-driven concept early, before building more infrastructure |
| 4 | **C (Classic Pipeline)** | Full pipeline with explicit modules per step | You need source transparency, structured dedup, and vector DB |
| 5 | **D (Multi-Agent)** | Specialized agents (research, data, sentiment, analyst, risk) | Complexity demands separation of concerns and parallel execution |
| 6 | **E Level 2 (Full Mandate)** | Full agent with D's multi-agent internals + LangSmith tracing | You want mandate-driven simplicity with production-grade internals |

Each step builds on the components of the previous one. Steps 3 and 4–5 can also be pursued in parallel — E Level 1 and the pipeline path (C→D) are independent tracks that converge at E Level 2.

### Workflow B: Research API-First (Simplified Pipeline)

Delegates the retrieval and initial summarization to an **online research LLM** (such as Perplexity Sonar, Exa.ai, YOU.com, or Gemini with Grounding), dramatically reducing pipeline complexity. This is the natural next step after Workflow A — you add programmatic data fetching and separate research from analysis, while keeping the overall architecture simple.

```
Investment Universe (Part I)
  + Master allow-list
       │
       ▼
Active tickers + Portfolio holdings
       │
       ▼
┌──────────────────────────────────┐
│  Online Research LLM API         │
│  (Perplexity / Exa / YOU.com /  │
│   Gemini Grounding / Tavily)    │
│  "Research the latest news for   │
│   MSFT, NVDA, SIE.DE today..."  │
│  → Synthesized summary + sources │
└────────────────┬─────────────────┘
                 │ cleaned, cited summaries
                 ▼
      LLM Analysis (GPT-4o / Claude 4)
       + Portfolio context
       + Quantitative data (FMP/yfinance)
       + Decision documentation
                 │
                 ▼
      Documented Recommendations
```

**Pros:** Minimal code, no scraping, no cleaning — the research API handles dedup and noise.
**Cons:** Less control over sources (some APIs offer domain filters to mitigate), black-box retrieval, potential hallucinations with specific numbers.
**Best for:** Rapid prototyping, personal projects, when speed-to-market matters more than source transparency.

**Components built in this step (reused by later workflows):**
- Research API wrapper (Perplexity / Tavily / Exa)
- Portfolio context module (yfinance / FMP for prices, fundamentals)
- LLM analysis call with structured output schema
- Decision documentation generation
- Basic output schema (JSON recommendations)

**Example using Perplexity** (similar OpenAI-compatible patterns apply to other providers):

```python
import os
from datetime import datetime
from openai import OpenAI

PERPLEXITY_API_KEY = os.environ["PERPLEXITY_API_KEY"]

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"
)

def get_market_news(tickers: list[str]) -> str:
    today = datetime.now().strftime("%B %d, %Y")
    ticker_str = ", ".join(tickers)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional financial researcher. "
                "Your task is to find current, market-relevant news accurately. "
                "Be factual and objective. Cite your sources."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Search for the most important financial news and analyst opinions "
                f"for {ticker_str} from today, {today}. Also include relevant macro news "
                f"(central bank decisions, sector developments). "
                f"Ignore irrelevant brief news. Summarize events and cite sources."
            ),
        },
    ]

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
        max_tokens=2000,
    )

    return response.choices[0].message.content

# Example
news = get_market_news(["MSFT", "NVDA", "SIE.DE"])
print(news)
```

> **Perplexity model pricing (as of early 2025):** `sonar` costs $1 per 1M input/output tokens (128K context) for lightweight Q&A. `sonar-pro` handles multi-step queries with double the citations and a larger context window. `sonar-reasoning-pro` is available for complex analytical tasks. The API also supports `search_domain_filter` to restrict results to trusted financial sources.

**Choosing a research API for Workflow B:**

| Provider | Strengths | Best For |
|----------|-----------|----------|
| **Perplexity Sonar** | Excellent recency, domain filtering, OpenAI-compatible API | General financial news research |
| **Exa.ai Research Pro** | Highest factual accuracy (94.9%), semantic search | Accuracy-critical analysis (earnings, figures) |
| **YOU.com** | Fastest (< 500ms), most cost-effective | High-frequency, budget-conscious pipelines |
| **Tavily** | Native LangChain integration, Search + Extract + Crawl | LangGraph-based agent architectures |
| **Google Gemini + Grounding** | Google Search quality, multi-turn reasoning | Google Cloud-native projects |

All providers share the same core tradeoff: simplified pipeline at the cost of reduced source control. Evaluate based on your priorities (accuracy, cost, latency, integration).

### Workflow C: Classic Pipeline

The full pipeline approach. Each step is a discrete, independently testable module. This builds on Workflow B by adding explicit control over retrieval, filtering, embedding, and vector storage — addressing B's limitations around source transparency and data precision.

```
Investment Universe (Part I)
  + Master allow-list
       │
       ▼
Active tickers + Portfolio holdings
       │
       ▼
┌──────────────────┐   ┌──────────────────┐
│  FMP / Alpha     │   │  SerpApi / Tavily │
│  Vantage         │   │  (macro news)     │
│  (ticker news)   │   │                   │
└────────┬─────────┘   └────────┬──────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
           Pre-filter & Dedup
                    │
                    ▼
          Embed → Vector DB
                    │
                    ▼
         LLM Analysis (GPT-4o)
          + Portfolio context
          + Quantitative data
          + Decision documentation
                    │
                    ▼
      Documented Recommendations
```

**Pros:** Full control over each step, easy to debug, sources are transparent.
**Cons:** More code to maintain, multiple API keys, complex error handling.
**Best for:** Production systems where reliability and auditability matter.

**Components added in this step (on top of Workflow B):**
- Explicit news retrieval modules (FMP, Alpha Vantage, SerpApi, RSS feeds)
- Pre-filtering and deduplication pipeline
- Embedding pipeline (OpenAI / Cohere / sentence-transformers)
- Vector database (ChromaDB / Pinecone / Qdrant)
- Document chunking and context management

**Components reused from Workflow B:**
- Portfolio context module (yfinance / FMP)
- LLM analysis call with structured output schema
- Decision documentation generation
- Output schema

### Workflow D: Multi-Agent Architecture (LangGraph)

The most sophisticated approach. Multiple specialized agents collaborate, orchestrated by LangGraph.

```
                    ┌─────────────────────┐
                    │   Orchestrator      │
                    │   (LangGraph)       │
                    └──┬──────┬──────┬────┘
                       │      │      │
            ┌──────────┘      │      └──────────┐
            ▼                 ▼                  ▼
   ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐
   │ Research Agent   │ │ Data Agent   │ │ Sentiment     │
   │ (Research LLM / │ │ (FMP /       │ │ Agent         │
   │  Tavily)        │ │  yfinance)   │ │ (StockTwits / │
   │                 │ │              │ │  Reddit)      │
   └────────┬────────┘ └──────┬───────┘ └───────┬───────┘
            │                 │                  │
            └────────┬────────┘──────────────────┘
                     ▼
            ┌─────────────────┐
            │ Analyst Agent   │
            │ (GPT-4o /       │
            │  Claude 4)      │
            │ + Vector DB     │
            │ + Portfolio ctx │
            └────────┬────────┘
                     ▼
            ┌─────────────────┐
            │ Risk Agent      │
            │ (validates      │
            │  recommendations│
            │  against rules) │
            └────────┬────────┘
                     ▼
              Recommendations
```

**Agents:**

1. **Research Agent:** Gathers qualitative news (online research LLM, Tavily, or traditional APIs).
2. **Data Agent:** Gathers quantitative data (prices, fundamentals, technical indicators).
3. **Sentiment Agent:** Monitors social media and alternative data sources.
4. **Analyst Agent:** Synthesizes all inputs, performs portfolio-specific analysis, generates recommendations.
5. **Risk Agent:** Validates recommendations against portfolio constraints (max position size, sector limits, stop-losses). Rejects or modifies recommendations that violate rules.

**Pros:** Separation of concerns, each agent is independently testable, agents can run in parallel, easily extensible.
**Cons:** Complex to build and debug, higher total token cost, requires LangGraph expertise.
**Best for:** Serious production systems with complex strategies and multiple data streams.

### Workflow E: Mandate-Driven Autonomous Agent

The most agentic approach. Instead of prescribing a multi-step pipeline, you provide a single **mandate document** (comparable to an Investment Policy Statement in traditional asset management) and let an autonomous agent handle all research, analysis, and decision-making internally. The pipeline collapses to: **one input → one agent → structured output.**

```
┌─────────────────────────────────────────────────────────────────┐
│  MANDATE DOCUMENT (the single input)                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. Investment Goals                                       │  │
│  │    - Target: long-term growth, 8-12% annual return        │  │
│  │    - Risk tolerance: moderate                             │  │
│  │    - Investment horizon: 5+ years                         │  │
│  │                                                           │  │
│  │ 2. Investment Universe & Constraints                      │  │
│  │    - Allowed: S&P 500, DAX 40, Nasdaq 100                │  │
│  │    - Excluded: crypto, penny stocks, leveraged ETFs       │  │
│  │    - Max single position: 15%                             │  │
│  │    - Sector cap: 30%                                      │  │
│  │                                                           │  │
│  │ 3. Current Portfolio State                                │  │
│  │    - Holdings: { MSFT: 12%, NVDA: 8%, ... }              │  │
│  │    - Cash: €15,000 (18% of portfolio)                     │  │
│  │    - Total value: €83,000                                 │  │
│  │                                                           │  │
│  │ 4. Decision Guidelines & Hints                            │  │
│  │    - Prefer quality over momentum                         │  │
│  │    - Avoid concentration in single sector                 │  │
│  │    - Consider upcoming earnings dates                     │  │
│  │    - Rebalance if any position drifts >5% from target     │  │
│  │                                                           │  │
│  │ 5. Research & Reporting Requirements                      │  │
│  │    - Must cite sources for all factual claims             │  │
│  │    - Must explain reasoning for every recommendation      │  │
│  │    - Flag low-confidence decisions explicitly              │  │
│  │    - Include macro/sector context in analysis             │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│  AUTONOMOUS AGENT                                             │
│                                                               │
│  The agent decides HOW to fulfill the mandate.                │
│  Internally, it may:                                          │
│   • Search for news (Perplexity, Tavily, web search)         │
│   • Fetch prices and fundamentals (yfinance, FMP)            │
│   • Check technical indicators                                │
│   • Query vector DB for historical context                    │
│   • Reason about portfolio allocation                         │
│   • Cross-check claims against data sources                   │
│                                                               │
│  The caller does NOT prescribe the internal steps.            │
│  The agent has tool access and autonomy to research as        │
│  it sees fit, within the mandate's constraints.               │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│  STRUCTURED OUTPUT (the deliverable)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ A. Decisions                                            │  │
│  │    - MSFT: Hold (confidence 0.90)                       │  │
│  │    - NVDA: Buy €2,000 more (confidence 0.78)            │  │
│  │    - SAP.DE: Sell 50% of position (confidence 0.82)     │  │
│  │                                                         │  │
│  │ B. Evidence & Sources                                   │  │
│  │    - News articles used (with URLs and dates)           │  │
│  │    - Price data consulted                               │  │
│  │    - Fundamental data points (P/E, earnings, etc.)      │  │
│  │    - Technical signals (RSI, MACD, etc.)                │  │
│  │                                                         │  │
│  │ C. Reasoning & Logic                                    │  │
│  │    - Per-decision rationale (why this action?)           │  │
│  │    - Alternatives considered and why rejected            │  │
│  │    - Risk assessment per recommendation                  │  │
│  │    - How the decision serves the mandate's goals         │  │
│  │                                                         │  │
│  │ D. Confidence & Caveats                                 │  │
│  │    - Confidence score per decision                       │  │
│  │    - Data gaps or limitations encountered               │  │
│  │    - Claims that could not be fully verified             │  │
│  │    - Suggested follow-up research                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

**How the mandate document maps to Parts I–VI:**

The mandate document *absorbs* the responsibilities of the earlier pipeline parts — not by eliminating them, but by declaring *what* the agent should achieve and letting the agent decide *how*:

| Pipeline Part | In Workflows B–D | In Workflow E (Mandate) |
|---|---|---|
| Part I (Investment Universe) | Explicit module with tickers, screeners, allow-list | Section 2 of the mandate: universe constraints as declarative rules |
| Part II (News Retrieval) | Explicit retrieval modules with configured sources | Agent decides which sources to query based on mandate goals |
| Part III (News Evaluation) | Filter/dedup module with configurable thresholds | Agent internally filters what's relevant; output must cite sources |
| Part IV (Data Preparation) | Embedding pipeline, vector DB, chunking strategy | Agent may use RAG internally, but the caller doesn't prescribe it |
| Part V (Portfolio Context) | Explicit data-fetching for prices, fundamentals | Section 3 of the mandate provides current state; agent fetches live data as needed |
| Part VI (Analysis & Decisions) | Structured prompts, confidence scoring, decision docs | The entire agent run IS the analysis; output contract enforces documentation |

**How Part VIII (Evaluation) and Part IX (Self-Optimization) apply:**

This is where the mandate-driven approach differs most from the other workflows — and where it potentially *simplifies* optimization:

- **Optimization target shifts.** In Workflows B–D, you tune dozens of parameters across six pipeline stages (which sources, which embedding model, which chunk size, which prompt template, etc.). In Workflow E, the primary optimization target is **the mandate document itself** — its wording, its constraints, its decision guidelines. This is a single, human-readable artifact.
- **Output as evaluation input.** The structured output (decisions + evidence + reasoning) feeds directly into Part VIII. Evaluators (human or AI) compare the agent's decisions against actual market outcomes, assess reasoning quality, and check evidence validity — exactly as in the other workflows.
- **Self-optimization scope.** Part IX's counterfactual engine asks: "If the mandate had said X instead of Y, would the decisions have been better?" For example:
  - "What if the sector cap were 25% instead of 30%?"
  - "What if the mandate emphasized momentum over quality?"
  - "What if we added 'pay attention to insider trading filings' to the research requirements?"
  - "What if the risk tolerance were set to 'conservative' instead of 'moderate'?"
- **Feedback loop.** The self-optimization process proposes mandate document edits (via shadow mode / A/B testing), evaluates their impact over time, and either auto-applies them (within guardrails) or escalates to human review.

```
                 ┌─────────────────────┐
                 │  Mandate Document   │◄──────── Human edits (manual)
                 │  (v1.0)            │◄──────── Self-optimization proposes edits
                 └────────┬────────────┘
                          │
                          ▼
                 ┌─────────────────────┐
                 │  Autonomous Agent   │──── run N ────►  Output N
                 └─────────────────────┘                     │
                                                             ▼
                                              ┌──────────────────────────┐
                                              │  Part VIII: Evaluation   │
                                              │  Compare decisions vs    │
                                              │  actual market outcomes  │
                                              └────────────┬─────────────┘
                                                           │
                                                           ▼
                                              ┌──────────────────────────┐
                                              │  Part IX: Self-Optimize  │
                                              │  "What if the mandate    │
                                              │   said X instead of Y?"  │
                                              │  Propose mandate edits   │
                                              └────────────┬─────────────┘
                                                           │
                                                 ┌─────────┴──────────┐
                                                 ▼                    ▼
                                        Auto-apply            Escalate to
                                        (within guardrails)   human review
                                                 │
                                                 ▼
                                        Mandate Document (v1.1)
```

**Pros:**
- Simplest architecture — one input, one output, one optimization target.
- Human-readable mandate is easy to review, version-control, and discuss with non-technical stakeholders.
- Leverages the latest agentic capabilities (tool use, multi-step reasoning, web search) without prescribing how the agent works internally.
- Agent can adapt its strategy per run — e.g., spend more time on research when markets are volatile, less when quiet.
- Natural fit for increasingly capable models (GPT-4o, Claude 4, Gemini 2) that can autonomously plan and execute multi-step research.
- Optimization is intuitive: "change the instructions" rather than "tune embedding chunk size from 512 to 768."

**Cons:**
- Less visibility into intermediate steps — you see what the agent *decided* and *why*, but not the detailed trace of every API call, every filtered article, every embedding query. (Mitigated by LangSmith tracing if the agent is built on LangGraph.)
- Harder to debug specific failures — if the agent misses important news, you may not know whether it failed to search, searched the wrong source, or searched correctly but filtered it out.
- Higher per-run token cost — the agent may do redundant research or explore dead ends that a prescriptive pipeline would avoid.
- Reproducibility challenges — the same mandate may produce different decisions on different runs (mitigated by temperature=0 and seed parameters, but not eliminated).
- Quality ceiling depends on the model — if the model is weak at financial reasoning, no amount of mandate tuning will compensate. (Workflows A–C can compensate with better data preparation and structured prompts.)
- The mandate document still needs careful engineering — vague or contradictory instructions lead to poor decisions. This is prompt engineering at a higher level of abstraction.

**Best for:** Teams that want maximum simplicity and trust modern models' autonomous capabilities.

#### Implementation Level 1: Simple Mandate Agent (implement after Workflow B)

Once Workflow B is working, you already have the key components: a research API wrapper, a portfolio context module, and an LLM analysis call. A simple mandate agent wraps these in the mandate-driven interface — no LangGraph, no vector DB, no multi-agent orchestration required.

```
┌────────────────────┐     ┌──────────────────────────────────────┐
│  Mandate Document  │     │  Simple Agent (single LLM + tools)   │
│  (goals, universe, │────►│                                      │
│   portfolio state, │     │  Tools available:                    │
│   guidelines)      │     │   • Research API (from Workflow B)   │
│                    │     │   • yfinance / FMP (from Workflow B) │
│                    │     │   • Output schema (from Workflow B)  │
└────────────────────┘     └──────────────────┬───────────────────┘
                                              │
                                              ▼
                                    Structured Output
                                    (decisions + evidence)
```

**What you build:**
- Mandate document parser (reads the mandate and injects it as system prompt / context)
- A single LLM call (or simple tool-use loop) that receives the mandate + tool results
- Reuses Workflow B's research API wrapper and portfolio context module directly
- Structured output validation (Pydantic schema from Workflow B)

**What you do NOT need yet:**
- LangGraph (no stateful multi-step orchestration)
- Vector DB (no embedding pipeline)
- Multi-agent coordination
- Deep Agents harness

**Why this is valuable early:** It validates the mandate-driven concept with minimal investment. You learn whether a well-crafted mandate document produces better decisions than the explicit pipeline of Workflow B. You also start building the mandate document itself — the artifact that will be optimized in Parts VIII and IX.

**Components reused from Workflow B:**
- Research API wrapper (Perplexity / Tavily / Exa)
- Portfolio context module (yfinance / FMP)
- LLM analysis + structured output schema
- Decision documentation generation

**Components added:**
- Mandate document format (markdown or structured YAML/JSON)
- Mandate parser / prompt injector
- Simple tool-use agent loop (can be as basic as OpenAI function calling)

#### Implementation Level 2: Full Mandate Agent (implement after Workflow D)

Once Workflow D (Multi-Agent) is working, you have the full infrastructure: specialized agents, LangGraph orchestration, vector DB, LangSmith tracing. The full mandate agent uses all of this internally while presenting the same simple mandate-driven interface externally.

```
┌────────────────────┐     ┌──────────────────────────────────────┐
│  Mandate Document  │     │  Full Agent (LangGraph + Deep Agents)│
│  (same format as   │────►│                                      │
│   Level 1)         │     │  Internal orchestration:             │
│                    │     │   • Research Agent (from Workflow D) │
│                    │     │   • Data Agent (from Workflow D)     │
│                    │     │   • Sentiment Agent (from Workflow D)│
│                    │     │   • Analyst Agent (from Workflow D)  │
│                    │     │   • Risk Agent (from Workflow D)     │
│                    │     │   • Vector DB (from Workflow C)      │
│                    │     │   • Planning tools (Deep Agents)     │
│                    │     │   • LangSmith tracing (full trace)   │
└────────────────────┘     └──────────────────┬───────────────────┘
                                              │
                                              ▼
                                    Structured Output
                                    (same schema as Level 1,
                                     but richer evidence trail)
```

**What you add on top of Level 1:**
- LangGraph-based orchestration (the agent internally delegates to sub-agents from Workflow D)
- Vector DB for historical context (from Workflow C)
- Deep Agents harness (planning tools, filesystem access, sub-agent delegation)
- LangSmith tracing for full observability into the agent's internal steps
- Anti-hallucination cross-checking (from Part VI infrastructure)

**Key design principle:** The mandate document format and the output schema stay **identical** between Level 1 and Level 2. The external interface does not change — only the internal sophistication. This means:
- Parts VIII and IX work the same way for both levels (they only see input mandate + output decisions)
- You can A/B test Level 1 vs. Level 2 with the same mandate to measure whether the added complexity actually improves decisions
- The mandate document you've been refining since Level 1 carries over directly

#### Hybrid approach — combining both levels:

In practice, Level 1 and Level 2 are not mutually exclusive. A pragmatic architecture might:

1. Use the **mandate document** as the high-level configuration and goal definition (same document for both levels).
2. Run **Level 1** (simple agent) as a fast daily check — low cost, quick results.
3. Run **Level 2** (full agent) as a weekly deep analysis — higher cost, more thorough research.
4. Compare outputs from both levels as an additional evaluation signal.
5. Use **n8n** as the outer scheduling and integration layer (triggers, notifications, human review routing).
6. Feed both the mandate document *and* the agent's structured output into Parts VIII and IX for evaluation and self-optimization.

This gives you the simplicity of the mandate-driven interface with the observability and debuggability of the pipeline approach.

### Monitoring & Observability

Regardless of workflow choice, monitoring is essential:

- **LangSmith:** Trace every agent step — which sources were queried, what was filtered, how the LLM reasoned, what was recommended. Detect hallucinations, track latency, monitor costs.
- **Custom dashboards:** Track recommendation accuracy over time (did the market move as the agent predicted?).
- **Alerting:** Notify if the pipeline fails, if a data source becomes unavailable, or if the agent's confidence drops consistently.

---

## Part VIII: Evaluation & Optimization Framework

The per-step optimization subsections (in Parts I–VI) define **what** each step should log and **which** parameters are tunable. This section describes the **overarching framework** that connects all review artifacts into a systematic improvement cycle.

### Core Principle

> **Every pipeline run is an experiment.** Parameters are hypotheses. Review documents are observations. Market outcomes are ground truth. Optimization is the scientific method applied to portfolio analysis.

The pipeline is not "finished" when it produces its first recommendation. It is finished when it *reliably* produces *good* recommendations — and that requires an iterative feedback loop.

### Review Document Standard

Every step in the pipeline must produce a structured JSON review document (as shown in Parts I–VI). To enable cross-step analysis, all review documents must share a common envelope:

```json
{
  "run_id": "2026-02-07-14:30",
  "step": "universe | retrieval | evaluation | preparation | context | analysis",
  "timestamp": "2026-02-07T14:32:15Z",
  "pipeline_version": "v2.3",
  "parameters": { "...step-specific tunable parameters..." },
  "metrics": { "...step-specific measurements..." },
  "artifacts": { "...step-specific output data..." },
  "flags": ["coverage_gap_SIE_DE", "low_confidence_MSFT"]
}
```

**Storage:** Store review documents in a structured format (JSON files in a timestamped directory, a database, or an experiment tracking platform). Each pipeline run should produce one review document per step, all linked by `run_id`.

**Aggregated run summary:** After all steps complete, generate a single **Run Summary** that links all per-step review documents and adds the final recommendation:

```json
{
  "run_id": "2026-02-07-14:30",
  "pipeline_version": "v2.3",
  "steps": {
    "universe": {"universe_size": 145, "assets_added": 3, "assets_removed": 1, "flags": []},
    "retrieval": {"articles_fetched": 47, "errors": 0, "flags": []},
    "evaluation": {"articles_passed": 14, "filtered": 33, "flags": []},
    "preparation": {"chunks_created": 28, "rag_relevance": "good", "flags": []},
    "context": {"tokens_used": 4850, "utilization": "38%", "flags": []},
    "analysis": {"recommendations": 3, "avg_confidence": 0.78, "flags": ["low_confidence_MSFT"]}
  },
  "decision_audit": {
    "hallucination_rate": 0.0,
    "source_coverage": 0.95,
    "consistency_rate": 1.0,
    "claims_verified": 8,
    "claims_failed": 0
  },
  "final_recommendations": ["NVDA: Hold (0.85)", "MSFT: No action (0.52)", "SIE.DE: Buy more (0.71)"],
  "market_outcome": null
}
```

The `market_outcome` field is filled in retrospectively (e.g. after 1 day, 7 days, 30 days) to provide ground truth for optimization.

### Experiment Tracking

Use an experiment tracking platform to compare pipeline runs with different parameter configurations:

| Platform | Best For | Notes |
|----------|----------|-------|
| **LangSmith** | LLM-specific tracing | Native LangChain integration; traces prompt/response, latency, token usage. Best for debugging individual LLM calls. |
| **MLflow** | Experiment comparison | Log parameters, metrics, and artifacts per run. Compare configurations side-by-side. Good for systematic hyperparameter tuning. |
| **Weights & Biases** | Rich visualization | Dashboards, charts, parameter sweep visualization. More powerful than MLflow for complex experiments. |
| **Custom (file-based)** | Simplicity | JSON files in a timestamped directory. No infrastructure needed. Sufficient for early-stage projects. |

**Recommendation:** Start with file-based logging + LangSmith. Once you need to compare many configurations systematically, add MLflow or W&B.

**What to track per experiment:**

- Pipeline version / configuration hash
- All tunable parameters (across all steps)
- Per-step metrics (articles fetched, filtered, tokens used, latency, cost)
- Final recommendations
- Market outcomes (filled in retrospectively)
- Total pipeline cost (API calls + LLM tokens)
- Total pipeline latency

### Human Review Workflow

Not every run needs human review. Define a review cadence and trigger conditions:

**Scheduled review:**
- **Daily:** Skim the Run Summary — check for flags, errors, or unusually low confidence.
- **Weekly:** Deep-dive into 2-3 runs. Read the full Analysis Log. Compare recommendations against actual market outcomes. Identify patterns.
- **Monthly:** Review aggregate metrics. Which parameter changes improved outcomes? Are there persistent coverage gaps or filter failures?

**Triggered review (review immediately when):**
- A recommendation had very high confidence but the market moved opposite
- A step produced errors or zero results
- Confidence scores dropped significantly compared to the rolling average
- A new source was added or a parameter was changed (review the first 3 runs with the new configuration)
- A decision record has "high" or "critical" hallucination risk (a factual claim was wrong or reasoning contradicted the action)
- The hallucination rate exceeds 10% over a rolling 7-day window

**Review checklist for humans:**

1. **Universe Update Log:** Were universe changes appropriate? Were any assets incorrectly added/removed? Did the master allow-list correctly filter violations?
2. **Retrieval Log:** Were all expected sources queried? Any errors? Any coverage gaps?
3. **Evaluation Report:** Were the right articles kept? Scan the filtered list — was anything important discarded?
4. **Preparation Report:** Are RAG retrieval tests returning relevant results?
5. **Context Snapshot:** Was the right data provided? Anything missing?
6. **Analysis Log:** Read the LLM's reasoning. Is it sound? Does it match the news? Are cited numbers correct?
7. **Decision Records:** Are decisions well-documented? Were alternatives genuinely considered? Did the hallucination check catch all factual errors? Were any decisions based on unverifiable claims?
6. **Outcome comparison:** Did the market behave as the agent predicted?

### AI-Assisted Optimization

Beyond human review, a **meta-agent** can review pipeline outputs and suggest parameter adjustments:

**Concept:** A separate LLM agent (the "Optimizer Agent") receives:
- The Run Summary (or multiple summaries over a time period)
- The retrospective market outcomes
- The current parameter configuration

**Prompt (conceptual):**

```
You are a pipeline optimization expert. Review the following pipeline run summaries
from the past week, including market outcomes.

[...run summaries with outcomes...]

Current configuration:
- Relevance threshold: 0.6
- Sentiment model: alpha_vantage (API-provided)
- Embedding model: text-embedding-3-small
- Analysis model: gpt-4o, temperature 0.2
- Prompt template: v2.3

Identify:
1. Which step appears to be the weakest link (most errors, worst contribution to outcome)?
2. Which parameter changes would you suggest testing next?
3. Are there patterns in failed recommendations (e.g. always wrong on macro news)?

Be specific and justify each suggestion with evidence from the run summaries.
```

**Important:** The Optimizer Agent suggests changes but does not apply them automatically. All parameter changes should be reviewed by a human before deployment.

### Backtesting Framework

To evaluate parameter changes without risking real portfolio decisions, implement backtesting:

**How it works:**
1. **Collect historical data:** Store raw retrieval results, market prices, and outcomes for past runs.
2. **Replay with new parameters:** Re-run the pipeline (Parts III–VI) on historical data with modified parameters.
3. **Compare outcomes:** Did the new parameters produce better recommendations for the historical period?

**Example:** You suspect the relevance threshold (currently 0.6) is too low, causing noise. Replay the past 30 days of retrieved articles with threshold 0.7:
- How many articles would have been filtered additionally?
- Would any important articles (that correlated with market moves) have been lost?
- Would the final recommendations have been different? Better?

**Limitations:**
- Backtesting cannot test Part II (retrieval) changes, since you'd need to re-query APIs for historical dates (not always possible).
- LLM responses are non-deterministic — use temperature 0.0 for backtesting to maximize reproducibility.
- Past performance does not guarantee future results. Use backtesting to catch obvious regressions, not to overfit to historical data.

### A/B Testing Pipeline Configurations

For changes that cannot be reliably backtested, run two configurations in parallel:

**How it works:**
1. **Configuration A** (current/control): The existing pipeline with current parameters.
2. **Configuration B** (challenger): The pipeline with the proposed parameter change.
3. Both process the same input data on the same day.
4. Compare recommendations and (after the market moves) compare outcomes.

**When to use A/B testing:**
- When changing the analysis model (e.g. GPT-4o → Claude 4 Sonnet)
- When changing the prompt template significantly
- When switching retrieval sources (e.g. Alpha Vantage → Finnhub)
- When changing the embedding model or vector DB

**Cost consideration:** Running two pipelines doubles API and LLM costs. Limit A/B tests to 1-2 weeks, then decide based on accumulated evidence.

### Optimization Cadence

| Frequency | Activity | Scope |
|-----------|----------|-------|
| **Every run** | Generate review documents for all steps | Automated |
| **Daily** | Skim Run Summary, check for flags | Human (5 min) |
| **Weekly** | Deep review of 2-3 runs, compare with market outcomes | Human (30-60 min) |
| **Bi-weekly** | Run Optimizer Agent on accumulated summaries | AI-assisted |
| **Monthly** | Aggregate metrics review, parameter adjustment decisions | Human (1-2 hours) |
| **Quarterly** | Full pipeline audit — source relevance, model performance, strategy alignment | Human + AI |

### Decision Audit Integration

The decision documentation from Part VI feeds directly into the evaluation framework. During every review cycle, the following decision-quality metrics are tracked:

**Automated metrics (computed every run):**

| Metric | Description | Target |
|--------|-------------|--------|
| **Hallucination rate** | % of recommendations with medium+ hallucination risk | < 5% |
| **Source coverage** | % of key_factors backed by explicit evidence_sources | > 90% |
| **Consistency rate** | % of recommendations where reasoning aligns with action | 100% |
| **Verification pass rate** | % of quantitative claims that pass automated fact-checking | > 95% |
| **Alternative consideration rate** | % of decisions with documented alternative_actions_considered | > 80% |

**Trend alerts:**

- If the hallucination rate exceeds 10% over a rolling 7-day window, trigger an immediate review.
- If source coverage drops below 80%, the pipeline may have a data preparation gap (Part IV) or context gap (Part V).
- If consistency rate drops below 95%, the prompt template may need revision.

**Human review integration:**

During the weekly deep-dive (see Optimization Cadence), reviewers should:
1. Read the decision records for the highest-confidence and lowest-confidence recommendations.
2. Verify that the hallucination check correctly identified all issues (audit the auditor).
3. Assess whether alternative actions were genuinely considered or whether the documentation is pro-forma.
4. Check whether decisions with "low" hallucination risk but wrong market outcomes had subtle factual errors that the automated check missed.

### Optimization Priorities

When starting out, not all parameters matter equally. Focus optimization efforts in this order:

1. **Analysis model & prompt** (Part VI) — Has the largest impact on recommendation quality. Small prompt changes can dramatically improve or degrade output.
2. **Decision documentation quality** (Part VI) — Undocumented or poorly documented decisions cannot be optimized. Ensure the anti-hallucination framework is working before tuning other parameters.
3. **Evaluation thresholds** (Part III) — Determines the signal-to-noise ratio. Too aggressive = missed insights. Too lenient = wasted tokens and confused LLM.
4. **Source selection** (Part II) — Are the right sources being queried? Are there coverage gaps for specific asset types?
5. **Universe composition** (Part I) — Is the investment universe comprehensive enough? Are opportunities being missed?
6. **RAG quality** (Part IV) — Only matters if your pipeline uses historical context retrieval. Test embedding models and chunk strategies.
7. **Context composition** (Part V) — Which indicators and fundamentals to include. Less critical early on; becomes important as the pipeline matures.

> **Part VIII provides the tools and processes for optimization. But who triggers it?** The human review cadence above works for deliberate tuning. However, if parameters remain unchanged for weeks or months, the pipeline may silently degrade as markets evolve, sources change quality, or models update. **Part IX** addresses this by adding an autonomous self-optimization layer that runs continuously and ensures the pipeline never becomes stale.

---

## Part IX: Continuous Self-Optimization

Part VIII describes *how* to evaluate and optimize (tools, review documents, human cadence). This section describes a system that does it **autonomously and continuously** — detecting when parameters become stale, simulating what would have happened under different settings, and applying improvements without waiting for a human review cycle.

### Core Principle

> **A pipeline with static parameters decays over time.** Markets shift regimes, data sources change quality, LLM providers update models, and what worked last month may underperform this month. The system must actively seek improvement, not passively wait for a human to notice degradation.

### 1. Counterfactual Analysis Engine

The heart of self-optimization. After every pipeline run — once the market outcome is known (typically 1-7 days later) — the system automatically asks: **"What would have happened with different parameters?"**

**How it works:**

1. **Trigger:** A completed run's `market_outcome` field is filled in (e.g. by an automated price-check job).
2. **Replay:** The system re-runs Parts III–VI on the *same input data* from that run, but with alternative parameter values.
3. **Compare:** Did the alternative parameters produce a better recommendation?
4. **Log:** Store the counterfactual result alongside the original run.

**What to simulate (examples):**

| Original Parameter | Counterfactual Variants | Question Answered |
|--------------------|------------------------|-------------------|
| Relevance threshold: 0.6 | 0.5, 0.7, 0.8 | Would a tighter/looser filter have improved the recommendation? |
| Analysis model: GPT-4o | Claude 4 Sonnet, Gemini 2 | Would a different model have reasoned better? |
| Prompt template: v2.3 | v2.2 (previous), v2.4 (experimental) | Did the latest prompt change help or hurt? |
| Sentiment: API-provided | LLM-based (GPT-4o-mini) | Would richer sentiment have changed the outcome? |
| Indicators: SMA_50, RSI | SMA_50, SMA_200, RSI, MACD, Volume | Would more context have helped the analysis? |

**Counterfactual result document:**

```json
{
  "original_run_id": "2026-02-07-14:30",
  "counterfactual_id": "cf-2026-02-07-14:30-eval-threshold-07",
  "parameter_changed": "evaluation.relevance_threshold",
  "original_value": 0.6,
  "counterfactual_value": 0.7,
  "original_recommendation": {"NVDA": "Hold", "confidence": 0.85},
  "counterfactual_recommendation": {"NVDA": "Hold", "confidence": 0.88},
  "market_outcome": {"NVDA": "+4.2%"},
  "verdict": "Counterfactual slightly better (higher confidence, same correct action)",
  "improvement_score": 0.03
}
```

**Cost management:** Running counterfactuals for every parameter on every run is expensive. Prioritize:
- Only simulate the top 2-3 parameters identified as most impactful (see Part VIII: Optimization Priorities).
- Use temperature 0.0 for reproducibility.
- Run counterfactuals during off-peak hours (overnight) when API costs may be lower.
- Use lighter models for counterfactual analysis where possible (e.g. GPT-4o-mini instead of GPT-4o for the counterfactual, unless the parameter being tested is the model itself).

### 2. Parameter Staleness Detection

The system tracks when each parameter was last changed and flags parameters that may have become stale.

**Staleness rules:**

| Parameter Category | Max Staleness | Rationale |
|--------------------|---------------|-----------|
| Analysis model | 60 days | LLM providers frequently release improved models |
| Prompt template | 30 days | Prompts should evolve as the portfolio or strategy changes |
| Relevance threshold | 30 days | Market volatility changes what counts as "relevant" |
| Source selection | 90 days | Sources rarely change quality overnight, but APIs do sunset |
| Embedding model | 90 days | Embedding quality is relatively stable |
| Technical indicators | 60 days | Different market regimes favor different indicators |

**Staleness alert document:**

```json
{
  "alert_type": "parameter_staleness",
  "timestamp": "2026-03-15T08:00:00Z",
  "stale_parameters": [
    {
      "parameter": "analysis.prompt_template",
      "current_value": "v2.3",
      "last_changed": "2026-01-10",
      "days_stale": 64,
      "max_staleness_days": 30,
      "counterfactual_evidence": "In 12 of the last 30 counterfactual simulations, v2.4-experimental outperformed v2.3 (avg improvement_score: +0.07)",
      "recommendation": "Promote v2.4-experimental to active via shadow testing"
    }
  ]
}
```

### 3. Drift Detection & Market Regime Awareness

Beyond parameter staleness, the system should detect when the *environment* has changed enough that the current configuration may no longer be optimal.

**What to monitor:**

- **Recommendation accuracy trend:** If the 7-day rolling accuracy drops below a threshold (e.g. from 70% correct to 50%), something has changed.
- **Confidence calibration:** If the agent says "0.85 confidence" but is only correct 60% of the time at that confidence level, the confidence model is miscalibrated.
- **Hallucination rate trend:** If the hallucination rate from decision documentation (Part VI) is rising, the analysis model may be degrading or the context provided may be insufficient. Correlate hallucination spikes with accuracy drops.
- **Decision quality drift:** If the source coverage rate or alternative consideration rate (from decision audit metrics in Part VIII) is declining, the pipeline may be cutting corners — likely due to context window pressure or prompt degradation.
- **Source quality drift:** If a source starts returning more errors, slower responses, or lower-quality articles, flag it.
- **Market regime change:** Volatility spikes (VIX), sector rotation, bear/bull transitions. Different regimes may need different parameters (e.g. tighter relevance filters during high-volatility periods when noise increases).

**Drift alert document:**

```json
{
  "alert_type": "accuracy_drift",
  "timestamp": "2026-03-20T08:00:00Z",
  "metric": "7d_rolling_accuracy",
  "current_value": 0.52,
  "baseline_value": 0.71,
  "decline_pct": -26.8,
  "possible_causes": [
    "Market regime shifted to high-volatility (VIX: 28.4, was 15.2)",
    "Prompt template v2.3 may not handle macro-driven markets well",
    "Source alpha_vantage latency increased 3x this week"
  ],
  "suggested_actions": [
    "Run counterfactual with high-volatility prompt variant",
    "Add Benzinga WIM as source for price-movement context",
    "Investigate alpha_vantage latency issue"
  ]
}
```

### 4. Shadow Mode (Canary Testing)

Before applying a parameter change to the live pipeline, run it in **shadow mode** — processing the same live data with the new parameters, but without affecting the actual recommendations.

**How it works:**

1. **Shadow pipeline:** A second instance of the pipeline runs alongside the live one with the proposed parameter change.
2. **Same input:** Both pipelines receive identical input data.
3. **No output:** The shadow pipeline's recommendations are logged but *not surfaced* to the user.
4. **Comparison:** After a defined period (e.g. 5-10 runs), compare shadow vs. live recommendations against actual market outcomes.
5. **Promotion decision:** If shadow consistently outperforms or matches live, promote the change. If it underperforms, discard it.

**Shadow test document:**

```json
{
  "shadow_test_id": "shadow-prompt-v2.4",
  "parameter_changed": "analysis.prompt_template",
  "live_value": "v2.3",
  "shadow_value": "v2.4-experimental",
  "started": "2026-03-15",
  "runs_completed": 8,
  "comparison": {
    "live_accuracy": 0.68,
    "shadow_accuracy": 0.75,
    "live_avg_confidence": 0.74,
    "shadow_avg_confidence": 0.77
  },
  "status": "shadow_outperforming",
  "recommendation": "Promote v2.4-experimental after 2 more runs for statistical significance"
}
```

**Cost consideration:** Shadow mode doubles the cost for the changed step (not the entire pipeline, since input data is shared). Limit to one shadow test at a time.

### 5. Automated Parameter Rollout

Once a parameter change passes shadow testing, it can be applied automatically — within guardrails.

**Rollout process:**

```
Counterfactual evidence accumulates
         │
         ▼
Staleness alert triggers (or drift detected)
         │
         ▼
Self-optimization agent proposes change
         │
         ▼
   ┌─────┴─────┐
   │ Guardrail │──── Change exceeds safety limits? ──→ Escalate to human
   │   check   │
   └─────┬─────┘
         │ passes
         ▼
Shadow mode activated (5-10 runs)
         │
         ▼
   ┌─────┴─────┐
   │ Shadow    │──── Shadow underperforms? ──→ Discard change, log result
   │ evaluation│
   └─────┬─────┘
         │ outperforms
         ▼
Parameter applied to live pipeline
         │
         ▼
Post-rollout monitoring (3 days)
         │
         ▼
   ┌─────┴─────┐
   │ Rollback  │──── Performance degrades? ──→ Automatic rollback to previous
   │   check   │
   └─────┬─────┘
         │ stable
         ▼
Change confirmed. Previous value archived.
```

### 6. Self-Optimization Safety Rails

Autonomous optimization is powerful but dangerous without constraints. Define hard limits:

**What can be auto-optimized (within guardrails):**
- Relevance threshold (within ±0.15 of human-set baseline)
- Batch window size (within defined range, e.g. 15 min – 4 hours)
- Minimum article length filter (within range)
- TTL for vector DB entries (within range)
- Prompt template (only to versions pre-approved as "experimental candidates")
- Temperature (within 0.0 – 0.4 range)

**What requires human approval:**
- Changing the master allow-list or investment universe constraints (Part I)
- Changing the analysis LLM model (e.g. GPT-4o → Claude 4)
- Adding or removing a data source
- Changing the portfolio strategy or risk constraints
- Modifying the output schema or decision documentation schema
- Any parameter change exceeding the guardrail range
- Disabling a pipeline step

**Rollback triggers (auto-revert immediately if):**
- Recommendation accuracy drops below an absolute floor (e.g. < 40% over 5 runs)
- A pipeline step starts producing errors after the change
- Confidence scores collapse (average drops below 0.4)
- Cost per run increases beyond a threshold (e.g. 2x the rolling average)

**Maximum concurrent changes:** Only one parameter may be in shadow testing at any time. Never auto-apply two changes simultaneously — it becomes impossible to attribute improvement or degradation to a specific change.

### Self-Optimization Architecture

The self-optimization system runs as a **separate, scheduled process** (not inline with the main pipeline):

```
┌─────────────────────────────────────────────────────────────┐
│                  SELF-OPTIMIZATION LOOP                       │
│                  (runs every N hours)                         │
│                                                              │
│  1. Check: Any runs with market_outcome filled in?           │
│     └─→ Run counterfactual simulations on those runs         │
│                                                              │
│  2. Check: Any parameters stale?                             │
│     └─→ Generate staleness alerts                            │
│                                                              │
│  3. Check: Accuracy or confidence drifting?                  │
│     └─→ Generate drift alerts                                │
│                                                              │
│  4. Check: Enough counterfactual evidence for a change?      │
│     └─→ Propose parameter change                             │
│         └─→ Guardrail check                                  │
│             └─→ Start shadow test (or escalate to human)     │
│                                                              │
│  5. Check: Any active shadow tests with enough runs?         │
│     └─→ Evaluate shadow vs. live                             │
│         └─→ Promote, discard, or extend test                 │
│                                                              │
│  6. Check: Any recently promoted changes?                    │
│     └─→ Post-rollout monitoring                              │
│         └─→ Confirm or rollback                              │
│                                                              │
│  Output: Self-optimization report (logged + alerts if needed)│
└─────────────────────────────────────────────────────────────┘
```

**Self-optimization report (generated each cycle):**

```json
{
  "cycle_timestamp": "2026-03-20T02:00:00Z",
  "counterfactuals_run": 6,
  "staleness_alerts": 1,
  "drift_alerts": 0,
  "active_shadow_tests": [
    {"id": "shadow-prompt-v2.4", "runs": 8, "status": "outperforming"}
  ],
  "changes_promoted_today": [],
  "changes_rolled_back_today": [],
  "next_proposed_change": "Promote prompt v2.4 after 2 more shadow runs",
  "human_escalations": []
}
```

### Relationship Between Part VIII and Part IX

| Aspect | Part VIII (Human-Driven) | Part IX (Autonomous) |
|--------|------------------------|----------------------|
| **Trigger** | Scheduled cadence (daily/weekly/monthly) | Continuous (every N hours) |
| **Who decides** | Human reviews evidence, makes decisions | System proposes and applies within guardrails |
| **Speed** | Days to weeks per optimization cycle | Hours to days per cycle |
| **Scope** | Can change anything (strategy, models, sources) | Constrained to guardrailed parameters |
| **Risk** | Low (human judgment) | Managed (shadow testing + rollback) |
| **Best for** | Major changes, strategy shifts, new sources | Fine-tuning thresholds, prompt iterations, model swaps |
| **Data source** | Same review documents from Parts I–VI | Same review documents + counterfactual results |

**They are complementary, not competing.** Part IX handles the continuous fine-tuning so that Part VIII's human reviews can focus on strategic decisions rather than parameter babysitting.

---

## Source Decision Guide

| Need | Recommended Source | Cost Factor |
|------|--------------------|-------------|
| Index constituents (universe) | FMP / Polygon.io reference data / Wikipedia (S&P 500 list) | Free–Low |
| Crypto universe data | CoinGecko API / CoinMarketCap | Free–Low |
| Maximum precision per stock | Financial Modeling Prep / Alpha Vantage / Finnhub | Free–Medium |
| Broad market overview | SerpApi (Google Search) / Tavily | Low |
| AI-native research (search + summarize) | Online Research LLMs (Perplexity / Exa / YOU.com / Gemini) / Tavily | Low–Medium |
| Price movement context | Benzinga ("Why Is It Moving") | Medium–High |
| German news & general coverage | RSS Feeds (Handelsblatt etc.) / NewsAPI | Free/Low |
| German regulatory ad-hoc filings | EQS News / DGAP | Free |
| International markets | EOD Historical Data (EODHD) | Low–Medium |
| Real-time streaming | Polygon.io / Finnhub (WebSocket) | Medium |
| Quantitative data (prices, fundamentals) | yfinance (free) / FMP / Alpha Vantage | Free–Medium |
| Technical indicators | Compute locally with `pandas-ta` / `ta` | Free |
| Social sentiment | StockTwits / Reddit API | Free–Low |
| Vector storage | ChromaDB (prototype) / Pinecone (production) | Free–Medium |
| MCP-based data access | Alpha Vantage MCP / FMP MCP / FactSet MCP | Free–High |
| Real-time / Professional level | Bloomberg Terminal (subscription, ~$24k+/year) | Very High |

---

## Appendix A: Online Research LLMs — Deep Dive

Online Research LLMs (also called "AI Search APIs" or "Grounded LLMs") are models that perform a real-time web search in the background, read the contents of multiple pages, and synthesize an answer with source citations. They fundamentally change the agent's architecture by replacing the multi-step search → scrape → clean → summarize pipeline with a single API call.

### Why Online Research LLMs Make Sense

Instead of laboriously searching, scraping, and cleaning "raw data", you delegate the entire research step to a model built exactly for that purpose. No training cutoff applies to the search results — the model retrieves live information.

### Benefits (Shared Across Providers)

- **Pipeline simplification:** Classic approach (Search API → URLs → Scraper → Cleaner → LLM) is replaced by a single API call.
- **Noise reduction:** The research LLM filters SEO spam and duplicates internally, delivering a curated summary.
- **Source referencing:** Most providers return citation URLs for manual review and verification.
- **Recency:** Models are tuned for current information, essential for financial news.

### Drawbacks / Risks (Shared Across Providers)

- **Black box:** Less control over which sources are scanned. Some providers offer domain filters (e.g. Perplexity's `search_domain_filter`) to mitigate this.
- **Hallucinations with numbers:** LLMs can make errors with specific financial figures (e.g. "revenue rose 3.4%"). For hard data (earnings reports), always cross-check against a financial API (FMP, Alpha Vantage).
- **Provider lock-in:** Each provider has a slightly different API format. Abstract the research step behind an interface to make switching easier.

### Provider Comparison

| Provider | Accuracy (SimpleQA) | Latency | Key Feature | API Style |
|----------|---------------------|---------|-------------|-----------|
| **Perplexity Sonar** | 93.9% | Medium | Domain filtering, OpenAI-compatible API | OpenAI SDK compatible |
| **Exa.ai Research Pro** | 94.9% (highest) | Medium | Neural/semantic search, highest factuality | Custom REST API |
| **YOU.com** | 93.0% | Fast (< 500ms) | Speed/depth tradeoff endpoints, cost-effective | Custom REST API |
| **Tavily** | 93.3% | Medium | Native LangChain, Search + Extract + Crawl | LangChain SDK / REST |
| **Google Gemini + Grounding** | N/A (Google quality) | Medium | Google Search quality, multi-turn, multimodal | Google AI SDK |

### Recommended Selection Criteria

- **Accuracy-first** (earnings data, specific figures): Exa.ai Research Pro
- **Cost-first** (high volume, budget constraints): YOU.com
- **Integration-first** (LangChain/LangGraph ecosystem): Tavily
- **Flexibility-first** (OpenAI-compatible, domain filtering): Perplexity Sonar
- **Ecosystem-first** (Google Cloud, Vertex AI): Gemini with Grounding

### Research API-Based Architecture

Regardless of which provider you choose, the architecture follows the same pattern:

**Step 1: "Research Agent" (Online Research LLM)**
Send a prompt to the research API for each portfolio position (or for the overall market).

**Step 2: "Portfolio Manager" (GPT-4o, Claude 4, or Gemini 2)**
Feed the cleaned, condensed research output into the analysis agent alongside portfolio context and quantitative data.

> **Note:** Always inject the current date dynamically (e.g. via `datetime.now().strftime(...)`) into research prompts to ensure the API targets the most recent information. This applies to all providers.

---

## Appendix B: Implementation Guide

This appendix covers practical implementation decisions: programming language, libraries, frameworks, MCP servers, testing strategies, and coding conventions. These choices are orthogonal to the pipeline architecture (Parts I–IX) but critical for building a maintainable, testable, and production-ready system.

### Programming Language

**Python is the clear primary choice** for this project. The reasons are overwhelming:

- **AI/ML ecosystem:** LangChain, LangGraph, LangSmith, OpenAI SDK, and virtually all LLM provider SDKs are Python-first.
- **Financial data libraries:** `yfinance`, `pandas`, `pandas-ta`, `ta`, `numpy` — the quantitative finance ecosystem is Python-native.
- **Data processing:** `pandas`, `polars` (for high-performance), `pydantic` (for schema validation).
- **Vector databases:** All major vector DB clients (ChromaDB, Pinecone, Qdrant, Weaviate) have first-class Python SDKs.
- **Community and hiring:** The largest pool of AI/financial-Python developers and the most extensive documentation.

**Reasonable alternatives (for specific components only):**

| Language | Use Case | Pros | Cons |
|----------|----------|------|------|
| **TypeScript/Node.js** | Web dashboard, API layer, real-time WebSocket handlers | Strong async I/O, good for UI/API, Vercel AI SDK | Weaker financial/ML library ecosystem |
| **Rust** | Performance-critical modules (backtesting engine, high-frequency data processing) | Extreme performance, memory safety | Steep learning curve, smaller AI ecosystem |
| **Go** | Infrastructure components (scheduling, queue management, microservice mesh) | Fast compilation, excellent concurrency, simple deployment | Poor AI/ML library support |

**Recommendation:** Write the core pipeline in Python. If you need a web interface, consider TypeScript for the frontend/API layer. If backtesting performance becomes a bottleneck, consider using `vectorbt` (NumPy-based) or `NautilusTrader` (Rust/C++ backend with Python API) rather than rewriting in another language.

### Core Libraries & Frameworks

**Agent orchestration:**

| Library | Role | Notes |
|---------|------|-------|
| **LangChain** | Foundation for LLM interactions, prompt templates, chains | Core dependency; provides abstractions for LLM calls, tool use, output parsing |
| **LangGraph** | Multi-agent orchestration, stateful workflows | Built on LangChain; defines agent graphs with conditional edges. Essential for Workflow D (multi-agent). |
| **LangSmith** | Observability, tracing, debugging | Traces every LLM call; essential for debugging and optimization (Parts VIII–IX). Free tier available. |
| **Pydantic** | Data validation, structured output schemas | Enforces JSON schemas for review documents, decision records, API responses. Use Pydantic v2. |

**Financial data & analysis:**

| Library | Role | Notes |
|---------|------|-------|
| **yfinance** | Free market data (prices, fundamentals) | No API key required. Good for prototyping. Unofficial, may break. |
| **pandas / polars** | Data manipulation, time series analysis | `pandas` for compatibility; `polars` for performance on large datasets |
| **pandas-ta** or **ta** | Technical indicator computation | Computes SMA, EMA, RSI, MACD, etc. from price data |
| **numpy** | Numerical computation | Foundation for quantitative analysis |
| **fmp-data** | Financial Modeling Prep Python client | LangChain integration available via `langchain-fmp-data` |

**Vector databases & embeddings:**

| Library | Role | Notes |
|---------|------|-------|
| **chromadb** | Local vector database | Best for prototyping; no server required |
| **pinecone-client** | Pinecone cloud vector DB | Production-ready; fully managed |
| **qdrant-client** | Qdrant vector DB | Self-hosted or cloud; rich filtering |
| **sentence-transformers** | Local embedding models | Run `all-MiniLM-L6-v2` etc. locally for free |
| **openai** | OpenAI embeddings & LLM calls | `text-embedding-3-small/large`; also used for Perplexity API |

**HTTP & async:**

| Library | Role | Notes |
|---------|------|-------|
| **httpx** | Async HTTP client | Preferred over `requests` for async pipelines |
| **aiohttp** | Async HTTP (alternative) | Good for WebSocket connections (Polygon.io, Finnhub) |
| **tenacity** | Retry logic with backoff | Essential for robust API calls; configurable retry strategies |

**Scheduling & infrastructure:**

| Library | Role | Notes |
|---------|------|-------|
| **APScheduler** | Task scheduling | Schedule pipeline runs, universe updates, self-optimization cycles |
| **celery** | Distributed task queue | For production systems with multiple workers |
| **python-dotenv** | Environment variable management | Keeps API keys out of code |

### MCP Servers for Financial Data

Model Context Protocol (MCP) servers enable AI agents to query financial data through standardized tool interfaces, eliminating custom API integration code. As of early 2026, the MCP ecosystem for financial data is maturing rapidly.

**Available MCP servers:**

| MCP Server | Data Provided | Notes |
|------------|---------------|-------|
| **Alpha Vantage MCP** | Real-time/historical prices, fundamentals, news, technical indicators | Official server (mcp.alphavantage.co). 115+ functions. Updated Jan 2026 for reduced token usage. Integrates with Claude, VS Code, Cursor. |
| **Financial Modeling Prep MCP** | Earnings, SEC filings, financial statements, stock screener | Community and official options available. Good for fundamental data. |
| **Polygon.io MCP** | Real-time market data, reference data | Experimental; good for streaming price data |
| **FactSet MCP** | Institutional-grade financial data | Production-grade MCP server announced 2025. Enterprise pricing. |
| **Yahoo Finance MCP** | Basic market data via yfinance | Community-built; free but unofficial |

**When to use MCP vs. direct API calls:**

| Scenario | Recommendation |
|----------|---------------|
| Agent needs to *autonomously decide* what data to fetch | MCP (the agent invokes tools as needed) |
| Pipeline has a *fixed, predictable* data flow | Direct API calls (simpler, faster, lower token cost) |
| Rapid prototyping with Claude / Cursor | MCP (instant integration, no code needed) |
| Production pipeline with strict latency requirements | Direct API calls (less overhead) |

**Recommendation:** Use MCP servers for the research and exploration phase. Transition critical data paths to direct API calls in production for reliability and cost control. Keep MCP available for ad-hoc queries (e.g. when the Analyst Agent needs to look up a specific data point not pre-fetched by the pipeline).

### Modular Architecture

The pipeline should be split into independently testable modules. Each module maps to a Part in the architecture:

```
src/
├── universe/              # Part I: Investment Universe
│   ├── __init__.py
│   ├── manager.py         # Universe CRUD, update logic
│   ├── screener.py        # Screening criteria evaluation
│   ├── master_allow_list.py  # Constraint enforcement
│   └── sources/           # Index-specific data fetchers
│       ├── sp500.py
│       ├── dax.py
│       └── crypto.py
├── retrieval/             # Part II: News Retrieval
│   ├── __init__.py
│   ├── orchestrator.py    # Coordinates multiple sources
│   └── sources/
│       ├── alpha_vantage.py
│       ├── fmp.py
│       ├── serpapi.py
│       ├── tavily.py
│       └── research_llm.py  # Online Research LLM wrapper
├── evaluation/            # Part III: News Evaluation
│   ├── __init__.py
│   ├── dedup.py           # Deduplication (SimHash)
│   ├── relevance.py       # Relevance scoring
│   ├── sentiment.py       # Sentiment analysis (API + LLM)
│   └── impact.py          # Portfolio-specific impact
├── preparation/           # Part IV: Data Preparation
│   ├── __init__.py
│   ├── schema.py          # Structured news schema (Pydantic)
│   ├── cleaner.py         # Text cleaning & normalization
│   ├── embeddings.py      # Embedding generation
│   ├── vector_store.py    # Vector DB interface
│   └── chunking.py        # Document chunking strategies
├── context/               # Part V: Portfolio Context
│   ├── __init__.py
│   ├── portfolio.py       # Holdings, strategy, constraints
│   ├── prices.py          # Price data fetching
│   ├── fundamentals.py    # Earnings, valuation metrics
│   └── indicators.py      # Technical indicator computation
├── analysis/              # Part VI: Analysis & Decision Making
│   ├── __init__.py
│   ├── analyzer.py        # Main LLM analysis logic
│   ├── prompts.py         # Prompt templates (versioned)
│   ├── decision_doc.py    # Decision documentation generation
│   ├── hallucination.py   # Anti-hallucination checks
│   └── output_schema.py   # Structured output definitions
├── workflows/             # Part VII: Workflow orchestration
│   ├── __init__.py
│   ├── one_shot.py        # Workflow A (single LLM call, zero infrastructure)
│   ├── research_first.py  # Workflow B
│   ├── classic.py         # Workflow C
│   ├── multi_agent.py     # Workflow D (LangGraph)
│   └── mandate_agent.py   # Workflow E (mandate-driven autonomous agent)
├── optimization/          # Parts VIII & IX
│   ├── __init__.py
│   ├── review_docs.py     # Review document generation
│   ├── experiment.py      # Experiment tracking
│   ├── counterfactual.py  # Counterfactual analysis engine
│   ├── staleness.py       # Parameter staleness detection
│   ├── drift.py           # Drift detection
│   ├── shadow.py          # Shadow mode testing
│   ├── decision_audit.py  # Decision quality metrics
│   └── rollout.py         # Automated parameter rollout
├── common/                # Shared utilities
│   ├── __init__.py
│   ├── config.py          # Centralized configuration
│   ├── logging.py         # Structured logging
│   ├── models.py          # Shared Pydantic models
│   └── retry.py           # Retry/backoff utilities
└── main.py                # Entry point, scheduling
tests/
├── unit/                  # Fast, isolated tests
│   ├── test_dedup.py
│   ├── test_relevance.py
│   ├── test_schema.py
│   ├── test_hallucination.py
│   ├── test_screener.py
│   └── ...
├── integration/           # Tests with real (or mocked) APIs
│   ├── test_retrieval_sources.py
│   ├── test_vector_store.py
│   ├── test_analysis_pipeline.py
│   └── ...
└── conftest.py            # Shared fixtures
```

**Key design principles:**

- **Each module has a clear interface** (defined via Pydantic models or abstract base classes). Modules communicate through data, not through shared mutable state.
- **Configuration is centralized** in a single config file (YAML/TOML) or environment variables. No hardcoded API keys, thresholds, or model names in module code.
- **Each retrieval source is a separate file** behind a common interface. Adding a new source means adding one file and registering it — no changes to the orchestrator logic.
- **Decision documentation is part of the analysis module**, not an afterthought. The `decision_doc.py` and `hallucination.py` modules are called as part of every analysis run.

### Testing Strategy

Testing an AI-powered pipeline requires a layered approach because different components have different testability characteristics.

**Layer 1: Unit tests (fast, deterministic, run on every commit)**

Test pure logic modules that don't depend on external APIs or LLMs:
- Deduplication algorithms (given two headlines, are they duplicates?)
- Relevance scoring logic (given a ticker list and an article, what's the score?)
- Schema validation (does a JSON blob conform to the Pydantic model?)
- Hallucination detection (given a claim and a fact, does the check pass?)
- Universe screening (given criteria and a stock, does it qualify?)
- Master allow-list filtering (given constraints, is this asset allowed?)
- Technical indicator computation (given price data, is the RSI correct?)

**Layer 2: Integration tests (slower, may hit real or mocked APIs)**

Test module boundaries:
- Retrieval source tests: Does the Alpha Vantage wrapper correctly parse the API response? (Use recorded/mocked responses for CI; real API for manual verification.)
- Vector store tests: Does embed → store → retrieve return the expected results?
- End-to-end pipeline tests: Given fixed input data, does the full pipeline produce structurally valid output?

**Layer 3: LLM output tests (non-deterministic, use statistical assertions)**

Testing LLM-dependent components requires different strategies:
- **Schema compliance:** Does the LLM output valid JSON matching the expected Pydantic model? (This is deterministic — either it parses or it doesn't.)
- **Smoke tests:** Given a known input, does the LLM produce *any* reasonable recommendation? (Not testing correctness, just that the pipeline doesn't crash.)
- **Regression tests:** Store "golden" LLM outputs from known-good runs. Flag (but don't fail) if new outputs deviate significantly. Use similarity metrics rather than exact matching.
- **Cost/latency guards:** Assert that LLM calls stay within expected token and time budgets.

**Testing tools:**

| Tool | Purpose |
|------|---------|
| **pytest** | Test runner (standard for Python) |
| **pytest-asyncio** | Testing async code |
| **pytest-cov** | Code coverage measurement |
| **pytest-mock / unittest.mock** | Mocking external APIs and LLM calls |
| **responses / respx** | HTTP request mocking for `requests` / `httpx` |
| **VCR.py / pytest-recording** | Record and replay HTTP interactions |
| **Hypothesis** | Property-based testing for data processing logic |
| **freezegun** | Time mocking (important for recency checks and TTL logic) |

### Test-Driven Development (TDD)

TDD (writing tests before implementation, following the Red-Green-Refactor cycle) has specific pros and cons in the context of AI-powered pipelines.

**Pros:**

| Advantage | Explanation |
|-----------|-------------|
| **Forces clear interfaces** | Writing tests first requires you to define inputs and outputs before implementation. This naturally produces the modular architecture described above. |
| **Catches regressions early** | When tuning prompts or changing parameters, existing tests immediately flag if something breaks. |
| **Documents behavior** | Tests serve as executable documentation of what each module is supposed to do. |
| **Pairs well with AI coding assistants** | In 2025-2026, AI coding tools (Cursor, Copilot) can generate implementation from test specifications, making TDD faster than ever. The tests serve as "cognitive scaffolding" that constrains and improves LLM-generated code. |
| **Builds confidence for refactoring** | With comprehensive tests, you can safely restructure modules, upgrade libraries, or swap implementations. |

**Cons / Challenges:**

| Challenge | Explanation |
|-----------|-------------|
| **Non-deterministic LLM outputs** | You cannot write a traditional assertion like `assert result == expected_output` for LLM responses. Need statistical assertions, schema checks, and smoke tests instead. |
| **Rapidly evolving interfaces** | During early prototyping, module interfaces change frequently. Maintaining tests for unstable interfaces creates friction. |
| **Mocking complexity** | Testing modules that depend on multiple external APIs requires extensive mocking setup, which can become brittle. |
| **Diminishing returns for prompt engineering** | Writing tests for prompt quality is inherently subjective. TDD works well for structured logic but poorly for creative optimization. |
| **Overhead in exploration phase** | When experimenting with new data sources or models, strict TDD can slow down rapid iteration. |

**Recommended approach — Pragmatic TDD:**

1. **Use strict TDD for:** Data processing modules (dedup, filtering, schema validation, hallucination checks, screeners), configuration management, utility functions. These are deterministic and benefit most from test-first design.
2. **Use test-after for:** LLM integration modules, prompt templates, retrieval orchestration. Write implementation first, then add regression tests once the interface stabilizes.
3. **Use contract tests for:** Module boundaries. Define the Pydantic schemas (contracts) first, then both the producer and consumer can be developed and tested independently.
4. **Skip unit tests for:** Exploratory prototyping code that will be rewritten. Don't invest in tests for throwaway experiments.

### Architectural Guides & Coding Conventions

Consistent conventions reduce friction, improve readability, and make AI-assisted coding (Cursor, Copilot) more effective.

**Foundational standards:**

| Standard | Description | Enforcement |
|----------|-------------|-------------|
| **PEP 8** | Python style guide (naming, indentation, line length, whitespace) | Enforced via Ruff |
| **PEP 257** | Docstring conventions | Enforced via Ruff (D rules) |
| **PEP 621** | Project metadata in `pyproject.toml` | Use `pyproject.toml` instead of `setup.py` |
| **PEP 484 / 526** | Type annotations | Enforced via mypy |

**Recommended toolchain (proven in production):**

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Linting + formatting (replaces flake8, isort, black, pylint) | `pyproject.toml` — fast, all-in-one. Set `target-version = "py312"`. |
| **mypy** | Static type checking | `pyproject.toml` — use `strict = true` for new code. Gradual adoption for existing code via `--follow-imports=skip`. |
| **pre-commit** | Git hook manager for automated checks | `.pre-commit-config.yaml` — runs Ruff + mypy + pytest on every commit |
| **pytest** | Test runner | `pyproject.toml` — configure test paths, markers, coverage thresholds |
| **uv** | Fast Python package manager (replaces pip/poetry for speed) | `pyproject.toml` — deterministic lockfile, fast installs. Alternative: **Poetry** for broader ecosystem support. |

**Project configuration (single `pyproject.toml`):**

```toml
[project]
name = "portfolio-optimizer"
version = "0.1.0"
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "D", "UP", "ANN", "S", "B", "A", "C4", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests requiring API access",
    "llm: marks tests that call real LLM APIs",
]
```

**Architectural patterns that work well for this project:**

| Pattern | Where to Apply | Why |
|---------|---------------|-----|
| **Repository pattern** | Data access (retrieval sources, vector DB, portfolio storage) | Abstracts storage behind interfaces; easy to swap implementations or mock for testing |
| **Strategy pattern** | Configurable algorithms (chunking strategy, sentiment model, embedding model) | Each strategy is a class implementing a common interface; selected via configuration |
| **Pipeline / Chain of Responsibility** | The main data flow (Parts II → VI) | Each step receives input, produces output + review doc, passes to next step |
| **Observer / Event pattern** | Review document collection, alerting | Steps emit review documents; the optimization framework subscribes to them |
| **Factory pattern** | Creating retrieval sources, LLM clients | Instantiate the right class based on configuration without hardcoding |

**Cursor / AI assistant integration:**

- Maintain a `.cursor/rules/` directory with project-specific conventions (e.g. "always use Pydantic v2 models for data classes", "always log structured JSON", "always include type annotations").
- Keep prompt templates in versioned files (not inline strings) so AI assistants can navigate and modify them.
- Use clear, descriptive function and variable names — AI assistants produce significantly better code when the surrounding context is self-documenting.

### Additional Guardrails

Beyond code quality tools, consider these operational guardrails:

**Dependency management:**
- Pin all dependency versions in a lockfile (`uv.lock` or `poetry.lock`). Never use floating version ranges in production.
- Run `pip-audit` or `safety` in CI to detect known vulnerabilities in dependencies.
- Update dependencies on a monthly cadence; test thoroughly before deploying updates.

**Secrets management:**
- Never commit API keys, tokens, or credentials to version control.
- Use environment variables (loaded via `python-dotenv`) for local development.
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, or GitHub Actions secrets) for CI/CD and production.
- Rotate API keys periodically, especially for paid services.

**CI/CD pipeline:**

```
Push to branch
    │
    ▼
┌────────────────────┐
│  1. Ruff lint       │ ← Fast: ~2 seconds
│  2. mypy type check │ ← Fast: ~5 seconds
│  3. Unit tests      │ ← Fast: ~10 seconds
│  4. Integration     │ ← Slower: ~60 seconds (mocked APIs)
│     tests           │
│  5. Coverage check  │ ← Fail if < 80% for core modules
└────────┬───────────┘
         │ all pass
         ▼
┌────────────────────┐
│  Merge to main     │
│  → Deploy to       │
│    staging          │
│  → Run smoke tests │
│    with real APIs   │
└────────────────────┘
```

**Logging and observability:**
- Use structured logging (`structlog` or Python's `logging` with JSON formatter). Every log entry should include `run_id`, `step`, and `timestamp`.
- Send logs to a centralized system (e.g. ELK stack, Grafana Loki, or simply structured JSON files).
- LangSmith handles LLM-specific tracing; structured logging handles everything else.

**Error handling:**
- Use `tenacity` for retry logic on all external API calls. Configure per-source retry policies (some APIs are flaky, others are not).
- Implement circuit breakers: if a source fails repeatedly, temporarily disable it and use fallback sources.
- Every error should be logged in the step's review document. Pipeline runs should never silently swallow errors.

**Rate limiting and cost control:**
- Track API call counts and costs per run. Include in review documents.
- Set hard monthly budget limits for paid APIs and LLM usage.
- Implement request throttling (e.g. via `asyncio.Semaphore`) to stay within rate limits.
- Use cheaper models for high-volume tasks (pre-filtering, embedding) and expensive models only for the final analysis.

---

## Appendix C: Implementation Resources & Reference Materials

Before beginning a detailed implementation, the following collection of GitHub repositories, frameworks, tutorials, and methodologies **must** be reviewed and considered. Each resource covers topics directly relevant to one or more parts of the portfolio optimization pipeline described in this document. The goal is to extract patterns, code examples, architectural decisions, library usage patterns, workflow definitions, and best practices that can accelerate and improve the implementation.

> **Important:** Before the implementation phase starts, a set of **reference markdown files** should be created (one per resource or topic area) summarizing the key takeaways, applicable patterns, code snippets, and integration points relevant to *this* project. These reference files become part of the project knowledge base and should be consulted during sprint planning and story implementation.

### Primary Resources (User-Provided)

The following resources were explicitly identified as important for the implementation:

#### 1. BMAD-METHOD — Agile AI-Driven Development Framework

- **URL:** <https://github.com/bmad-code-org/BMAD-METHOD>
- **Stars:** ~34.6k | **License:** MIT
- **Relevance:** Provides a complete AI-driven agile development methodology with 21+ specialized agents, 50+ guided workflows, and scale-adaptive intelligence. Directly applicable to how we plan, architect, and implement the portfolio optimization system.
- **Key takeaways to extract:**
  - Structured workflows for product briefs, PRDs, architecture creation, epic/story creation, sprint planning
  - Agent-based development patterns (PM, Architect, Developer, UX, Scrum Master agents)
  - Scale-domain-adaptive planning approaches
  - The "Quick Flow" (quick-spec → dev-story → code-review) for smaller features
  - The "Full Planning Path" for complex features
- **Applicable to:** Overall project management, sprint planning, story creation, code review processes

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **GitHub Spec Kit** | [github/spec-kit](https://github.com/github/spec-kit) | Tool-agnostic (works with Copilot, Claude, Cursor, Gemini CLI); lightweight slash-command interface (`/speckit.specify`, `/speckit.plan`); backed by GitHub; good for greenfield projects; minimal setup | Less comprehensive than BMAD (no specialized agent roles); no built-in multi-repo support; younger project; limited to spec generation (no QA, Scrum Master, UX agents) |
| **OpenSpec** | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | ~22k stars; lightweight "Propose → Apply → Archive" cycle; delta specs track changes cleanly; unified evolving spec as source of truth; supports 20+ AI tools; fast iteration | Less structured than BMAD (no predefined agent workflows); no full agile simulation (no sprint planning, retrospective); workspace/multi-repo support still upcoming |

**Decision guidance:** Choose **BMAD-METHOD** for complex, multi-repo projects that benefit from simulated team roles and full agile ceremony coverage. Choose **GitHub Spec Kit** for simpler greenfield projects where you want minimal overhead and already use GitHub Copilot. Choose **OpenSpec** for a middle ground — more structure than Spec Kit but less ceremony than BMAD, with strong change-tracking via delta specs.

#### 2. Jinja — Template Engine

- **URL:** <https://github.com/pallets/jinja>
- **Stars:** ~11.4k | **License:** BSD-3-Clause
- **Relevance:** A fast, expressive, extensible templating engine. Useful for generating structured prompts, report templates, review documents, and notification messages within the pipeline.
- **Key takeaways to extract:**
  - Template inheritance and inclusion patterns
  - Macro definitions for reusable prompt components
  - Autoescaping for safe output generation
  - Sandboxed environment for safe rendering of user-influenced templates
  - Template compilation and caching strategies
- **Applicable to:** Prompt engineering (structured prompt templates), review document generation (Part VIII), notification/reporting systems

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **Mako** | [sqlalchemy/mako](https://github.com/sqlalchemy/mako) | One of the fastest pure-Python template engines; supports dynamic inheritance; allows embedded Python logic directly in templates; good for complex template logic | "PHP-like" — less separation of concerns; template debugging can be harder; smaller community than Jinja; less IDE/tooling support |
| **Chameleon** | [malthe/chameleon](https://github.com/nicfit/chameleon) | Very fast HTML/XML template engine; TAL-based (Template Attribute Language); good for XML-heavy output | XML-centric (less suitable for plain-text prompts); smaller community; less documentation; not ideal for non-HTML templates |
| **Python f-strings / `string.Template`** | Built-in | Zero dependencies; simple and readable for short templates; no learning curve; part of Python stdlib | No inheritance, macros, filters, or loops; poor for complex, reusable prompt templates; no sandboxing; doesn't scale for large template libraries |

**Decision guidance:** **Jinja** is the clear winner for this project. It dominates the Python ecosystem (~60% community preference), has excellent integration with LangChain (which uses it internally), offers sandboxing for safety, and provides the inheritance/macro system needed for a library of reusable prompt templates. Use Mako only if you need embedded Python logic in templates. Use f-strings only for trivial, one-off string interpolation.

#### 3. Deep Agents (LangChain) — Agent Harness

- **URL:** <https://github.com/langchain-ai/deepagents>
- **Stars:** ~9k | **License:** MIT
- **Relevance:** Batteries-included agent harness built on LangChain and LangGraph. Provides planning tools, filesystem backend, sub-agent spawning, and context management — directly applicable to our multi-agent architecture.
- **Key takeaways to extract:**
  - Planning tools (`write_todos` / `read_todos`) for task breakdown and progress tracking
  - Filesystem tools (`read_file`, `write_file`, `edit_file`, `ls`, `glob`, `grep`) for context management
  - Sub-agent spawning and delegation patterns (`task` tool)
  - Auto-summarization for long conversations
  - Smart defaults for teaching models how to use tools effectively
  - MCP integration via `langchain-mcp-adapters`
- **Applicable to:** Multi-Agent Architecture (Part VII — Workflow D), agent orchestration, context management, sub-agent delegation patterns

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **Agno** | [agno-agi/agno](https://github.com/agno-agi/agno) | High-performance multi-agent runtime; built-in session management and MCP tool support; supports text, images, audio, video; many out-of-the-box features | More setup required than simpler alternatives; newer project with smaller community; not built on LangChain (separate ecosystem) |
| **PydanticAI** | [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | Type-safe tool contracts with Pydantic models; structured I/O validation; excellent for ensuring reliable structured outputs; familiar if using Pydantic already | Narrower scope (type-safe agent tooling, not a full harness); less built-in planning/delegation; newer project |
| **smolagents (HuggingFace)** | [huggingface/smolagents](https://github.com/huggingface/smolagents) | Ultra-minimal (<1k lines core); agents write and execute Python code to use tools; works with any LLM; simple API; secure sandboxing | Minimal built-in features (no planning tools, no filesystem backend, no sub-agents); code-execution approach may need extra safety measures; less production-oriented |
| **OpenAI Agents SDK** | [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | Native OpenAI integration; built-in web search, file search, computer use tools; handoff patterns for multi-agent; guardrails | Locked to OpenAI models; vendor lock-in; less flexible for multi-provider setups; relatively new |

**Decision guidance:** **Deep Agents** is the best fit if you're already committed to the LangChain/LangGraph ecosystem (which this project is). It provides the richest built-in harness (planning, filesystem, sub-agents, MCP) on top of LangGraph. Consider **Agno** if you need high-performance multi-modal agents outside the LangChain ecosystem. Consider **PydanticAI** as a complementary tool for type-safe structured outputs regardless of which harness you choose. Use **smolagents** only for lightweight prototyping.

#### 4. Prompt Engineering Techniques

- **URL:** <https://github.com/NirDiamant/Prompt_Engineering>
- **Stars:** ~7.1k | **License:** Custom non-commercial
- **Relevance:** Comprehensive collection of prompt engineering tutorials from fundamental to advanced. Essential for designing the structured prompts used in our AI analysis pipeline.
- **Key takeaways to extract:**
  - Zero-shot and few-shot prompting techniques
  - Chain of Thought (CoT) prompting for step-by-step reasoning
  - Self-consistency and multiple reasoning paths
  - Constrained and guided generation for structured outputs
  - Role prompting for specialized agent personas
  - Task decomposition patterns
  - Prompt chaining and sequencing
  - Prompt optimization techniques (A/B testing, iterative refinement)
  - Prompt security and safety (injection prevention)
- **Applicable to:** Part VI (AI-Powered Analysis & Decision Making), prompt template design, anti-hallucination strategies

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **DAIR.AI Prompt Engineering Guide** | [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | ~70k stars (10x larger community); comprehensive web version at promptingguide.ai; covers papers, research, and academic foundations; self-paced courses via DAIR.AI Academy; regularly updated with latest techniques | More academic/theoretical; fewer hands-on Jupyter notebooks; broader scope may require more filtering for relevant techniques |
| **Anthropic Prompt Engineering Tutorial** | [anthropics/prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | ~30k stars; 9 structured chapters with exercises; official vendor tutorial with deep model-specific insights; excellent for learning Claude-specific prompting; interactive format | Claude-specific (techniques may not transfer 1:1 to GPT-4o or Gemini); narrower scope; less coverage of advanced multi-agent prompt patterns |
| **LearnPrompt (learnprompting.org)** | [LearnPrompt/LP](https://github.com/LearnPrompt/LP) | Community-driven; web-based guide format; active Discord community; covers fundamentals through advanced topics | Less code-oriented; fewer runnable notebooks; more introductory level |

**Decision guidance:** Use **NirDiamant's Prompt_Engineering** as the primary hands-on resource (Jupyter notebooks, directly runnable). Supplement with **DAIR.AI's guide** for theoretical depth and the latest research papers. Use the **Anthropic tutorial** specifically when optimizing prompts for Claude models. All three are complementary rather than mutually exclusive.

#### 5. RAG — Retrieval-Augmented Generation (Techniques & Implementation)

RAG is the core mechanism our pipeline uses to feed relevant news, financial data, and historical context to LLMs for analysis. This combined entry covers both *foundational implementation* (how to build a RAG pipeline from scratch) and *advanced techniques* (how to optimize it).

**Primary resource — Advanced Techniques Catalog:**

- **URL:** <https://github.com/NirDiamant/RAG_Techniques>
- **Stars:** ~24.6k | **License:** Custom non-commercial
- **Relevance:** Comprehensive collection of 30+ advanced RAG techniques with runnable scripts. The primary reference for optimizing our RAG pipeline once the basics are in place.
- **Key takeaways to extract:**
  - Foundational RAG patterns (basic RAG, reliable RAG, chunk size optimization)
  - Query enhancement techniques (query transformations, HyDE approach)
  - Context enrichment (contextual chunk headers, semantic chunking, contextual compression)
  - Advanced retrieval methods (fusion retrieval, intelligent reranking, multi-faceted filtering, hierarchical indices)
  - Iterative and adaptive retrieval techniques
  - Evaluation frameworks (DeepEval, GroUSE)
  - Advanced architectures (Graph RAG, RAPTOR, Self-RAG, Corrective RAG)
  - Explainable retrieval for transparency

**Starting point — RAG from Scratch (LangChain):**

- **URL:** <https://github.com/langchain-ai/rag-from-scratch/blob/main/rag_from_scratch_1_to_4.ipynb>
- **Relevance:** Step-by-step notebook building a RAG pipeline from zero using LangChain — the recommended *first* resource to work through before diving into the advanced techniques above.
- **Key takeaways to extract:**
  - Document loading with `WebBaseLoader`
  - Text splitting with `RecursiveCharacterTextSplitter` (chunk size, chunk overlap)
  - Embedding with `OpenAIEmbeddings`
  - Vector store setup with `Chroma`
  - Retriever configuration (`as_retriever`, search kwargs)
  - Prompt template design for RAG (`rlm/rag-prompt`)
  - RAG chain composition using LCEL (`RunnablePassthrough | prompt | llm | StrOutputParser`)
  - Token counting with `tiktoken`
  - Cosine similarity for document relevance

**Recommended learning path:** Work through *RAG from Scratch* first to understand the fundamentals and get a working LangChain-based RAG pipeline. Then use *RAG Techniques* as a catalog of optimizations to apply incrementally — starting with chunk size tuning and semantic chunking, progressing to fusion retrieval and reranking, and eventually evaluating advanced architectures like Graph RAG or Self-RAG.

- **Applicable to:** Part IV (Data Preparation for AI), Part VI (AI-Powered Analysis), vector database strategies, embedding optimization, implementation of the RAG pipeline core

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **LlamaIndex "Build a RAG" Tutorial** | [docs.llamaindex.ai](https://docs.llamaindex.ai/en/stable/understanding/) | Step-by-step official docs; production-oriented; covers advanced patterns (agents, structured data, evaluation); strong data connector ecosystem; real-world SEC filings example available via Mistral Cookbook | LlamaIndex-specific (not LangChain); would introduce a second framework; different API conventions |
| **Awesome RAG** | [Poll-The-People/awesome-rag](https://github.com/Poll-The-People/awesome-rag) | Curated link collection; broad coverage of RAG ecosystem; good for discovering new tools and papers | Links only (no runnable code); smaller community (~175 stars); may contain stale links |
| **LangChain RAG Benchmarks** | [langchain-ai/langchain-benchmarks](https://langchain-ai.github.io/langchain-benchmarks/notebooks/retrieval/comparing_techniques.html) | Quantitative comparison of RAG architectures; benchmark datasets for evaluation; configurable factory functions for testing | Narrower focus (benchmarking, not teaching); requires existing RAG knowledge; LangChain-specific |
| **Haystack RAG Tutorial** | [deepset-ai/haystack](https://haystack.deepset.ai/tutorials) | Pipeline-based architecture; strong for search use cases; well-documented; good for comparison with LangChain approach | Haystack-specific; smaller community than LangChain; would introduce yet another framework |

**Decision guidance:** Use the two primary resources together (RAG from Scratch → RAG Techniques) as they cover the same topic at complementary depths within our chosen LangChain stack. Supplement with **LangChain Benchmarks** for quantitative evaluation of your chosen RAG architecture. Review **LlamaIndex's tutorial** to compare its data connector approach — if its financial data ingestion proves superior, a hybrid approach is possible. The Mistral Cookbook's SEC filings example is worth reviewing for its direct relevance to financial document processing.

#### 6. Agents Towards Production

- **URL:** <https://github.com/NirDiamant/agents-towards-production>
- **Stars:** ~17.2k | **License:** Custom non-commercial
- **Relevance:** End-to-end tutorials covering every layer of production-grade GenAI agents. Directly applicable to deploying our portfolio optimization agent in production.
- **Key takeaways to extract:**
  - Stateful agent workflows with LangGraph
  - Agent memory (dual-memory, semantic search, persistent state) — e.g., Redis, Mem0
  - Secure tool calling (OAuth2, human-in-the-loop safety controls)
  - Web data collection and real-time integration (Tavily, Bright Data)
  - Production-ready RAG with automated evaluation
  - Agent deployment patterns (Docker, FastAPI, on-prem LLM)
  - Agent tracing & debugging with LangSmith
  - Agent evaluation and behavioral analysis
  - Agent security (prompt injection, behavior alignment, tool access control)
  - Multi-agent communication (A2A Protocol)
  - Fine-tuning agents for domain expertise
  - GPU deployment for scalability
- **Applicable to:** All Parts, especially Part VII (Workflows), Part VIII (Evaluation & Optimization), Part IX (Self-Optimization), Appendix B (Implementation Guide)

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **Microsoft Agent Framework** | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Combines Semantic Kernel + AutoGen concepts; supports Python and .NET; enterprise-grade with Microsoft backing; strong Azure integration; well-documented | Microsoft/Azure-centric; heavier framework; may be overkill for Python-only projects; less community-driven |
| **LangGraph Documentation & Tutorials** | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Official tutorials for the runtime we're likely using; production-focused with deployment guides; time-travel debugging (LangGraph Studio); Agent Protocol support | Narrower scope (LangGraph-specific, not general production patterns); vendor-specific; tutorials may assume LangChain familiarity |
| **Phidata (now Agno)** | [agno-agi/agno](https://github.com/agno-agi/agno) | Production-oriented agent framework with built-in monitoring; Docker-based deployment; memory and knowledge base integration; fast iteration | Smaller community than LangChain ecosystem; framework migration (Phidata → Agno) may cause documentation gaps |

**Decision guidance:** **NirDiamant's Agents Towards Production** is uniquely comprehensive — it covers the full stack from development to deployment with vendor-neutral tutorials. Use it as the primary reference for production patterns. Supplement with **LangGraph's official docs** for runtime-specific deployment guidance, and review the **Microsoft Agent Framework** if enterprise Azure integration becomes relevant.

#### 7. GenAI Agents

- **URL:** <https://github.com/NirDiamant/GenAI_Agents>
- **Stars:** ~19.8k | **License:** Custom non-commercial
- **Relevance:** Comprehensive guide for building intelligent, interactive AI systems — from simple conversational agents to complex multi-agent systems.
- **Key takeaways to extract:**
  - Simple data analysis agent patterns
  - Memory-enhanced conversational agents (short-term + long-term memory)
  - Multi-agent collaboration systems
  - Self-improving agent patterns
  - LangGraph tutorial (modular AI workflows, state management)
  - Internet search and summarize agents
  - News summarization agents (TL;DR patterns)
  - Research team agents (multi-agent research collaboration)
  - Self-healing codebase patterns
- **Applicable to:** Part VI (AI Analysis), Part VII (Multi-Agent Architecture), Part IX (Self-Optimization), agent design patterns

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **CrewAI Examples** | [crewAIInc/crewAI-examples](https://github.com/crewAIInc/crewAI-examples) | Practical multi-agent examples with role-playing crews; covers research teams, content creation, financial analysis; easy-to-understand role/task/crew abstraction | CrewAI-specific (not LangGraph); fewer agent types covered; less focus on self-improving patterns; proprietary cloud features |
| **LangChain Templates & Cookbooks** | [langchain-ai/langchain](https://github.com/langchain-ai/langchain/tree/master/cookbook) | Official LangChain cookbook with production patterns; directly compatible with our chosen stack; covers tool use, agents, RAG, structured output | Scattered across the repo (harder to navigate); some examples may be outdated due to rapid LangChain evolution; less tutorial-style narrative |
| **AutoGen Examples** | [microsoft/autogen](https://github.com/microsoft/autogen/tree/main/python/samples) | Strong multi-agent dialogue examples; human-in-the-loop patterns; group chat coordination; event-driven architecture | AutoGen-specific; different paradigm (conversation-based vs. graph-based); steeper learning curve; Microsoft ecosystem |

**Decision guidance:** **NirDiamant's GenAI_Agents** offers the broadest variety of agent patterns in a tutorial format — from simple to complex multi-agent systems. Use it as an agent pattern catalog. Supplement with **CrewAI Examples** for role-based multi-agent inspiration and the **LangChain Cookbook** for stack-compatible implementation patterns.

#### 8. n8n — Workflow Automation & AI Agent Platform

- **URL:** <https://github.com/n8n-io/n8n>
- **Stars:** ~173k | **License:** Sustainable Use License (fair-code, source-available, self-hostable)
- **Relevance:** A powerful, self-hostable workflow automation platform with 500+ integrations and native AI agent capabilities built on LangChain. Directly applicable as an orchestration layer for our portfolio optimization pipeline — connecting data sources, scheduling runs, managing human-in-the-loop approvals, and building visual AI agent workflows.
- **Key takeaways to extract:**
  - Visual workflow builder for rapid prototyping of pipeline steps
  - Native AI agent nodes (chat agents, RAG agents, planning agents, multi-agent systems)
  - LangChain integration for AI workflows
  - 500+ pre-built integrations (Slack, email, databases, APIs, webhooks)
  - Human-in-the-loop guardrails for AI agent safety
  - Self-hosting for data sovereignty (critical for financial data)
  - Webhook triggers for event-driven pipeline execution
  - Error handling, retry logic, and workflow monitoring built-in
  - SOC2 compliance support
  - JavaScript and Python custom code nodes for complex logic
  - Community template library (600+ AI workflow templates)
- **Applicable to:** Part VII (Workflow Orchestration), Part VIII (Evaluation — notification and review triggers), Part IX (Self-Optimization — scheduled parameter evaluation), scheduling and integration layer

**Relationship to LangGraph, Deep Agents, and LangSmith — Complementary, Not Competing:**

A common question is whether n8n duplicates or conflicts with the other tools in this document. The short answer: **no — these tools operate at different layers of the stack and are designed to be used together.** Here is how each layer works and why combining them is not only reasonable but recommended:

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: OBSERVABILITY                                         │
│  LangSmith — traces, debugs, and evaluates everything below     │
│  (reads data; does NOT execute anything)                        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: OUTER ORCHESTRATION                                   │
│  n8n — schedules runs, triggers on events, connects external    │
│  services, manages human-in-the-loop, routes outputs            │
│  (the "when", "what triggers", and "what happens after")        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: AGENT HARNESS                                         │
│  Deep Agents — planning tools, filesystem access, sub-agent     │
│  delegation, context management, auto-summarization             │
│  (the "how the agent works internally")                         │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: AGENT RUNTIME                                         │
│  LangGraph — state machines, tool calling, branching, cycles,   │
│  memory, checkpointing                                          │
│  (the "state machine that drives the agent")                    │
└─────────────────────────────────────────────────────────────────┘
```

**Layer-by-layer analysis:**

| Tool | Layer | Role | Overlap with n8n? |
|---|---|---|---|
| **LangGraph** | Agent runtime | Manages the internal state machine of an AI agent: which tools to call, how to branch, when to loop, how to checkpoint state. This is the *inner* logic of a single agent run. | **No overlap.** n8n triggers *when* a LangGraph agent runs and *what happens with its output*. LangGraph controls *what the agent does internally*. n8n can call a LangGraph agent via HTTP/webhook, then route the result to Slack, a database, or a review queue. |
| **Deep Agents** | Agent harness | Adds high-level capabilities *on top of* LangGraph: planning (todo lists), filesystem I/O, sub-agent spawning, MCP integration. Think of it as the "toolbox" the agent uses during execution. | **Minimal overlap.** n8n's AI agent nodes offer *visual* agent building, while Deep Agents provides *code-level* agent harness capabilities. For this project, the portfolio optimization agent logic should live in Deep Agents/LangGraph (Python, testable, version-controlled), while n8n handles scheduling, integration, and human review routing. n8n should *not* be used to implement the core analysis logic — that belongs in code. |
| **LangSmith** | Observability | Traces every LLM call, tool invocation, and agent step. Provides debugging, evaluation metrics, and dataset management. It is purely a *read/observe* layer — it does not execute anything. | **Zero overlap.** LangSmith traces what happens *inside* LangGraph/Deep Agents. n8n orchestrates what happens *outside*. Both run simultaneously. In fact, LangSmith traces will cover LLM calls made inside n8n's AI nodes too (if configured), giving you end-to-end visibility. |

**Recommended architecture for this project:**

```
                     ┌──────────────┐
                     │  LangSmith   │ ← traces everything
                     │ (observing)  │
                     └──────┬───────┘
                            │ traces
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────┐  triggers  ┌─────────────┐  outputs  ┌─────────┐
│  n8n    │ ─────────► │ LangGraph + │ ────────► │  n8n    │
│ (cron,  │  webhook/  │ Deep Agents │  JSON     │ (route  │
│ webhook,│  HTTP call │ (portfolio  │  result   │ results │
│ trigger)│            │  analysis)  │           │ to Slack│
└─────────┘            └─────────────┘           │ DB, email│
                                                  │ review  │
                                                  │ queue)  │
                                                  └─────────┘
```

**Concrete example — a daily portfolio optimization run:**

1. **n8n** fires a cron trigger at 08:00 every trading day.
2. **n8n** fetches the current portfolio state from the broker API and current prices from Yahoo Finance (using built-in integrations — no code needed).
3. **n8n** calls the Python-based portfolio optimization agent (running as a FastAPI endpoint or Docker container) via HTTP.
4. Inside that endpoint, **LangGraph** orchestrates the multi-step agent: news retrieval → evaluation → RAG lookup → AI analysis → decision generation.
5. **Deep Agents** provides the agent with planning tools (task breakdown), filesystem access (reading/writing review documents), and sub-agent delegation (research sub-agent, risk sub-agent).
6. **LangSmith** traces every LLM call, tool invocation, and state transition that happens in steps 4-5 — for debugging, evaluation, and optimization.
7. The agent returns a structured JSON result (decision records, confidence scores, recommended actions).
8. **n8n** receives the result and routes it: posts a summary to Slack, writes decision records to the database, sends a notification email if confidence is below threshold, and queues items for human review.
9. **n8n** triggers a separate review workflow if any hallucination risk was flagged.

**What n8n should NOT be used for:**

- Do **not** implement the core AI analysis logic (Part VI) inside n8n's visual AI nodes. The analysis involves complex state management, multi-step reasoning, structured output parsing, and anti-hallucination checks that require version-controlled, unit-tested Python code (LangGraph + Deep Agents).
- Do **not** use n8n as a replacement for LangSmith's tracing. n8n shows whether a workflow *ran* and what its inputs/outputs were, but it cannot trace individual LLM calls, token usage, latency per step, or intermediate reasoning — that is LangSmith's job.
- Do **not** build the self-optimization engine (Part IX) purely in n8n. The counterfactual analysis and parameter tuning logic requires Python (numpy, pandas, statistical analysis). n8n should *schedule* and *trigger* the optimization runs, not implement them.

**What n8n SHOULD be used for:**

- Scheduling: cron-based triggers for daily/weekly pipeline runs
- Integration glue: connecting broker APIs, notification services (Slack, email, Teams), databases, and review tools without writing boilerplate code
- Human-in-the-loop: routing decisions that need approval to a review queue, sending alerts when confidence is low or hallucination risk is high
- Monitoring dashboard triggers: sending alerts if a pipeline run fails, takes too long, or produces anomalous results
- Self-optimization triggers: scheduling the Part IX counterfactual analysis runs and routing optimization proposals for human review

> **Bottom line:** Using n8n alongside LangGraph, Deep Agents, and LangSmith is not just reasonable — it is the recommended architecture. Each tool covers a layer that the others do not. Removing any one of them would force you to re-implement its functionality from scratch (e.g., writing custom cron + webhook + Slack integration code instead of using n8n, or building your own tracing system instead of using LangSmith).

**Alternatives & Comparison:**

| Alternative | URL | Pros | Cons |
|---|---|---|---|
| **Make (Integromat)** | [make.com](https://www.make.com) | Powerful visual builder; good balance of power and accessibility; European data residency; upcoming Maia AI builder (natural language → workflow) | Cloud-only (no self-hosting); per-operation pricing (expensive for data-heavy loops); less code flexibility than n8n; no native LangChain integration |
| **Zapier** | [zapier.com](https://www.zapier.com) | 6,000+ integrations (largest ecosystem); excellent for non-technical users; Zapier Agents for AI automation | Cloud-only; most expensive at scale; limited custom code; per-task pricing; not suitable for complex AI agent loops; no self-hosting |
| **Temporal** | [temporalio/temporal](https://github.com/temporalio/temporal) | Durable execution (agents survive restarts); used by OpenAI for Codex; excellent for mission-critical long-running workflows; SDK for Python, Go, Java, TypeScript | Not visual (code-only); steeper learning curve; no built-in integrations (must code all connectors); infrastructure overhead; overkill for simpler workflows |
| **Apache Airflow** | [apache/airflow](https://github.com/apache/airflow) | Industry standard for data pipeline orchestration; massive community; excellent scheduling; DAG-based; strong monitoring | Heavy infrastructure; Python-only DAGs; designed for data pipelines (not AI agents); no visual builder for non-developers; complex setup |
| **Windmill** | [windmill-labs/windmill](https://github.com/windmill-labs/windmill) | Open-source workflow engine; supports Python, TypeScript, Go, SQL; self-hostable; fast; auto-generated UIs | Smaller community than n8n; fewer pre-built integrations; less AI-specific tooling; less mature ecosystem |
| **Prefect** | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | Python-native workflow orchestration; modern API; good observability; easy to adopt for Python developers; hybrid execution | Less visual than n8n; fewer pre-built integrations; more developer-focused; no native AI agent nodes |

**Decision guidance:** **n8n** is the strongest choice for this project because it combines visual workflow building, native AI/LangChain integration, self-hosting for financial data sovereignty, and 500+ integrations — all in one platform. Use **Temporal** additionally if you need durable execution guarantees for long-running agent workflows (e.g., multi-day research tasks that must survive restarts). Consider **Prefect** or **Airflow** if you prefer Python-native orchestration and already have infrastructure for them. **Make** and **Zapier** are unsuitable for this project due to cloud-only limitations and cost at scale.

### Additional Recommended Resources

The following repositories and projects cover similar or complementary topics and should also be reviewed:

#### Agent Orchestration Frameworks

| Resource | URL | Stars | Relevance |
|---|---|---|---|
| **LangGraph** | <https://github.com/langchain-ai/langgraph> | ~24k | Core orchestration framework for building stateful, multi-agent workflows. Primary candidate for Workflow D. |
| **LangChain** | <https://github.com/langchain-ai/langchain> | ~100k+ | Foundation library for LLM application development. Tools, chains, memory, and integrations. |
| **CrewAI** | <https://github.com/crewAIInc/crewAI> | ~43k | Alternative multi-agent orchestration framework with role-playing agents. Consider as alternative to LangGraph for multi-agent workflows. |
| **Microsoft AutoGen** | <https://github.com/microsoft/autogen> | ~40k+ | Multi-agent collaboration through dialogue. Strong multi-agent coordination with human-in-the-loop. |
| **Microsoft Semantic Kernel** | <https://github.com/microsoft/semantic-kernel> | ~22k+ | Enterprise-grade AI SDK (Python, C#, Java). Good for single-agent orchestration and plugin architecture. |
| **LlamaIndex** | <https://github.com/run-llama/llama_index> | ~38k+ | Data framework for LLM applications. Strong RAG, data connectors, and structured data extraction. Alternative/complement to LangChain for data-heavy pipelines. |
| **Haystack** | <https://github.com/deepset-ai/haystack> | ~18k+ | End-to-end NLP/LLM framework. Pipeline-based architecture for building search and RAG systems. |

#### Financial-Specific Resources

| Resource | URL | Relevance |
|---|---|---|
| **FinancialDatasets Toolkit (LangChain)** | <https://docs.langchain.com/oss/python/integrations/tools/financial_datasets> | LangChain integration for financial data (16,000+ tickers, 30+ years of data) |
| **yfinance** | <https://github.com/ranaroussi/yfinance> | Yahoo Finance API wrapper. Primary free data source for prices, fundamentals, and historical data. |
| **FinRL** | <https://github.com/AI4Finance-Foundation/FinRL> | Deep reinforcement learning framework for quantitative finance. Advanced portfolio optimization strategies. |
| **FinGPT** | <https://github.com/AI4Finance-Foundation/FinGPT> | Open-source financial LLM. Sentiment analysis, named entity recognition, and financial Q&A. |

#### Development & Testing Tools

| Resource | URL | Relevance |
|---|---|---|
| **LangSmith** | <https://smith.langchain.com> | Tracing, debugging, and evaluation platform for LLM applications (Part VIII, Part IX). |
| **DeepEval** | <https://github.com/confident-ai/deepeval> | LLM evaluation framework. Test correctness, faithfulness, and contextual relevancy of RAG systems. |
| **Ragas** | <https://github.com/explodinggradients/ragas> | Framework for evaluating RAG pipelines (faithfulness, answer relevancy, context recall). |
| **Pytest** | <https://github.com/pytest-dev/pytest> | Testing framework (see Appendix B for testing strategy details). |

### Pre-Implementation Reference File Strategy

Before starting detailed implementation planning, the following reference markdown files should be created in the project repository (e.g., under `docs/implementation-references/`):

| Reference File | Content | Primary Source(s) |
|---|---|---|
| `ref-agile-workflow.md` | BMAD-METHOD workflows, sprint planning patterns, agent-based development approach | BMAD-METHOD |
| `ref-prompt-engineering.md` | Prompt templates, CoT patterns, few-shot examples, structured output patterns applicable to financial analysis | Prompt_Engineering, RAG from Scratch |
| `ref-rag-architecture.md` | RAG patterns, chunking strategies, embedding choices, retrieval optimization, evaluation methods | RAG_Techniques, RAG from Scratch, LlamaIndex |
| `ref-agent-patterns.md` | Multi-agent design patterns, sub-agent delegation, memory management, state management | GenAI_Agents, Deep Agents, Agents Towards Production, LangGraph |
| `ref-production-deployment.md` | Deployment patterns, containerization, API design, security, monitoring, tracing | Agents Towards Production, LangSmith |
| `ref-testing-evaluation.md` | Test strategies for LLM systems, RAG evaluation metrics, agent behavioral testing | Agents Towards Production, DeepEval, Ragas, Pytest |
| `ref-template-engine.md` | Jinja2 patterns for prompt templates, report generation, review document templating | Jinja |
| `ref-financial-data.md` | Financial API integration patterns, data source comparison, real-time vs. delayed data strategies | yfinance, FinancialDatasets Toolkit, FinGPT, FinRL |
| `ref-alternative-frameworks.md` | Comparison of CrewAI, AutoGen, Semantic Kernel vs. LangGraph for our multi-agent architecture needs | CrewAI, AutoGen, Semantic Kernel, Haystack |
| `ref-workflow-automation.md` | n8n workflow patterns, visual AI agent building, integration strategies, scheduling, human-in-the-loop triggers; comparison with Temporal, Prefect, Airflow | n8n, Temporal, Prefect, Airflow |

**Process:**
1. For each resource, clone/review the repository and extract relevant patterns, code snippets, and architectural decisions.
2. Write the reference file with sections: *Summary*, *Applicable Patterns*, *Code Snippets*, *Integration Points*, *Trade-offs & Limitations*.
3. During sprint planning, reference the applicable markdown files when creating stories and technical specifications.
4. Update reference files as new versions of libraries are released or new resources are discovered.

> **Note:** The reference files are living documents. As the project evolves and new patterns emerge from the community, they should be updated. The resources listed here represent the state as of early 2026 — the AI/LLM ecosystem moves fast, and newer tools or techniques may supersede some of these by the time implementation begins.

---

## Legal & Compliance Considerations

When building an automated portfolio optimization pipeline, keep the following in mind:

- **Terms of Service:** Always review the ToS of each data source. Some prohibit redistribution, scraping, or use in automated trading systems. API-based access is generally safer than scraping.
- **Rate Limits:** Most free tiers impose rate limits (e.g. 5 requests/minute). Exceeding limits can result in temporary or permanent bans. Implement backoff/retry logic.
- **Data Redistribution:** If your system stores or forwards news content, check whether the license permits redistribution. Many APIs allow internal analysis but prohibit republishing.
- **Financial Advice Disclaimer:** If any output from the agent is shared with others, include disclaimers that automated analysis does not constitute financial advice.
- **Market Data Regulations:** Real-time exchange data may require exchange agreements (e.g. NYSE, Nasdaq). Delayed data (15+ minutes) is typically unrestricted.

---

## Conclusion

Portfolio optimization with AI is a multi-stage problem that goes well beyond news retrieval. The key to success lies in building a pipeline that:

1. **Defines the investment universe** — dynamically maintains the set of candidate assets, constrained by an optional master allow-list (Part I)
2. **Retrieves** data efficiently from the right sources (Part II)
3. **Evaluates** and filters noise before it reaches expensive models (Part III)
4. **Prepares** data in AI-optimized formats using embeddings and structured schemas (Part IV)
5. **Contextualizes** news against the actual portfolio, prices, and fundamentals (Part V)
6. **Analyzes** with well-engineered prompts and structured outputs, with every decision documented and verified against factual data (Part VI)
7. **Orchestrates** these steps in a reliable, monitorable workflow (Part VII)
8. **Evaluates and optimizes** itself through systematic review, experiment tracking, and feedback loops (Part VIII)
9. **Self-optimizes** continuously through counterfactual analysis, staleness detection, shadow testing, and automated parameter rollout (Part IX)

Points 8 and 9 are what separate a prototype from a production system. Part VIII ensures humans can understand and deliberately improve the pipeline. Part IX ensures the pipeline does not silently degrade when no one is looking — it actively seeks better configurations and adapts to changing market conditions. **Decision documentation** (Part VI) is the connective tissue — every AI-generated recommendation is auditable, traceable to specific evidence, and verified against hallucination-prone claims.

Part VII offers five workflows (A through E) ordered so that each step builds on the components of the previous one. Workflow E has two implementation levels — Level 1 slots in early (after B), Level 2 comes last (after D). See Part VII for full details.

**Recommended build order (step-by-step, each builds on the previous):**

| Step | Workflow | What you build | Components reused | Components added |
|---|---|---|---|---|
| 0 | **Prepare** | Review Appendix C resources; create reference markdown files | — | Project knowledge base |
| 1 | **A (One-Shot)** | A prompt and an API call. Zero infrastructure. | — | Prompt crafting experience |
| 2 | **B (Research API-First)** | Programmatic pipeline with research API + quantitative data | Prompt insights from A | Research API wrapper, portfolio context module, LLM analysis, output schema, decision docs |
| 3 | **E Level 1 (Simple Mandate)** | Mandate document + simple agent using B's tools | All of B's components | Mandate document format, mandate parser, simple tool-use agent loop |
| 4 | **C (Classic Pipeline)** | Full pipeline with explicit retrieval, filtering, embedding, vector DB | Portfolio context, LLM analysis, output schema from B | News retrieval modules, pre-filter/dedup, embedding pipeline, vector DB |
| 5 | **D (Multi-Agent)** | Specialized agents orchestrated by LangGraph | All of C's pipeline modules (become agent tools) | LangGraph orchestration, agent wrappers, parallel execution |
| 6 | **E Level 2 (Full Mandate)** | Full agent with D's multi-agent internals + LangSmith tracing | D's agent infrastructure + E Level 1's mandate format | Deep Agents harness, LangSmith integration, anti-hallucination cross-checks |

**When to add evaluation & optimization:**
- **Part VIII (Evaluation):** Start generating review documents and decision records from Step 2 onward — even if nobody reads them initially. Add LangSmith and structured cadence once Workflow B stabilizes.
- **Part IX (Self-Optimization):** Layer in counterfactual engine, shadow mode, and automated parameter rollout once you have 30+ runs with market outcomes recorded. For E Level 1, self-optimization targets the mandate document; for the pipeline path, it targets per-step parameters.

**Steps 3 and 4–5 can run in parallel:** After Workflow B, the mandate path (E Level 1) and the pipeline path (C→D) are independent tracks that share B's components. You can pursue both simultaneously and compare results. They converge at E Level 2, which combines the mandate-driven interface with the full multi-agent infrastructure.

**You do not need to implement all steps.** Each step is independently useful. Many projects will stop at Step 2 or 3 and never need the full pipeline or multi-agent architecture. Advance only when you encounter limitations that the current workflow cannot address.

**From day one, generate review documents and decision records** — even if nobody reads them initially. They are the foundation that both Part VIII and Part IX build on. Without them, neither human review nor autonomous optimization is possible.

**Practical recommendation:** Use an online research LLM (Perplexity, Exa, YOU.com, or Tavily) for qualitative research, a classic API (Yahoo Finance / FMP / Finnhub) for quantitative data, a vector database for historical context, and a capable LLM (GPT-4o / Claude 4) for the final analysis — all orchestrated by LangGraph and monitored with LangSmith. Layer in the optimization framework (file-based logging → LangSmith → MLflow → counterfactual engine → shadow mode) incrementally as the pipeline matures and accumulates run history. See **Appendix B** for detailed implementation guidance on libraries, frameworks, MCP servers, testing strategies, and coding conventions. Before starting implementation, review the resources cataloged in **Appendix C** — create the recommended reference markdown files to ensure architectural patterns, prompt engineering techniques, RAG strategies, and agent orchestration best practices from the broader community are incorporated into the design from the outset.
