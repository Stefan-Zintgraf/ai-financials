---
name: newstrader-model-check
description: When testing model connectivity, verifying the LLM is reachable, or checking if the AI provider works, use --model-check. Use when the user asks to test model connectivity, verify the model, check if the model responds, or debug LLM availability.
---

# NewsTrader Model Connectivity Check

When testing whether the configured LLM (Anthropic, OpenAI, or Ollama) is reachable and responding, activate the venv and run:

```bash
cd Scripts && . .venv/bin/activate && python AnalyzePortfolio_Pipeline.py --model-check
```

This loads env.txt, initializes the LLM, sends a minimal "Say OK" test prompt, and exits. No portfolio analysis is performed.

Use this instead of running the full pipeline when the user wants to verify model connectivity or debug LLM configuration.
