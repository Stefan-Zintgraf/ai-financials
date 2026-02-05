import anthropic
import asyncio
import os

async def test_models():
    # Load key
    api_key = None
    with open("env.txt", "r") as f:
        for line in f:
            if "ANTHROPIC_API_KEY=" in line:
                api_key = line.split("=", 1)[1].strip()
    
    if not api_key:
        print("❌ No API Key found")
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)
    # Models to test in order of preference
    models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-latest",
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229"
    ]
    
    print("Suchen nach funktionierendem Modell...")
    for model in models:
        try:
            print(f"Testen: {model}...", end="", flush=True)
            await client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print(" ✅ ERFOLG!")
            return model
        except Exception as e:
            print(f" ❌ FEHLER ({e})")
    
    return None

if __name__ == "__main__":
    asyncio.run(test_models())
