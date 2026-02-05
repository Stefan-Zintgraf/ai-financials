import sys
import os
import asyncio
import json
from claude_agent_sdk import query, ClaudeAgentOptions

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("🚀 Test Script: IBKR Connection Check")

    # Hardcoded IBKR Configuration (Copy from AnalyzePortfolio.py)
    active_port = 4001
    active_mode = 'gateway-live'

    print(f"🔒 IBKR Modus fixiert auf: {active_mode} (Port {active_port})")

    # Force IBKR Configuration
    os.environ["IB_GATEWAY_HOST"] = "127.0.0.1"
    os.environ["IB_GATEWAY_PORT"] = str(active_port)
    os.environ["IB_GATEWAY_CLIENT_ID"] = "997" # Different ID for test
    
    # Prepare Environment for Subprocess
    subprocess_env = dict(os.environ)
    subprocess_env["PYTHONIOENCODING"] = "utf-8"

    # Options (Copied from AnalyzePortfolio.py, reduced to IBKR only)
    options = ClaudeAgentOptions(
        mcp_servers={
            "ibkr": {
                "command": r"C:\Users\HMz\AppData\Local\Programs\Python\Python313\python.exe",
                "args": [r"C:\Users\HMz\Documents\Source\McpServer\ibapi-mcp-server\gateway_server.py"],
                "env": subprocess_env
            }
        },
        allowed_tools=["mcp__ibkr__*"],
        permission_mode="acceptEdits"
    )

    print("--- Initializing Connection Mode ---")
    
    # 1. Set Connection Mode Explicitly via Tool Call
    # We construct a prompt that forces the tool call.
    init_prompt = f"""
    Bitte konfiguriere die IBKR Verbindung.
    Rufe das Tool `mcp__ibkr__set_connection_mode_tool` auf mit:
    - mode: '{active_mode}'
    - port: {active_port}
    
    Danach, rufe `mcp__ibkr__ibkr_get_mid_price_tool` für 'AAPL' auf.
    Gib mir das Ergebnis zurück.
    """

    print("--- Sending Query ---")
    full_response = ""
    try:
        async for message in query(prompt=init_prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        full_response += block.text
                        print(block.text, end="", flush=True) # Stream text
                    
                    if hasattr(block, 'name') and hasattr(block, 'input'):
                         print(f"\n  [Tool Call] {block.name}: {block.input}", flush=True)

    except Exception as e:
        print(f"\n❌ Error during query: {e}")

    print("\n--- Done ---")

if __name__ == "__main__":
    asyncio.run(main())
