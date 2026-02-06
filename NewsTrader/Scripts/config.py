"""Configuration: paths, API keys, and global state for the NewsTrader pipeline."""
import os
import sys

# --- PATH CONFIGURATION ---
if sys.platform == "win32":
    MCP_BASE = r"C:\Users\HMz\Documents\Source\McpServer"
else:
    MCP_BASE = "/home/dev/proj/quantrosoft/mcp-server"

# Web Price Cache
if sys.platform == "win32":
    WEB_PRICE_CACHE_FILE = r"G:\Meine Ablage\ShareFile\NewsTrader\web_price_cache.json"
else:
    WEB_PRICE_CACHE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WEB_PRICE_CACHE_FILE = os.path.join(WEB_PRICE_CACHE_DIR, "web_price_cache.json")

# --- GLOBAL STATE ---
Global_EURUSD = None  # Must be fetched at runtime

TIINGO_KEY = None
ALPACA_KEY = None
ALPACA_SECRET = None
TR_PHONE = None
TR_PIN = None
ANTHROPIC_CLIENT = None

# When True: skip AI calls, use debug input files, output xlsx/pdf with _DEBUG suffix
DUMMY_ANALYSIS = False

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def load_env_keys():
    """Load API keys from local env.txt and MCP server dist folders."""
    global TIINGO_KEY, ANTHROPIC_CLIENT, ALPACA_KEY, ALPACA_SECRET, TR_PHONE, TR_PIN

    import anthropic

    env_paths = [
        "env.txt",
        os.path.join(MCP_BASE, "tiingo-mcp-server", "dist", "env.txt"),
        os.path.join(MCP_BASE, "alpaca-mcp-server", "dist", "env.txt"),
        os.path.join(MCP_BASE, "ibapi-mcp-server", "dist", "env.txt"),
        os.path.join(MCP_BASE, "trade-republic-mcp-server", "dist", "env.txt"),
    ]

    loaded_any = False
    for path in env_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, val = line.split("=", 1)
                            os.environ[key.strip()] = val.strip()
                print(f"Loaded environment from: {path}")
                loaded_any = True
            except Exception as e:
                print(f"Error loading keys from {path}: {e}")

    if loaded_any:
        TIINGO_KEY = os.environ.get("TIINGO_API_KEY")
        ALPACA_KEY = os.environ.get("APCA_API_KEY_ID") or os.environ.get("ALPACA_API_KEY")
        ALPACA_SECRET = (
            os.environ.get("APCA_API_SECRET_KEY") or os.environ.get("ALPACA_SECRET_KEY")
        )
        TR_PHONE = os.environ.get("TRADE_REPUBLIC_PHONE")
        TR_PIN = os.environ.get("TRADE_REPUBLIC_PIN")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            ANTHROPIC_CLIENT = anthropic.AsyncAnthropic(api_key=api_key)
            print("Anthropic Client initialized.")
        else:
            print("Warning: ANTHROPIC_API_KEY not found in any env.txt.")
    else:
        print("Warning: No env.txt files found in any search locations.")
