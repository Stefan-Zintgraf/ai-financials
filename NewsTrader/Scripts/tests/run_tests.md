# NewsTrader Test Suite

## Overview

The test suite validates the AnalyzePortfolio pipeline and its components. It consists of:

- **run_tests.py** – Orchestrator that discovers and runs sub-tests, writes `test_results.md`
- **run_all_tests.py** – Runs numbered single tests via `run_tests.py --run`, writes `run_all_tests_results.md`
- **test_*.py** – Individual test modules
- **test.config** – INI configuration for which tests to run (used only when not using `--run`)

## Quick Start

```bash
# Run all enabled tests from test.config
python run_tests.py

# Fast smoke test (no LLM, no network, no config needed)
python run_tests.py --run=unit_ai_analysis,dummy_pipeline

# Preview what would run
python run_tests.py --dry-run
```

## CLI Reference

| Flag | Description |
|------|-------------|
| `--dry-run` | Print what would run without executing |
| `--stop-on-failure` | Stop after first failure |
| `--free-models` | Only test ollama provider (overrides test.config providers) |
| `--run=<spec>` | Run only specified test(s); **bypasses test.config entirely** |

### --run Filter Syntax

With `--run`, the config file is not loaded. All parameters must be specified explicitly.

- **Module names**: `unit_ai_analysis`, `dummy_pipeline`, `model_check`, `pipeline`, `error_handling`, `data_providers`
- **Separator**: `/` (slash) – used instead of dot because model names can contain dots (e.g. `llama3.2:1b`)
- **Comma-separated**: Multiple tests can be run in one invocation

**Parameter requirements:**

| Module | Parameters | Example |
|--------|------------|---------|
| unit_ai_analysis | none | `--run=unit_ai_analysis` |
| dummy_pipeline | none | `--run=dummy_pipeline` |
| model_check | PROVIDER/MODEL | `--run=model_check/ollama/mistral:latest` |
| pipeline | PROVIDER/MODEL/MULTISTEP[/THR] | `--run=pipeline/ollama/mistral:latest/on/4096` |
| pipeline (multistep off) | PROVIDER/MODEL/off | `--run=pipeline/ollama/mistral:latest/off` |
| error_handling | none | `--run=error_handling` |
| data_providers | none | `--run=data_providers` |

For `pipeline` with `multistep=on`, the threshold is required: `PROVIDER/MODEL/on/THRESHOLD`.

## Configuration File (test.config)

When running without `--run`, `tests/test.config` is loaded. Sections:

### [general]

- `stop_on_failure` – Stop after first failure (default: false)
- `timeout` – Max seconds per pipeline subprocess (default: 300)

### [tests]

Enable/disable test modules (true/false):

- `unit_ai_analysis` – Pure-function unit tests for ai_analysis.py
- `dummy_pipeline` – Pipeline with --dummy-analysis, no LLM
- `model_check` – LLM connectivity check per provider/model
- `pipeline` – Full analysis pipeline with deep validation (most expensive)
- `error_handling` – Invalid inputs and error-path tests
- `data_providers` – Network smoke tests (forex, news, Tiingo)

When `pipeline=false`, no provider/model/multistep combinations are tested; only the other modules run.

### [providers]

Which providers to include: `ollama`, `anthropic`, `openai` (each true/false).

### [models]

Comma-separated models per provider, e.g. `ollama = tinyllama:latest, mistral:latest`.

### [multistep]

- `vary` – Test both multistep=on and off
- `thresholds` – Comma-separated values when multistep=on (e.g. 4096, 8192)

## Test Modules

| Module | What it tests | Needs |
|--------|---------------|-------|
| unit_ai_analysis | ai_analysis.py pure functions (regex, parse, validate) | Nothing |
| dummy_pipeline | Pipeline with --dummy-analysis; Excel, PDF, log | Debug input files |
| model_check | LLM connectivity per provider/model | API keys (or Ollama) |
| pipeline | Full analysis; parse failures, recommendations, Excel | API keys, LLM |
| error_handling | Invalid provider, missing env | env.txt for restore |
| data_providers | Forex, Google News, Tiingo | Network, optional keys |

## Output

Results are written to `tests/test_results.md`:

- **Summary table** – One row per module with OK/FAILED/SKIPPED
- **Details** – PASS/FAIL/SKIP lines for each sub-test

## Examples

```bash
# Run everything (config-driven)
python run_tests.py

# Fast smoke test (no LLM, no network, no config needed)
python run_tests.py --run=unit_ai_analysis,dummy_pipeline

# Test only free/local models (config-driven, overrides providers)
python run_tests.py --free-models

# Check if a specific model connects
python run_tests.py --run=model_check/ollama/mistral:latest

# Single pipeline test for debugging
python run_tests.py --run=pipeline/ollama/mistral:latest/on/4096

# Pipeline test without multistep
python run_tests.py --run=pipeline/anthropic/claude-3-5-haiku-latest/off

# Model with dot in name (unambiguous thanks to slash separator)
python run_tests.py --run=pipeline/ollama/llama3.2:1b/on/4096

# Multiple specific tests in one run
python run_tests.py --run=unit_ai_analysis,model_check/ollama/llama3.2:1b,pipeline/ollama/mistral:latest/off

# Preview what config-driven run would execute
python run_tests.py --dry-run

# Run numbered single tests (output: run_all_tests_results.md)
python run_all_tests.py                    # All 24 tests
python run_all_tests.py --test=1,4,12      # Tests 1, 4, 12 only
python run_all_tests.py --list             # List all numbered tests
```
