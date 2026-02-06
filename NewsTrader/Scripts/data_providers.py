"""Data providers: Tiingo, Alpaca, forex rate."""
import json
import os
import subprocess
import sys
import asyncio
import requests
import re

import config

# --- TIINGO ---
if config.MCP_BASE and os.name != "nt":
    TIINGO_MCP_PATH = os.path.join(config.MCP_BASE, "tiingo-mcp-server")
    TIINGO_PYTHON = os.path.join(TIINGO_MCP_PATH, ".venv", "bin", "python")
    TIINGO_RUNNER = os.path.join(TIINGO_MCP_PATH, "tiingo_runner.py")

    def _run_tiingo(cmd: list) -> list | dict:
        """Run tiingo_runner.py via tiingo venv; returns parsed JSON or [] on error."""
        if not os.path.isfile(TIINGO_PYTHON):
            raise RuntimeError(
                f"Tiingo venv not found at {TIINGO_PYTHON}. "
                "Install: python -m venv .venv && pip install -r requirements.txt"
            )
        if not os.path.isfile(TIINGO_RUNNER):
            raise RuntimeError(f"Tiingo runner not found at {TIINGO_RUNNER}")
        env = os.environ.copy()
        result = subprocess.run(
            [TIINGO_PYTHON, TIINGO_RUNNER] + cmd,
            capture_output=True,
            text=True,
            cwd=TIINGO_MCP_PATH,
            env=env,
            timeout=60,
        )
        if result.returncode != 0:
            err = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(f"Tiingo runner failed: {err}")
        out = result.stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(data["error"])
        return data

    def tiingo_get_price(ticker: str):
        """Get ticker price via tiingo venv subprocess."""
        return _run_tiingo(["get_ticker_price", ticker])

    def tiingo_get_news(tickers=None, limit: int = 20, **kwargs):
        """Get news via tiingo venv subprocess."""
        cmd = ["get_news", "--limit", str(limit)]
        if tickers is not None:
            t = tickers if isinstance(tickers, str) else ",".join(tickers) if tickers else ""
            if t:
                cmd.extend(["--tickers", t])
        return _run_tiingo(cmd)
else:
    # Windows: import from tiingo-mcp-server
    sys.path.insert(0, os.path.join(config.MCP_BASE, "tiingo-mcp-server"))
    try:
        from tiingo_mcp_server.tiingo_functions import (
            get_ticker_price_sync as tiingo_get_price,
            get_news_sync as tiingo_get_news,
        )
    except ImportError as e:
        print(f"Critical Import Error (Tiingo): {e}")
        sys.exit(1)

# --- ALPACA ---
try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest
    ALPACA_AVAILABLE = True
    print("Alpaca: OK")
except ImportError as e:
    print("Alpaca import failed:", type(e).__name__, e)
    ALPACA_AVAILABLE = False


async def get_forex_rate(base="EUR", quote="USD"):
    """
    Fetch current forex rate (e.g. EUR to USD) robustly.
    1. Tiingo API
    2. Web Scraping (Google Finance)
    """
    print("    Fetching Forex via Tiingo...")
    if config.TIINGO_KEY:
        try:
            url = f"https://api.tiingo.com/tiingo/fx/top?tickers={base.lower()}{quote.lower()}&token={config.TIINGO_KEY}"
            headers = {"Content-Type": "application/json"}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                rate = data.get("midPrice")
                if rate:
                    print(f"    Forex via Tiingo: {rate}")
                    return float(rate)
        except Exception as e:
            print(f"    Tiingo Forex failed: {e}")

    print("    Tiingo missing, trying Google Finance...")
    try:
        url = f"https://www.google.com/finance/quote/{base}-{quote}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        match = re.search(r'data-last-price="([\d\.]+)"', resp.text)
        if match:
            rate = float(match.group(1))
            print(f"    Forex via Google Finance: {rate}")
            return rate
        match = re.search(r'<div class="YMlKec fxKbKc">([\d\.]+)</div>', resp.text)
        if match:
            rate = float(match.group(1))
            print(f"    Forex via Google Finance: {rate}")
            return rate
    except Exception as e:
        print(f"    Google Finance Forex failed: {e}")

    return None
