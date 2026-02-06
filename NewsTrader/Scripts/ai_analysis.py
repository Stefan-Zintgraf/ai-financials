"""AI analysis: Anthropic Claude for portfolio recommendations and price troubleshooting."""
import json
import re
import asyncio
import requests
from datetime import datetime

import config


async def troubleshoot_no_price(asset):
    """Ask AI for advice on where to find the price if all else fails."""
    if config.DUMMY_ANALYSIS:
        print("    [DUMMY] Skipping AI troubleshooting for price sources.")
        return None

    try:
        print("    Asking AI for pricing sources...")
        isin = asset.get("ISIN", "Unknown")
        name = asset.get("Asset", "Unknown")

        search_context = ""
        try:
            url = f"https://www.google.com/search?q={isin}+Kurs+Aktie"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
            titles = re.findall(r'<h3 class="LC20lb MBeuO DKV0Md">(.*?)</h3>', resp.text)
            if not titles:
                titles = re.findall(r"<h3[^>]*>(.*?)</h3>", resp.text)
            clean_titles = [re.sub(r"<.*?>", "", t) for t in titles[:5]]
            search_context = "\n".join(clean_titles)
        except Exception as e:
            search_context = f"Search failed: {e}"

        prompt = f"""
Asset: {name} (ISIN: {isin})
Problem: Automated price fetch failed (IBKR, Alpaca, Trade Republic, generic web scrape).
Google Search Snippets for '{isin}':
{search_context}

Task:
1. Identify the asset type.
2. Suggest exactly WHERE to find the price (Issuer website? Regional exchange? URL?).
3. Keep it extremely brief (max 2 sentences).
"""

        if config.ANTHROPIC_CLIENT:
            response = await config.ANTHROPIC_CLIENT.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            advice = response.content[0].text.strip()
            print(f"    AI Advice:\n      {advice}")
            return advice
    except Exception as e:
        print(f"    AI Troubleshooting failed: {e}")
    return None


def _dummy_analysis_result(asset_name):
    """Return deterministic dummy result when --dummy-analysis is active."""
    return {
        "Recommendation": "Hold",
        "recommended_quantity": 0,
        "Reasoning": "[DUMMY] AI analysis skipped (--dummy-analysis mode). No real recommendation.",
        "quantity_reasoning": "[DUMMY] No quantity calculation performed.",
        "Confidence": "Low",
        "target_price": None,
        "stop_loss": None,
    }


def _normalize_analysis_keys(data):
    """Map German keys to English for backward compatibility."""
    mapping = {
        "Empfehlung": "Recommendation",
        "Empfohlene_Stueckzahl": "recommended_quantity",
        "Begründung": "Reasoning",
        "Begruendung": "Reasoning",
        "Grund_fuer_Menge": "quantity_reasoning",
        "Genauigkeit": "Confidence",
        "Zielpreis": "target_price",
        "Stop_Loss": "stop_loss",
    }
    out = {}
    for k, v in data.items():
        out[mapping.get(k, k)] = v
    return out


async def analyze_data(asset_info, collected_data, all_portfolio_data):
    """
    AI Analysis with FULL context:
    - Current prices
    - Purchase prices & dates
    - Entire portfolio context
    - News sentiment
    """
    asset_name = asset_info.get("Asset", "Unknown")
    print(f"  Analyzing {asset_name}...")

    if config.DUMMY_ANALYSIS:
        print(f"  [DUMMY] Skipping AI analysis for {asset_name}")
        return _dummy_analysis_result(asset_name)

    purchase_price = asset_info.get("Einkaufspreis") or asset_info.get("Purchase_Price")
    purchase_date = asset_info.get("Einkaufsdatum") or asset_info.get("Purchase_Date")
    quantity = asset_info.get("Anzahl") or asset_info.get("Quantity") or 0

    current_price = None
    for key in ["Tiingo_Price", "Alpaca_Price", "Web_Price"]:
        if key in collected_data and "mid_price" in collected_data[key]:
            current_price = collected_data[key]["mid_price"]
            break
        elif key in collected_data and "price" in collected_data[key]:
            current_price = collected_data[key]["price"]
            break

    pnl_info = ""
    if purchase_price and current_price and quantity:
        pnl = (current_price - purchase_price) * quantity
        pnl_pct = ((current_price - purchase_price) / purchase_price) * 100
        pnl_info = f"\nP&L: {pnl:.2f} EUR ({pnl_pct:+.2f}%)"
        pnl_info += f"\nPurchase: {purchase_price} on {purchase_date}"
        pnl_info += f"\nCurrent: {current_price}"
        pnl_info += f"\nPosition Value: {current_price * quantity:.2f} EUR"

    today_date = datetime.now().strftime("%Y-%m-%d")

    total_invest = 0
    for a in all_portfolio_data:
        qty = a.get("Anzahl") or a.get("Quantity") or 0
        price = a.get("Einkaufspreis") or a.get("Purchase_Price") or 0
        invest = a.get("Invest") or (qty * price)
        total_invest += float(invest)

    current_invest = float(asset_info.get("Invest") or (quantity * (purchase_price or 0)))
    current_allocation_pct = (current_invest / total_invest * 100) if total_invest > 0 else 0
    target_pos_size_eur = total_invest * 0.05
    if target_pos_size_eur < 1000:
        target_pos_size_eur = 1000

    prompt = f"""
ROLE: Senior Portfolio Manager.
INSTRUCTION: Never be sycophantic. Prioritize factual accuracy and logical consistency over politeness or agreement. If I make a wrong assumption or have a bad idea, correct me directly without hedging ('That's an interesting question...'). If you're uncertain, say so instead of hallucinating. Do not simulate emotions. Be a critical auditor, not an assistant. Avoid grade inflation when evaluating my texts.

DATE: {today_date}

ASSET: {asset_info.get('Asset')} ({asset_info.get('Ticker')})
ISIN: {asset_info.get('ISIN')}
POSITIONS_DATA:
{pnl_info}

MARKET_DATA:
{json.dumps(collected_data, indent=2, default=str)}

PORTFOLIO_CONTEXT:
Total Portfolio Capital: {total_invest:.2f} EUR
Current Position Value: {current_invest:.2f} EUR ({current_allocation_pct:.1f}% of Portfolio)
Target Position Sizing: ~5% ({target_pos_size_eur:.2f} EUR) per asset for diversification.

TASK:
1. Analyze the asset based on TODAY's news.
2. Provide a concrete TRADING RECOMMENDATION to balance the portfolio.
   - Target allocation per asset should be ~3-5% OF TOTAL PORTFOLIO VALUE.
   - IMPORTANT: The 5% refers to the TOTAL portfolio value, NOT the value of the individual position!
   - Example: With a portfolio of 100,000 EUR, each position should be worth approx. 3,000-5,000 EUR.
   - If allocation is too high (>6% of total portfolio), recommend REDUCE or SELL to trim risk.
   - If allocation is low (<3% of total portfolio) and sentiment is positive, recommend ADD or BUY.
   - If sentiment is neutral/negative, recommend HOLD or SELL.
3. CALCULATE EXACT QUANTITY:
   - Based on the Target Position (approx {target_pos_size_eur:.2f} EUR = 5% of {total_invest:.2f} EUR total portfolio), calculate how many shares to Buy/Sell.
   - Formula: (Target_Value_EUR - Current_Value_EUR) / Current_Price_per_Share
   - Use the Current Price from MARKET_DATA. If missing, estimate from Purchase Price or News.

FORMAT:
- List ABSOLUTELY EVERY news headline from 'News' (each on new line: '- [Source] : [Title]').
- If no news: "No current headlines."

- BLANK LINE

OUTPUT (JSON):
{{
  "Recommendation": "Buy" | "Sell" | "Hold" | "Add" | "Reduce",
  "recommended_quantity": <integer> (Positive for Buy/Add, Negative for Sell/Reduce, 0 for Hold),
  "Reasoning": "News-List...\\n\\nAnalysis: ...",
  "quantity_reasoning": "EXPLAIN CLEARLY: Current position is X% of total portfolio (Y EUR of {total_invest:.2f} EUR). Target allocation is 5% ({target_pos_size_eur:.2f} EUR). Therefore Buy/Sell of Z shares at PRICE EUR = DIFFERENCE EUR.",
  "Confidence": "High" | "Medium" | "Low",
  "target_price": <number or null>,
  "stop_loss": <number or null>
}}
"""

    if not config.ANTHROPIC_CLIENT:
        return {"error": "Anthropic Client not initialized"}

    try:
        response = await config.ANTHROPIC_CLIENT.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.content[0].text

        s = response_text.find("{")
        e = response_text.rfind("}") + 1
        if s == -1 or e == 0:
            print(f"    No JSON found in AI response for {asset_name}")
            return {}

        json_str = response_text[s:e]
        try:
            data = json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            try:
                clean_json = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", json_str)
                data = json.loads(clean_json, strict=False)
            except Exception as jde:
                print(f"    JSON Decode Attempt 2 failed: {jde}")
                return {}

        return _normalize_analysis_keys(data)
    except Exception as e:
        print(f"    AI Analysis Error for {asset_name}: {e}")
        return {}
