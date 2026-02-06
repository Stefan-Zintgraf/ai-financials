"""Backward-compatible entry point. All logic lives in the sibling modules."""
import sys
import asyncio
import signal

import config
import llm_provider
from utils import handle_sigint
from orchestrator import main

signal.signal(signal.SIGINT, handle_sigint)

if __name__ == "__main__":
    if "--dummy-analysis" in sys.argv:
        config.DUMMY_ANALYSIS = True
        print("[DUMMY] AI analysis disabled -- generating placeholder results.")
        print("[DUMMY] Using debug input files if present (Open_Positions_Debug.xlsx, Watch_Positions_Debug.xlsx).")

    if "--quick-analysis" in sys.argv:
        config.QUICK_ANALYSIS = True
        print("[QUICK] Using real LLM with debug input files only (Open_Positions_Debug.xlsx, Watch_Positions_Debug.xlsx).")

    if "--model-check" in sys.argv:
        print("Model check: loading env.txt and verifying LLM...")
        config.load_env_keys()
        config.apply_cli_overrides()
        try:
            llm_provider.init_llm()
            asyncio.run(llm_provider.verify_llm())
            print("Model check PASSED.")
        except Exception as e:
            print(f"Model check FAILED: {e}")
            sys.exit(1)
        sys.exit(0)

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nUnexpected error: {e}")
