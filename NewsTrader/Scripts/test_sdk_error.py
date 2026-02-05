"""
Test script to isolate the claude_agent_sdk error
"""
import sys
import os
import asyncio
from datetime import datetime

# Add MCP paths
MCP_BASE = r"C:\Users\HMz\Documents\Source\McpServer"
sys.path.append(os.path.join(MCP_BASE, "tiingo-mcp-server"))

# Test 1: Direct Tiingo import (should work)
print("=" * 60)
print("TEST 1: Direct Tiingo API call (no SDK)")
print("=" * 60)
try:
    from tiingo_mcp_server.tiingo_functions import get_news_sync as tiingo_get_news
    news = tiingo_get_news(tickers=["AAPL"], limit=3)
    print(f"✅ Tiingo direct call works! Got {len(news) if news else 0} news items")
    if news:
        print(f"   First headline: {news[0].get('title', 'N/A')}")
except Exception as e:
    print(f"❌ Tiingo direct call failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: claude_agent_sdk import
print("\n" + "=" * 60)
print("TEST 2: Import claude_agent_sdk")
print("=" * 60)
try:
    from claude_agent_sdk import query, ClaudeAgentOptions
    print("✅ claude_agent_sdk imported successfully")
except Exception as e:
    print(f"❌ claude_agent_sdk import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Simple SDK query (no tools)
print("\n" + "=" * 60)
print("TEST 3: Simple SDK query (no tools)")
print("=" * 60)

async def test_simple_query():
    try:
        prompt = "Say 'Hello' and return JSON: {\"status\": \"ok\"}"
        options = ClaudeAgentOptions(allowed_tools=[])
        
        response_text = ""
        print("   Sending query...")
        async for msg in query(prompt=prompt, options=options):
            if hasattr(msg, 'content'):
                for block in msg.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
        
        print(f"✅ Simple query works! Response: {response_text[:100]}")
        return True
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 4: SDK query with search_web tool
print("\n" + "=" * 60)
print("TEST 4: SDK query with search_web tool")
print("=" * 60)

async def test_tool_query():
    try:
        prompt = "Search for 'Apple stock news' and return the first headline as JSON: {\"headline\": \"...\"}"
        options = ClaudeAgentOptions(allowed_tools=["search_web"])
        
        response_text = ""
        print("   Sending query with tool...")
        async for msg in query(prompt=prompt, options=options):
            if hasattr(msg, 'content'):
                for block in msg.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
        
        print(f"✅ Tool query works! Response: {response_text[:100]}")
        return True
    except Exception as e:
        print(f"❌ Tool query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run tests
async def main():
    print("\n" + "=" * 60)
    print("RUNNING ASYNC TESTS")
    print("=" * 60)
    
    result1 = await test_simple_query()
    print(f"\nTest 3 result: {'PASS' if result1 else 'FAIL'}")
    
    if result1:
        result2 = await test_tool_query()
        print(f"Test 4 result: {'PASS' if result2 else 'FAIL'}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("If Test 3 fails: claude_agent_sdk has a general problem")
    print("If Test 4 fails: MCP tool integration is the issue")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
