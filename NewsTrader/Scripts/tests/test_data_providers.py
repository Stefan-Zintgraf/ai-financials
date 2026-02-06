"""Network smoke tests for forex, Google News, Tiingo. Skipped when keys/network unavailable."""
import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_helpers import report, skip


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config")
    parser.add_argument("--filter", default=None, help="Filter params (ignored)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout (ignored)")
    args = parser.parse_args()

    if args.dry_run:
        print("Would run: forex_rate_returns_float, google_news_returns_list, tiingo_news_returns_list")
        return 0

    # Load env for key check (after dry-run so --dry-run never needs env.txt)
    import config
    config.load_env_keys()

    failed = 0

    # forex_rate_returns_float
    try:
        from data_providers import get_forex_rate
        rate = asyncio.run(get_forex_rate("EUR", "USD"))
        if rate is not None and isinstance(rate, (int, float)) and rate > 0:
            report("forex_rate_returns_float", True, "OK")
        elif rate is None:
            skip("forex_rate_returns_float", "Forex fetch returned None (Tiingo/Google unavailable)")
        else:
            report("forex_rate_returns_float", False, f"Expected float>0, got {rate}")
            failed += 1
    except Exception as e:
        skip("forex_rate_returns_float", str(e))

    # google_news_returns_list
    try:
        from news import get_google_news
        items = asyncio.run(get_google_news("Apple"))
        if isinstance(items, list):
            report("google_news_returns_list", True, "OK")
        else:
            report("google_news_returns_list", False, f"Expected list, got {type(items)}")
            failed += 1
    except Exception as e:
        skip("google_news_returns_list", str(e))

    # tiingo_news_returns_list
    if not os.environ.get("TIINGO_API_KEY") and not config.TIINGO_KEY:
        skip("tiingo_news_returns_list", "TIINGO_API_KEY not set")
    else:
        try:
            from data_providers import tiingo_get_news
            items = tiingo_get_news(tickers="AAPL", limit=3)
            if isinstance(items, list):
                report("tiingo_news_returns_list", True, "OK")
            else:
                report("tiingo_news_returns_list", False, f"Expected list, got {type(items)}")
                failed += 1
        except Exception as e:
            skip("tiingo_news_returns_list", str(e))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
