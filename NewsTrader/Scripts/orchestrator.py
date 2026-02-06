"""Orchestrator: main pipeline flow, fetch_asset_data, and coordination."""
import os
import sys
import glob
import pandas as pd
from datetime import datetime

import config
import llm_provider
from utils import Tee
from data_providers import get_forex_rate, ALPACA_AVAILABLE
from price_search import deep_dive_price_search
from news import aggregate_news
from ai_analysis import analyze_data, troubleshoot_no_price, write_llm_debug
from pdf_report import create_pdf
from excel_report import save_analysis_excel

if ALPACA_AVAILABLE:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest


async def fetch_asset_data(asset):
    """Fetch all data for an asset using available price sources."""
    ticker = asset.get("Ticker", "")
    if not ticker and asset.get("ISIN"):
        ticker = asset.get("ISIN")

    result = {
        "Asset": asset.get("Asset"),
        "Ticker": ticker,
        "FetchedAt": datetime.now().isoformat(),
    }

    print(f"  Data: {asset.get('Asset')} ({ticker})")

    price_found = False

    if ALPACA_AVAILABLE and config.ALPACA_KEY and ticker and not price_found:
        try:
            alpaca_client = StockHistoricalDataClient(config.ALPACA_KEY, config.ALPACA_SECRET)
            req = StockLatestQuoteRequest(symbol_or_symbols=ticker)
            quote = alpaca_client.get_stock_latest_quote(req)
            if ticker in quote:
                q = quote[ticker]
                result["Alpaca_Price"] = {
                    "bid": q.bid_price,
                    "ask": q.ask_price,
                    "mid_price": (q.bid_price + q.ask_price) / 2
                    if q.bid_price and q.ask_price
                    else None,
                }
                if result["Alpaca_Price"]["mid_price"] and config.Global_EURUSD:
                    orig = result["Alpaca_Price"]["mid_price"]
                    result["Alpaca_Price"]["mid_price"] = orig / config.Global_EURUSD
                    result["Alpaca_Price"]["note"] = f"Converted from {orig} USD"
                    result["Alpaca_Price"]["currency"] = "EUR"
                else:
                    result["Alpaca_Price"]["currency"] = "USD"
                print(f"    Alpaca Price: {result['Alpaca_Price']['mid_price']:.2f} {result['Alpaca_Price']['currency']}")
                price_found = True
        except Exception:
            pass

    if not price_found:
        try:
            web_price = await deep_dive_price_search(asset, ticker)
            if "price" in web_price:
                result["Web_Price"] = web_price
                print(f"    Web Price ({web_price.get('source')}): {web_price['price']}")
                price_found = True
            else:
                result["Web_Price"] = web_price
        except Exception as e:
            result["Web_Price_Error"] = str(e)

    found_price_log = None
    found_source_log = None
    found_curr_log = "EUR"

    if "Alpaca_Price" in result and "mid_price" in result["Alpaca_Price"]:
        found_price_log = result["Alpaca_Price"]["mid_price"]
        found_curr_log = result["Alpaca_Price"].get("currency", "USD")
        found_source_log = "Alpaca"
    elif "Web_Price" in result and "price" in result["Web_Price"]:
        found_price_log = result["Web_Price"]["price"]
        found_curr_log = "EUR"
        found_source_log = result["Web_Price"].get("source", "Web")

    if found_price_log:
        print(f"    Found current price at {found_source_log}: {found_price_log:.2f} {found_curr_log}")
    else:
        print("    No current price found.")
        await troubleshoot_no_price(asset)

    news_data = await aggregate_news(asset, ticker)
    result["News"] = news_data
    if news_data["count"] > 0:
        print(f"    Found {news_data['count']} news items")

    return result


async def main():
    config.Global_EURUSD = None

    if sys.platform == "win32":
        base_dir = r"G:\Meine Ablage\ShareFile\NewsTrader"
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    positions_file = os.path.join(base_dir, "Open_Positions.xlsx")
    watchlist_file = os.path.join(base_dir, "Watch_Positions.xlsx")
    use_debug_files = config.DUMMY_ANALYSIS or config.QUICK_ANALYSIS
    if use_debug_files:
        pos_debug = os.path.join(base_dir, "Open_Positions_Debug.xlsx")
        watch_debug = os.path.join(base_dir, "Watch_Positions_Debug.xlsx")
        prefix = "[DUMMY]" if config.DUMMY_ANALYSIS else "[QUICK]"
        if os.path.exists(pos_debug):
            positions_file = pos_debug
            print(f"{prefix} Using debug positions: {pos_debug}")
        if os.path.exists(watch_debug):
            watchlist_file = watch_debug
            print(f"{prefix} Using debug watchlist: {watch_debug}")

    analysen_dir = os.path.join(base_dir, "Analysen")
    today_str = datetime.now().strftime("%y%m%d")
    daily_folder = os.path.join(analysen_dir, today_str)
    os.makedirs(daily_folder, exist_ok=True)
    debug_suffix = "_DEBUG" if use_debug_files else ""
    output_file = os.path.join(daily_folder, f"{today_str} Portfolio_Pipeline_Analyse{debug_suffix}.xlsx")
    log_file_path = os.path.join(daily_folder, f"{today_str}_Pipeline.log")

    if os.path.exists(log_file_path):
        try:
            os.remove(log_file_path)
            print(f"Deleted old log file: {log_file_path}")
        except Exception:
            pass

    log_file = open(log_file_path, "a", encoding="utf-8")
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    print(f"\n{'='*50}")
    print(f"Logging to: {log_file_path}")
    print(f"{'='*50}\n")

    config.load_env_keys()
    config.apply_cli_overrides()

    # Initialize and verify LLM (unless dummy mode)
    if not config.DUMMY_ANALYSIS:
        try:
            llm_provider.init_llm()
            await llm_provider.verify_llm()
        except Exception as e:
            print(f"FATAL: LLM not available: {e}")
            sys.exit(1)
    else:
        print("[DUMMY] Skipping LLM initialization.")

    print(f"Cleaning up old analysis files for {today_str}...")
    try:
        old_files = glob.glob(os.path.join(daily_folder, "*"))
        for f in old_files:
            if os.path.abspath(f) == os.path.abspath(log_file_path):
                continue
            try:
                os.remove(f)
                print(f"   Deleted: {os.path.basename(f)}")
            except Exception:
                pass
    except Exception as e:
        print(f"   Cleanup warning: {e}")

    print(f"Reading {positions_file}...")
    df = pd.read_excel(positions_file)
    df = df.dropna(subset=["Asset"])
    assets = df.to_dict("records")

    watchlist_assets = []
    if os.path.exists(watchlist_file):
        print(f"Reading {watchlist_file}...")
        df_watch = pd.read_excel(watchlist_file)
        if "Asset" not in df_watch.columns and "Emittent" in df_watch.columns:
            print("   Mapped 'Emittent' to 'Asset' for Watchlist.")
            df_watch["Asset"] = df_watch["Emittent"]
        if "Asset" in df_watch.columns:
            df_watch = df_watch.dropna(subset=["Asset"])
            watchlist_assets = df_watch.to_dict("records")
        else:
            print("   Watchlist has no 'Asset' or 'Emittent' column. Skipping.")
    else:
        print(f"No Watchlist file found at: {watchlist_file}")

    print(f"Starting Pipeline Analysis for {len(assets)} assets and {len(watchlist_assets)} watchlist items...")

    results = []
    watchlist_results = []

    config.Global_EURUSD = await get_forex_rate("EUR", "USD")
    if not config.Global_EURUSD:
        print("FATAL ERROR: Could not determine EUR/USD exchange rate.")
        print("   Cannot proceed safely with currency conversions.")
        return

    print(f"Active EUR/USD Rate: {config.Global_EURUSD}")

    print("\n" + "=" * 40)
    print("PROCESSING PORTFOLIO")
    print("=" * 40)
    for i, asset in enumerate(assets):
        print(f"\n[{i+1}/{len(assets)}] Processing: {asset.get('Asset')}...")
        data = await fetch_asset_data(asset)
        if "FATAL_ERROR" in data:
            print("\n" + "!" * 50)
            print(f"STOPPING: {data['FATAL_ERROR']}")
            print("!" * 50)
            sys.exit(1)
        analysis = await analyze_data(asset, data, assets)
        final_record = {**asset, **analysis, **data}
        results.append(final_record)
        try:
            safe_name = "".join([c for c in asset.get("Asset", "Unknown") if c.isalpha() or c.isdigit()]).strip()
            create_pdf(os.path.join(daily_folder, f"{today_str}_{safe_name}{debug_suffix}.pdf"), final_record, config.get_model_display_name())
        except Exception:
            pass

    if watchlist_assets:
        print("\n" + "=" * 40)
        print("PROCESSING WATCHLIST")
        print("=" * 40)
        for i, asset in enumerate(watchlist_assets):
            print(f"\n[{i+1}/{len(watchlist_assets)}] Watching: {asset.get('Asset')}...")
            data = await fetch_asset_data(asset)
            analysis = await analyze_data(asset, data, assets)
            final_record = {**asset, **analysis, **data}
            watchlist_results.append(final_record)
            try:
                safe_name = "".join([c for c in asset.get("Asset", "Unknown") if c.isalpha() or c.isdigit()]).strip()
                create_pdf(os.path.join(daily_folder, f"{today_str}_CHECK_{safe_name}{debug_suffix}.pdf"), final_record, config.get_model_display_name())
            except Exception:
                pass

    save_analysis_excel(output_file, results, watchlist_results, assets)

    if config.QUICK_ANALYSIS:
        write_llm_debug(daily_folder)

    print(f"\nPipeline Complete. Saved to {output_file}")
