"""Runs --model-check per enabled provider and each model. Skips if API key missing."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_helpers import report, skip, load_test_config


def _has_api_key(provider: str) -> bool:
    if provider == "ollama":
        return True
    if provider == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config")
    parser.add_argument("--filter", default=None, help="Filter: PROVIDER/MODEL for single check")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent

    # Load env for API key check (config.load_env_keys)
    sys.path.insert(0, str(script_dir))
    import config
    config.load_env_keys()

    if args.filter:
        parts = args.filter.split("/")
        if len(parts) != 2:
            print(f"Invalid --filter for model_check: expected PROVIDER/MODEL, got {args.filter}")
            return 1
        provider, model = parts[0].lower(), parts[1]
        providers_config = {provider: True}
        models_config = {provider: [model]}
    else:
        config_path = args.config or (Path(__file__).resolve().parent / "test.config")
        cp = load_test_config(config_path)
        providers_config = {}
        if cp.has_section("providers"):
            for p in ("ollama", "anthropic", "openai"):
                providers_config[p] = cp.getboolean("providers", p, fallback=False)
        models_config = {}
        if cp.has_section("models"):
            for p in ("ollama", "anthropic", "openai"):
                val = cp.get("models", p, fallback="")
                models_config[p] = [m.strip() for m in val.split(",") if m.strip()]

    failed = 0
    for provider, enabled in providers_config.items():
        if not enabled:
            continue
        models = models_config.get(provider, [])
        if not models:
            models = ["llama3.2:1b"] if provider == "ollama" else []
        for model in models:
            name = f"{provider}/{model}_model_check"
            if not _has_api_key(provider):
                skip(name, f"API key not set for {provider}")
                continue
            cmd = [
                sys.executable, "AnalyzePortfolio_Pipeline.py",
                "--quick-analysis", "--model-check",
                f"--provider={provider}", f"--mode={model}",
            ]
            if args.dry_run:
                print(f"Would run: {' '.join(cmd)}")
                continue
            try:
                result = subprocess.run(
                    cmd,
                    cwd=script_dir,
                    capture_output=True,
                    text=True,
                    timeout=args.timeout,
                    env=os.environ.copy(),
                )
            except subprocess.TimeoutExpired:
                report(name, False, "Timeout")
                failed += 1
                continue
            except Exception as e:
                report(name, False, str(e))
                failed += 1
                continue
            if result.returncode == 0:
                report(name, True, "OK")
            else:
                err = (result.stderr or result.stdout or "")[:200]
                report(name, False, f"Exit {result.returncode}: {err}")
                failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
