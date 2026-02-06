---
name: newstrader-testing
description: When testing, debugging, fixing, or running a test of the NewsTrader pipeline, use --dummy-analysis to skip real AI API calls. Use when the user asks to test the script, debug the script, fix bugs, run the pipeline, or execute AnalyzePortfolio_Pipeline.
---

# NewsTrader Pipeline Testing

When running or testing `AnalyzePortfolio_Pipeline.py` (or any script that invokes the pipeline), always pass the `--dummy-analysis` flag:

```bash
python AnalyzePortfolio_Pipeline.py --dummy-analysis
```

This skips real Anthropic API calls and generates deterministic dummy results instead. This saves time, money, and avoids rate limits during development and debugging.

In dummy mode, the pipeline also uses `Open_Positions_Debug.xlsx` and `Watch_Positions_Debug.xlsx` (if they exist) instead of the production input files.

Never run the pipeline without `--dummy-analysis` unless the user explicitly asks for a real/live analysis run.
