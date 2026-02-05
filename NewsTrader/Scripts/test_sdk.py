import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    print("Testing Claude SDK...")
    options = ClaudeAgentOptions(permission_mode="acceptEdits")
    try:
        async for message in query(prompt="Sag Hallo.", options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"Antwort: {block.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
