"""Configuration: paths, API keys, and global state for the NewsTrader pipeline."""
import os
import sys

# --- CLI OVERRIDES ---
# Parsed from --provider=, --mode=, --multistep=, --multistep_thr=
# Applied after load_env_keys(); overrides env.txt.


def apply_cli_overrides():
    """Parse CLI args and override os.environ. Call after load_env_keys()."""
    provider = None
    mode = None
    multistep = None
    multistep_thr = None
    for arg in sys.argv[1:]:
        if arg.startswith("--provider="):
            provider = arg.split("=", 1)[1].strip().lower()
        elif arg.startswith("--mode="):
            mode = arg.split("=", 1)[1].strip()
        elif arg.startswith("--multistep="):
            multistep = arg.split("=", 1)[1].strip().lower()
        elif arg.startswith("--multistep_thr="):
            multistep_thr = arg.split("=", 1)[1].strip()

    if provider:
        os.environ["AI_PROVIDER"] = provider
        print(f"  CLI override: AI_PROVIDER={provider}")
    if mode:
        p = os.environ.get("AI_PROVIDER", "anthropic").lower()
        if p == "ollama":
            os.environ["OLLAMA_MODEL"] = mode
        elif p == "anthropic":
            os.environ["ANTHROPIC_MODEL"] = mode
        elif p == "openai":
            os.environ["OPENAI_MODEL"] = mode
        print(f"  CLI override: model={mode}")
    if multistep in ("on", "off"):
        os.environ["AI_MULTI_STEP"] = multistep
        print(f"  CLI override: AI_MULTI_STEP={multistep}")
    if multistep_thr is not None:
        try:
            int(multistep_thr)
            os.environ["AI_MULTI_STEP_THRESHOLD"] = multistep_thr
            print(f"  CLI override: AI_MULTI_STEP_THRESHOLD={multistep_thr}")
        except ValueError:
            pass


def get_model_display_name() -> str:
    """Return human-readable provider/model for PDF content (e.g. 'ollama / tinyllama:latest')."""
    if DUMMY_ANALYSIS:
        return "dummy"
    provider = os.environ.get("AI_PROVIDER", "anthropic").lower()
    if provider == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
    elif provider == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
    elif provider == "openai":
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    else:
        model = "unknown"
    return f"{provider} / {model}"


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

# When True: skip AI calls, use debug input files, output xlsx/pdf with _DEBUG suffix
DUMMY_ANALYSIS = False

# When True: use real LLM but debug input files only; output with _DEBUG suffix (quick sanity check)
QUICK_ANALYSIS = False

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def load_env_keys():
    """Load API keys from local env.txt and MCP server dist folders."""
    global TIINGO_KEY, ALPACA_KEY, ALPACA_SECRET, TR_PHONE, TR_PIN

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
    else:
        print("Warning: No env.txt files found in any search locations.")
