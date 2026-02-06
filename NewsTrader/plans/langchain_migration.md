# LangChain Migration Strategy

Migration from Anthropic SDK to LangChain for `AnalyzePortfolio_Pipeline.py`.

---

## Overview

The pipeline currently uses `anthropic.AsyncAnthropic` directly for two AI use cases:

1. **`troubleshoot_no_price`** – AI advice when price lookup fails (model: `claude-3-5-haiku-latest`, max_tokens: 150)
2. **`analyze_data`** – Portfolio analysis and trading recommendations (model: `claude-3-haiku-20240307`, max_tokens: 1000)

---

## 1. Dependencies

### Remove
- `anthropic`

### Add
- `langchain-anthropic` – Anthropic integration for LangChain
- `langchain-core` – Core abstractions (messages, etc.)

### requirements.txt
```
langchain-anthropic>=0.2.0
langchain-core>=0.3.0
```

---

## 2. Imports

| Current | New |
|---------|-----|
| `import anthropic` | `from langchain_anthropic import ChatAnthropic` |
| — | `from langchain_core.messages import HumanMessage` |

---

## 3. Client Initialization

**Location:** `load_env_keys()` (around lines 136–179)

| Current | New |
|---------|-----|
| `ANTHROPIC_CLIENT = anthropic.AsyncAnthropic(api_key=api_key)` | `LLM = ChatAnthropic(anthropic_api_key=api_key, model="claude-3-haiku-20240307", max_tokens=1000)` |

**Notes:**
- Use a single `LLM` instance for the main analysis.
- For `troubleshoot_no_price` (different model/max_tokens), either:
  - Create a second instance: `LLM_TROUBLESHOOT = ChatAnthropic(..., model="claude-3-5-haiku-latest", max_tokens=150)`, or
  - Use `.with_config()` / `.bind()` if supported for per-call overrides.

---

## 4. Call Pattern Changes

### Anthropic SDK (current)
```python
response = await ANTHROPIC_CLIENT.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)
response_text = response.content[0].text
```

### LangChain (target)
```python
response = await LLM.ainvoke([HumanMessage(content=prompt)])
response_text = response.content
```

---

## 5. Affected Functions

### 5.1 `troubleshoot_no_price` (lines ~518–524)

- Replace `ANTHROPIC_CLIENT.messages.create(...)` with `LLM.ainvoke([HumanMessage(content=prompt)])`
- Replace `response.content[0].text.strip()` with `response.content.strip()`
- Use `LLM_TROUBLESHOOT` if a separate instance is created for this use case

### 5.2 `analyze_data` (lines ~1025–1038)

- Replace `if not ANTHROPIC_CLIENT` with `if not LLM`
- Replace `"Anthropic Client not initialized"` with `"LLM not initialized"`
- Replace `ANTHROPIC_CLIENT.messages.create(...)` with `LLM.ainvoke([HumanMessage(content=prompt)])`
- Replace `response.content[0].text` with `response.content`

---

## 6. Global Variable Rename

| Current | New |
|---------|-----|
| `ANTHROPIC_CLIENT` | `LLM` (or `LLM_ANALYSIS`) |

Update all references in:
- `load_env_keys()`
- `troubleshoot_no_price()`
- `analyze_data()`

---

## 7. Error Handling

- Keep existing `try/except` blocks.
- LangChain may raise different exceptions; consider catching `langchain_core.exceptions` if needed.
- Preserve current fallback behavior (e.g. returning `None` or `{}`).

---

## 8. Testing Checklist

- [ ] `load_env_keys()` initializes LLM when `ANTHROPIC_API_KEY` is set
- [ ] `troubleshoot_no_price` returns AI advice when price lookup fails
- [ ] `analyze_data` returns valid JSON with `Empfehlung`, `Begründung`, etc.
- [ ] JSON parsing and cleaning logic still works with LangChain output
- [ ] Pipeline runs end-to-end for portfolio and watchlist
- [ ] PDF generation and Excel export unchanged

---

## 9. Rollback

If issues occur:
1. Revert imports and client initialization
2. Restore `anthropic` in `requirements.txt`
3. Revert call sites in `troubleshoot_no_price` and `analyze_data`

---

## 10. Optional Future Enhancements

After migration, LangChain enables:
- **Chains** – Structured multi-step flows
- **Agents** – Tool use (e.g. Tiingo, Alpaca) for richer analysis
- **Output parsers** – Structured output (e.g. Pydantic) instead of manual JSON parsing
- **Prompt templates** – Reusable prompts with variables
