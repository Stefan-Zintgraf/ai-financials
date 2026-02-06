"""Generic LLM provider abstraction supporting Anthropic, OpenAI, and Ollama via LangChain.

Settings read from os.environ (populated from env.txt by config.load_env_keys):
  AI_PROVIDER      = anthropic | openai | ollama   (default: anthropic)
  ANTHROPIC_MODEL / OPENAI_MODEL / OLLAMA_MODEL   (model per provider)
  ANTHROPIC_API_KEY / OPENAI_API_KEY              (required for cloud providers)
  OLLAMA_BASE_URL                                 (optional; auto-detected if not set)
"""
import os
import re
from typing import Type, TypeVar

import httpx
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

_LLM = None
_PROVIDER = None
_CONTEXT_SIZE: int | None = None

OLLAMA_MAC_PORT = 12434
OLLAMA_WIN_PORT = 11434

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def _ollama_host():
    """Return host -- Docker-aware."""
    in_docker = os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")
    return "http://host.docker.internal" if in_docker else "http://localhost"


def _fetch_ollama_models(base_url, timeout=5.0):
    """Return (reachable, model_names)."""
    try:
        r = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=timeout)
        r.raise_for_status()
        return True, [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return False, []


def _fetch_ollama_context_size(base_url: str, model: str) -> int | None:
    """Query Ollama /api/show for the model's num_ctx. Returns None on failure."""
    try:
        r = httpx.post(
            f"{base_url.rstrip('/')}/api/show",
            json={"model": model},
            timeout=5.0,
        )
        r.raise_for_status()
        data = r.json()
        params = data.get("parameters", "")
        if isinstance(params, str):
            match = re.search(r"num_ctx\s+(\d+)", params)
            if match:
                return int(match.group(1))
        model_info = data.get("model_info", {})
        if isinstance(model_info, dict):
            for key, val in model_info.items():
                if "context_length" in key.lower() and isinstance(val, int):
                    return val
        return None
    except Exception:
        return None


def get_model_context_size() -> int | None:
    """Return cached model context size (Ollama only). None for other providers or on failure."""
    return _CONTEXT_SIZE


def _resolve_ollama_url(model):
    """Resolve Ollama base URL: explicit env, then MAC (GPU), then Windows."""
    explicit = os.environ.get("OLLAMA_BASE_URL", "").strip()
    if explicit:
        reachable, names = _fetch_ollama_models(explicit)
        if not reachable:
            raise RuntimeError(f"Ollama not reachable at {explicit}")
        if model and model not in names:
            raise ValueError(
                f"Model '{model}' not found at {explicit}. Pull: ollama pull {model}"
            )
        return explicit.rstrip("/")

    host = _ollama_host()
    for port, label in [(OLLAMA_MAC_PORT, "MAC/GPU"), (OLLAMA_WIN_PORT, "Windows")]:
        url = f"{host}:{port}"
        reachable, names = _fetch_ollama_models(url)
        if reachable and (not model or model in names):
            print(f"  Using Ollama on {label} (port {port}).")
            return url
    raise RuntimeError("Ollama not reachable. Set OLLAMA_BASE_URL in env.txt.")


def init_llm():
    global _LLM, _PROVIDER, _CONTEXT_SIZE
    _PROVIDER = os.environ.get("AI_PROVIDER", "anthropic").lower()
    _CONTEXT_SIZE = None

    if _PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic

        model = os.environ.get("ANTHROPIC_MODEL") or "claude-3-5-haiku-latest"
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set in env.txt")
        _LLM = ChatAnthropic(anthropic_api_key=api_key, model=model)

    elif _PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        model = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in env.txt")
        _LLM = ChatOpenAI(api_key=api_key, model=model)

    elif _PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        model = os.environ.get("OLLAMA_MODEL") or "llama3"
        base_url = _resolve_ollama_url(model)
        _LLM = ChatOllama(model=model, base_url=base_url)
        ctx = _fetch_ollama_context_size(base_url, model)
        if ctx is not None:
            _CONTEXT_SIZE = ctx
            print(f"  Model context size: {ctx} tokens")

    else:
        raise ValueError(f"Unknown AI_PROVIDER: {_PROVIDER}")

    print(f"  LLM initialized: provider={_PROVIDER}, model={model}")


def _bind_kwargs(tokens: int, temperature: float | None = None):
    """Return bind kwargs for token limit and optional temperature."""
    if _PROVIDER == "ollama":
        opts = {"num_predict": tokens}
        if temperature is not None:
            opts["temperature"] = temperature
        return {"options": opts}
    out = {"max_tokens": tokens}
    if temperature is not None:
        out["temperature"] = temperature
    return out


async def verify_llm():
    """Send a minimal test prompt to confirm the model is reachable and responds.
    Raises RuntimeError with a clear message on failure.
    Must be awaited (or wrapped in asyncio.run() from sync code)."""
    if _LLM is None:
        raise RuntimeError("LLM not initialized -- call init_llm() first")
    try:
        bound = _LLM.bind(**_bind_kwargs(5))
        await bound.ainvoke([HumanMessage(content="Say OK")])
        print(f"  LLM verified: {_PROVIDER} responded OK.")
    except Exception as e:
        raise RuntimeError(
            f"LLM verification failed ({_PROVIDER}): {e}\n"
            "  Check your API key, model name, and network connectivity in env.txt."
        ) from e


async def ainvoke(
    prompt: str, max_tokens: int = 1000, temperature: float | None = None
) -> str:
    if _LLM is None:
        raise RuntimeError("LLM not initialized -- call init_llm() first")
    bound = _LLM.bind(**_bind_kwargs(max_tokens, temperature))
    response = await bound.ainvoke([HumanMessage(content=prompt)])
    return response.content


async def ainvoke_retry(prompt: str, max_tokens: int = 400) -> str:
    """Retry with lower temperature and smaller output. Last-resort fallback."""
    return await ainvoke(prompt, max_tokens=max_tokens, temperature=0.3)


async def ainvoke_structured(
    prompt: str, schema: Type[SchemaT], max_tokens: int = 1000
) -> dict | None:
    """Invoke LLM with structured output. Returns dict on success, None on failure."""
    if _LLM is None:
        raise RuntimeError("LLM not initialized -- call init_llm() first")
    try:
        structured_llm = _LLM.with_structured_output(schema)
        bound = structured_llm.bind(**_bind_kwargs(max_tokens))
        result = await bound.ainvoke([HumanMessage(content=prompt)])
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, dict):
            return result
        return dict(result) if result is not None else None
    except Exception:
        return None
