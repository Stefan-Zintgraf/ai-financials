---
name: newstrader-testing
description: When testing the NewsTrader pipeline, run real LLM (--quick-analysis) or dummy (--dummy-analysis) mode. Ask which mode only if the user does not clearly specify. Use when the user asks to test the script, debug the script, fix bugs, run the pipeline, or execute AnalyzePortfolio_Pipeline.
---

# NewsTrader Pipeline Testing

If the user clearly specifies which mode (e.g. "quick test with real model", "real LLM", "dummy", "simulated", "no AI"), run that mode directly. Otherwise, ask: **"Which test mode? (a) Real LLM – to check prompts or model behavior; (b) Dummy – no AI, test data flow, Excel, PDF, etc."**

Run (from NewsTrader root, with venv):

- **a** → `cd Scripts && . .venv/bin/activate && python AnalyzePortfolio_Pipeline.py --quick-analysis`
- **b** → `cd Scripts && . .venv/bin/activate && python AnalyzePortfolio_Pipeline.py --dummy-analysis`

**Real LLM** (`--quick-analysis`): Uses debug input files, real AI calls. For testing prompt changes or model integration.

**Dummy** (`--dummy-analysis`): Skips AI, uses placeholder results. For testing data flow, reports, news aggregation, etc.

Never run a full production run (no flags) unless the user explicitly asks for it.
