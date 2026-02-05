import asyncio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')


async def ask_claude():
    # Erste Frage: US-Aktien aus cTrader als Liste für Download
    question1 = "hole alle aktien symbole mit .us trailer aber OHNE -24 über ctrader mcp server user account 5122894. Gib die komplette Liste als CSV aus (nur Symbol pro Zeile) damit ich sie downloaden kann."

    # Zweite Frage: Nachrichten analysieren
    question2 = "lese aktuelle nachrichten von tiingo mcp server und alpaca mcp server und analysiere, welche der 3, besten us aktien am ehesten für einen kauf geeignet sind"

    options = ClaudeAgentOptions(
        mcp_servers={
            "ctrader": {
                "command": r"C:\Users\HMz\AppData\Local\Programs\Python\Python313\python.exe",
                "args": [
                    r"C:\Users\HMz\Documents\Source\McpServer\ctrader-mcp-server\server.py",
                    "--transport",
                    "stdio"
                ],
                "env": {}
            },
            "tiingo": {
                "command": r"C:\Users\HMz\AppData\Local\Programs\Python\Python313\python.exe",
                "args": [
                    r"C:\Users\HMz\Documents\Source\McpServer\tiingo-mcp-server\server.py"
                ],
                "env": {}
            },
            "alpaca": {
                "command": r"C:\Users\HMz\AppData\Local\Programs\Python\Python313\python.exe",
                "args": [
                    r"C:\Users\HMz\Documents\Source\McpServer\alpaca-mcp-server\src\alpaca_mcp_server\server.py",
                    "--transport",
                    "stdio"
                ],
                "env": {}
            }
        },
        allowed_tools=["mcp__ctrader__*", "mcp__tiingo__*", "mcp__alpaca__*"],
        permission_mode="acceptEdits"
    )

    # Erste Anfrage
    print("=== Frage 1: US-Aktien aus cTrader ===\n")
    async for message in query(prompt=question1, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

    print("\n" + "="*50 + "\n")

    # Zweite Anfrage
    print("=== Frage 2: Nachrichten-Analyse für Kaufempfehlung ===\n")
    async for message in query(prompt=question2, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(ask_claude())
