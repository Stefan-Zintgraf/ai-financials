"""AI analysis: generic LLM (Anthropic, OpenAI, Ollama) for portfolio recommendations and price troubleshooting."""
import json
import os
import re
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

import config
import llm_provider

# Debug capture for QUICK_ANALYSIS: model, multistep, prompt(s), response(s)
_LLM_DEBUG: dict | None = None


class AnalysisResult(BaseModel):
    """Schema for AI analysis output. Used for structured output and validation."""

    Recommendation: Literal["Buy", "Sell", "Hold", "Add", "Reduce"]
    recommended_quantity: int
    Reasoning: str
    quantity_reasoning: str
    Confidence: Literal["High", "Medium", "Low"]
    target_price: float | None = None
    stop_loss: float | None = None


class Step2Result(BaseModel):
    """Schema for multi-step: recommendation and reasoning."""

    Recommendation: Literal["Buy", "Sell", "Hold", "Add", "Reduce"]
    Reasoning: str
    Confidence: Literal["High", "Medium", "Low"]
    target_price: float | None = None
    stop_loss: float | None = None


class Step3Result(BaseModel):
    """Schema for multi-step: quantity calculation."""

    recommended_quantity: int
    quantity_reasoning: str


REQUIRED_FIELDS = ["Recommendation", "recommended_quantity", "Reasoning", "quantity_reasoning", "Confidence"]
OPTIONAL_FIELDS = ["target_price", "stop_loss"]


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

        advice = (await llm_provider.ainvoke(prompt, max_tokens=150)).strip()
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


def _validate_analysis_result(data: dict) -> tuple[bool, list[str]]:
    """Check required fields exist and have correct types. Returns (is_valid, missing_fields)."""
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            missing.append(field)
            continue
        val = data[field]
        if field == "Recommendation":
            if val not in ("Buy", "Sell", "Hold", "Add", "Reduce"):
                missing.append(field)
        elif field == "recommended_quantity":
            if not isinstance(val, int):
                missing.append(field)
        elif field == "Confidence":
            if val not in ("High", "Medium", "Low"):
                missing.append(field)
        elif field in ("Reasoning", "quantity_reasoning"):
            if not isinstance(val, str):
                missing.append(field)
    return (len(missing) == 0, missing)


def _build_failure_result(
    missing_fields: list[str], raw_preview: str, asset_name: str
) -> dict:
    """Return structured failure result. Never return empty dict."""
    return {
        "Recommendation": "[Parse failed]",
        "recommended_quantity": 0,
        "Reasoning": "[Incomplete] Model response could not be parsed.",
        "quantity_reasoning": f"[Missing] Required fields: {', '.join(missing_fields)}",
        "Confidence": "Low",
        "target_price": None,
        "stop_loss": None,
        "_parse_failed": True,
        "_missing_fields": missing_fields,
        "_raw_preview": raw_preview[:200] if raw_preview else "",
    }


def _lenient_parse(data: dict) -> dict:
    """
    Fill missing/invalid required fields with placeholders. Keep valid fields.
    Sets _parse_failed and _missing_fields when any required field is missing/invalid.
    """
    normalized = _normalize_analysis_keys(data)
    out = {
        "Recommendation": None,
        "recommended_quantity": 0,
        "Reasoning": "",
        "quantity_reasoning": "",
        "Confidence": "Low",
        "target_price": normalized.get("target_price"),
        "stop_loss": normalized.get("stop_loss"),
    }
    missing = []

    # Recommendation
    val = normalized.get("Recommendation")
    if val in ("Buy", "Sell", "Hold", "Add", "Reduce"):
        out["Recommendation"] = val
    elif val is not None and val != "":
        out["Recommendation"] = "[Invalid]"
        missing.append("Recommendation")
    else:
        out["Recommendation"] = "[Missing]"
        missing.append("Recommendation")

    # recommended_quantity
    val = normalized.get("recommended_quantity")
    if isinstance(val, int):
        out["recommended_quantity"] = val
    elif val is not None:
        out["recommended_quantity"] = 0
        missing.append("recommended_quantity")
    else:
        missing.append("recommended_quantity")

    # Reasoning
    val = normalized.get("Reasoning")
    if isinstance(val, str) and val.strip():
        out["Reasoning"] = val
    elif val is not None:
        out["Reasoning"] = "[Invalid]"
        missing.append("Reasoning")
    else:
        out["Reasoning"] = "[Missing]"
        missing.append("Reasoning")

    # quantity_reasoning
    val = normalized.get("quantity_reasoning")
    if isinstance(val, str) and val.strip():
        out["quantity_reasoning"] = val
    elif val is not None:
        out["quantity_reasoning"] = "[Invalid]"
        missing.append("quantity_reasoning")
    else:
        out["quantity_reasoning"] = "[Missing]"
        missing.append("quantity_reasoning")

    # Confidence
    val = normalized.get("Confidence")
    if val in ("High", "Medium", "Low"):
        out["Confidence"] = val
    elif val is not None:
        out["Confidence"] = "Low"
        missing.append("Confidence")
    else:
        missing.append("Confidence")

    # target_price, stop_loss - optional, coerce to float or None
    for f in ("target_price", "stop_loss"):
        val = normalized.get(f)
        if val is None:
            out[f] = None
        elif isinstance(val, (int, float)):
            out[f] = float(val)
        else:
            out[f] = None

    if missing:
        out["_parse_failed"] = True
        out["_missing_fields"] = missing

    return out


def _init_llm_debug_if_needed():
    """Initialize _LLM_DEBUG for QUICK_ANALYSIS captures."""
    global _LLM_DEBUG
    if not config.QUICK_ANALYSIS or config.DUMMY_ANALYSIS:
        return
    if _LLM_DEBUG is None:
        _LLM_DEBUG = {
            "model": config.get_model_display_name(),
            "multistep": _use_multi_step(),
            "entries": [],
        }


def _record_llm_entry(asset_name: str, multistep: bool, entry: dict):
    """Record one asset's prompt/response for debug output."""
    _init_llm_debug_if_needed()
    if _LLM_DEBUG is None:
        return
    _LLM_DEBUG["entries"].append({"asset": asset_name, "multistep": multistep, **entry})


def write_llm_debug(folder_path: str | Path) -> None:
    """Write captured LLM debug data to folder_path/llm_debug.json. Clears capture."""
    global _LLM_DEBUG
    if _LLM_DEBUG is None or not _LLM_DEBUG.get("entries"):
        return
    path = Path(folder_path) / "llm_debug.json"
    try:
        path.write_text(json.dumps(_LLM_DEBUG, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    _LLM_DEBUG = None


def _use_multi_step() -> bool:
    """Use multi-step prompts. Controlled by AI_MULTI_STEP env (auto|on|off)."""
    mode = os.environ.get("AI_MULTI_STEP", "auto").lower()
    if mode == "off":
        return False
    if mode == "on":
        return True
    if os.environ.get("AI_PROVIDER", "").lower() != "ollama":
        return False
    ctx_size = llm_provider.get_model_context_size()
    if ctx_size is None:
        return False
    threshold = int(os.environ.get("AI_MULTI_STEP_THRESHOLD", "4096"))
    return ctx_size <= threshold


def _regex_extract(raw_text: str) -> dict | None:
    """Extract analysis fields from raw text when JSON parse fails. Returns partial dict or None."""
    if not raw_text or not raw_text.strip():
        return None
    text = raw_text.strip()
    out = {}
    m_rec = re.search(r"\b(Buy|Sell|Hold|Add|Reduce)\b", text, re.I)
    if m_rec:
        out["Recommendation"] = m_rec.group(1).capitalize()
    m_conf = re.search(r"\b(High|Medium|Low)\b", text, re.I)
    if m_conf:
        out["Confidence"] = m_conf.group(1).capitalize()
    m_qty = re.search(
        r"(?:recommended_quantity|quantity|shares?)\s*[=:]\s*(-?\d+)", text, re.I
    )
    if not m_qty:
        m_qty = re.search(r"(?:buy|sell|add|reduce)\s+(\d+)", text, re.I)
    if m_qty:
        out["recommended_quantity"] = int(m_qty.group(1))
    m_reason = re.search(r"(?:because|reason)[:\s]+([^.]+\.?)", text, re.I)
    if m_reason:
        out["Reasoning"] = m_reason.group(1).strip()
    if not out:
        return None
    return out


def _build_step1_prompt(
    asset_info,
    collected_data,
    pnl_info: str,
    total_invest: float,
    current_invest: float,
    current_allocation_pct: float,
    target_pos_size_eur: float,
    today_date: str,
) -> str:
    """Step 1: full context, asks for summary. Output: free-form text."""
    return f"""
ROLE: Senior Portfolio Manager. Be factual and concise.

DATE: {today_date}
ASSET: {asset_info.get('Asset')} ({asset_info.get('Ticker')})
ISIN: {asset_info.get('ISIN')}
POSITIONS_DATA:
{pnl_info}

MARKET_DATA:
{json.dumps(collected_data, indent=2, default=str)}

PORTFOLIO_CONTEXT:
Total Portfolio: {total_invest:.2f} EUR. Current position: {current_invest:.2f} EUR ({current_allocation_pct:.1f}%). Target per asset: ~5% ({target_pos_size_eur:.2f} EUR).

TASK: Summarize in 3-5 sentences: (1) Key news headlines from the data above, (2) Current price, (3) Sentiment, (4) Portfolio allocation. List each news headline on a new line with "- [Source]: [Title]". If no news, say "No current headlines."
""".strip()


def _build_step2_prompt(
    summary: str,
    total_invest: float,
    current_invest: float,
    current_allocation_pct: float,
    target_pos_size_eur: float,
) -> str:
    """Step 2: summary + portfolio, asks for recommendation. Output: structured."""
    return f"""
CONTEXT SUMMARY:
{summary}

PORTFOLIO:
Total: {total_invest:.2f} EUR. Current position: {current_invest:.2f} EUR ({current_allocation_pct:.1f}%). Target 5%: {target_pos_size_eur:.2f} EUR.

RULES:
- If allocation >6%, recommend REDUCE or SELL.
- If allocation <3% and sentiment positive, recommend ADD or BUY.
- If sentiment neutral/negative, recommend HOLD or SELL.

Respond with JSON only:
{{"Recommendation": "Buy"|"Sell"|"Hold"|"Add"|"Reduce", "Reasoning": "...", "Confidence": "High"|"Medium"|"Low", "target_price": number|null, "stop_loss": number|null}}
""".strip()


def _build_step3_prompt(
    step2_result: dict,
    current_price: float | None,
    target_pos_size_eur: float,
    current_invest: float,
    total_invest: float,
) -> str:
    """Step 3: recommendation + price, asks for quantity. Output: structured."""
    rec = step2_result.get("Recommendation", "Hold")
    price = current_price or 0.0
    target_val = target_pos_size_eur
    current_val = current_invest
    diff = target_val - current_val
    return f"""
Recommendation from previous step: {rec}
Current price: {price:.2f} EUR
Target position value: {target_val:.2f} EUR (5% of {total_invest:.2f} EUR)
Current position value: {current_val:.2f} EUR
Difference: {diff:.2f} EUR

Formula: recommended_quantity = round((Target_Value - Current_Value) / Price). Positive for Buy/Add, negative for Sell/Reduce, 0 for Hold.

Respond with JSON only:
{{"recommended_quantity": <integer>, "quantity_reasoning": "Brief explanation"}}
""".strip()


async def _run_multi_step_analysis(
    asset_info,
    collected_data,
    all_portfolio_data,
    pnl_info: str,
    current_price: float | None,
    total_invest: float,
    current_invest: float,
    current_allocation_pct: float,
    target_pos_size_eur: float,
    today_date: str,
    asset_name: str,
) -> dict | None:
    """Run 3-step analysis. Returns merged dict or None on failure."""
    prompt1 = _build_step1_prompt(
        asset_info,
        collected_data,
        pnl_info,
        total_invest,
        current_invest,
        current_allocation_pct,
        target_pos_size_eur,
        today_date,
    )
    summary = await llm_provider.ainvoke(prompt1, max_tokens=150)
    if not summary or not summary.strip():
        return None
    summary = summary.strip()

    prompt2 = _build_step2_prompt(
        summary, total_invest, current_invest, current_allocation_pct, target_pos_size_eur
    )
    step2_raw = await llm_provider.ainvoke_structured(
        prompt2, Step2Result, max_tokens=300
    )
    response2_str = None
    if step2_raw is None:
        response2_str = await llm_provider.ainvoke(prompt2, max_tokens=300)
        response2 = response2_str
        s, e = response2.find("{"), response2.rfind("}") + 1
        if s != -1 and e > 0:
            try:
                step2_raw = json.loads(response2[s:e], strict=False)
            except json.JSONDecodeError:
                pass
    if step2_raw is None:
        return None
    step2 = (
        step2_raw.model_dump()
        if hasattr(step2_raw, "model_dump")
        else dict(step2_raw)
    )
    if response2_str is None:
        response2_str = json.dumps(step2)

    prompt3 = _build_step3_prompt(
        step2, current_price, target_pos_size_eur, current_invest, total_invest
    )
    step3_raw = await llm_provider.ainvoke_structured(
        prompt3, Step3Result, max_tokens=150
    )
    response3_str = None
    if step3_raw is None:
        response3_str = await llm_provider.ainvoke(prompt3, max_tokens=150)
        response3 = response3_str
        s, e = response3_str.find("{"), response3_str.rfind("}") + 1
        if s != -1 and e > 0:
            try:
                step3_raw = json.loads(response3[s:e], strict=False)
            except json.JSONDecodeError:
                pass
    step3 = {}
    if step3_raw is not None:
        step3 = (
            step3_raw.model_dump()
            if hasattr(step3_raw, "model_dump")
            else dict(step3_raw)
        )
    if response3_str is None and step3:
        response3_str = json.dumps(step3)

    qty = step3.get("recommended_quantity", 0)
    if isinstance(qty, str):
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            qty = 0
    elif not isinstance(qty, int):
        qty = 0

    merged = {
        "Recommendation": step2.get("Recommendation"),
        "recommended_quantity": qty,
        "Reasoning": step2.get("Reasoning", ""),
        "quantity_reasoning": step3.get("quantity_reasoning", ""),
        "Confidence": step2.get("Confidence", "Low"),
        "target_price": step2.get("target_price"),
        "stop_loss": step2.get("stop_loss"),
    }
    _record_llm_entry(
        asset_name,
        True,
        {
            "steps": [
                {"prompt": prompt1, "response": summary},
                {"prompt": prompt2, "response": response2_str or ""},
                {"prompt": prompt3, "response": response3_str or ""},
            ]
        },
    )
    return merged


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

    def _build_prompt(include_json_block: bool) -> str:
        base = f"""
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
"""
        if include_json_block:
            base += f"""

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
        return base.strip()

    def _try_parse_response(response_text: str) -> dict | None:
        """Extract JSON from response, or None if not found."""
        s = response_text.find("{")
        e = response_text.rfind("}") + 1
        if s == -1 or e == 0:
            return None
        json_str = response_text[s:e]
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            try:
                clean_json = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", json_str)
                return json.loads(clean_json, strict=False)
            except Exception:
                return None

    try:
        if _use_multi_step():
            result = await _run_multi_step_analysis(
                asset_info,
                collected_data,
                all_portfolio_data,
                pnl_info,
                current_price,
                total_invest,
                current_invest,
                current_allocation_pct,
                target_pos_size_eur,
                today_date,
                asset_name,
            )
            if result is not None:
                is_valid, missing = _validate_analysis_result(result)
                if is_valid:
                    return result
                lenient = _lenient_parse(result)
                if lenient.get("_parse_failed"):
                    print(
                        f"    Analysis incomplete for {asset_name}: missing or invalid fields {missing}."
                    )
                return lenient
            print(f"    Multi-step failed for {asset_name}, falling back to single-prompt.")

        prompt_structured = _build_prompt(include_json_block=False)
        result = await llm_provider.ainvoke_structured(
            prompt_structured, AnalysisResult, max_tokens=1000
        )
        if result is not None:
            res_dict = result.model_dump() if hasattr(result, "model_dump") else dict(result)
            _record_llm_entry(asset_name, False, {"prompt": prompt_structured, "response": json.dumps(res_dict)})
            is_valid, missing = _validate_analysis_result(result)
            if is_valid:
                return result
            lenient = _lenient_parse(result)
            if lenient.get("_parse_failed"):
                print(
                    f"    Analysis incomplete for {asset_name}: missing or invalid fields {missing}."
                )
            return lenient

        prompt_fallback = _build_prompt(include_json_block=True)
        response_text = await llm_provider.ainvoke(prompt_fallback, max_tokens=1000)

        data = _try_parse_response(response_text)
        if data is not None:
            _record_llm_entry(asset_name, False, {"prompt": prompt_fallback, "response": response_text})
            lenient = _lenient_parse(data)
            if lenient.get("_parse_failed"):
                missing = lenient.get("_missing_fields", REQUIRED_FIELDS)
                lenient["_raw_preview"] = response_text[:200] if response_text else ""
                print(
                    f"    Analysis incomplete for {asset_name}: missing or invalid fields {missing}."
                )
            return lenient

        regex_data = _regex_extract(response_text)
        if regex_data:
            _record_llm_entry(asset_name, False, {"prompt": prompt_fallback, "response": response_text})
            lenient = _lenient_parse(regex_data)
            print(f"    Used regex fallback for {asset_name}.")
            return lenient

        print(f"    Retrying with lower temperature for {asset_name}...")
        retry_text = await llm_provider.ainvoke_retry(prompt_fallback, max_tokens=400)
        data = _try_parse_response(retry_text)
        if data is not None:
            _record_llm_entry(asset_name, False, {"prompt": prompt_fallback, "response": retry_text})
            lenient = _lenient_parse(data)
            return lenient
        regex_data = _regex_extract(retry_text)
        if regex_data:
            _record_llm_entry(asset_name, False, {"prompt": prompt_fallback, "response": retry_text})
            lenient = _lenient_parse(regex_data)
            return lenient

        _record_llm_entry(asset_name, False, {"prompt": prompt_fallback, "response": retry_text or response_text})
        print(f"    No JSON found in AI response for {asset_name}")
        return _build_failure_result(
            REQUIRED_FIELDS, response_text[:200] if response_text else "", asset_name
        )
    except Exception as e:
        print(f"    AI Analysis Error for {asset_name}: {e}")
        return _build_failure_result(REQUIRED_FIELDS, str(e), asset_name)
