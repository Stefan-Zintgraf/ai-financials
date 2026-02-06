"""Backward-compatible entry point. All logic lives in the sibling modules."""
import sys
import asyncio
import signal

import config
from utils import handle_sigint
from orchestrator import main

signal.signal(signal.SIGINT, handle_sigint)

if __name__ == "__main__":
    if "--dummy-analysis" in sys.argv:
        config.DUMMY_ANALYSIS = True
        print("[DUMMY] AI analysis disabled -- generating placeholder results.")
        print("[DUMMY] Using debug input files if present (Open_Positions_Debug.xlsx, Watch_Positions_Debug.xlsx).")

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nUnexpected error: {e}")
