"""Run numbered single tests via run_tests.py --run. Writes run_all_tests_results.md.

Each single test is one invocation of run_tests.py --run=<spec>. Use --test=1,4,12
to run specific tests; omit --test to run all.

Usage:
  python run_all_tests.py                    # Run all numbered tests
  python run_all_tests.py --test=1,4,12      # Run tests 1, 4, and 12
  python run_all_tests.py --list             # List all tests and exit
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = TESTS_DIR.parent
RUN_TESTS = TESTS_DIR / "run_tests.py"
OUTPUT_FILE = TESTS_DIR / "run_all_tests_results.md"

# Numbered test catalog (matches default test.config: providers, models, multistep)
# Each entry: (number, run_spec, short_description)
TEST_CATALOG: list[tuple[int, str, str]] = [
    (1, "unit_ai_analysis", "Unit tests for ai_analysis.py"),
    (2, "dummy_pipeline", "Pipeline with --dummy-analysis"),
    (3, "error_handling", "Invalid inputs and error-path tests"),
    (4, "data_providers", "Network smoke tests (forex, news, Tiingo)"),
    (5, "model_check/ollama/tinyllama:latest", "Model check: ollama/tinyllama"),
    (6, "model_check/ollama/llama3.2:1b", "Model check: ollama/llama3.2:1b"),
    (7, "model_check/ollama/mistral:latest", "Model check: ollama/mistral"),
    (8, "model_check/anthropic/claude-3-5-haiku-latest", "Model check: anthropic/claude-3-5-haiku"),
    (9, "model_check/openai/gpt-4o-mini", "Model check: openai/gpt-4o-mini"),
    (10, "pipeline/ollama/tinyllama:latest/off", "Pipeline: ollama/tinyllama multistep=off"),
    (11, "pipeline/ollama/tinyllama:latest/on/4096", "Pipeline: ollama/tinyllama multistep=on/4096"),
    (12, "pipeline/ollama/tinyllama:latest/on/8192", "Pipeline: ollama/tinyllama multistep=on/8192"),
    (13, "pipeline/ollama/llama3.2:1b/off", "Pipeline: ollama/llama3.2:1b multistep=off"),
    (14, "pipeline/ollama/llama3.2:1b/on/4096", "Pipeline: ollama/llama3.2:1b multistep=on/4096"),
    (15, "pipeline/ollama/llama3.2:1b/on/8192", "Pipeline: ollama/llama3.2:1b multistep=on/8192"),
    (16, "pipeline/ollama/mistral:latest/off", "Pipeline: ollama/mistral multistep=off"),
    (17, "pipeline/ollama/mistral:latest/on/4096", "Pipeline: ollama/mistral multistep=on/4096"),
    (18, "pipeline/ollama/mistral:latest/on/8192", "Pipeline: ollama/mistral multistep=on/8192"),
    (19, "pipeline/anthropic/claude-3-5-haiku-latest/off", "Pipeline: anthropic/claude multistep=off"),
    (20, "pipeline/anthropic/claude-3-5-haiku-latest/on/4096", "Pipeline: anthropic/claude multistep=on/4096"),
    (21, "pipeline/anthropic/claude-3-5-haiku-latest/on/8192", "Pipeline: anthropic/claude multistep=on/8192"),
    (22, "pipeline/openai/gpt-4o-mini/off", "Pipeline: openai/gpt-4o-mini multistep=off"),
    (23, "pipeline/openai/gpt-4o-mini/on/4096", "Pipeline: openai/gpt-4o-mini multistep=on/4096"),
    (24, "pipeline/openai/gpt-4o-mini/on/8192", "Pipeline: openai/gpt-4o-mini multistep=on/8192"),
]

NUM_TO_SPEC = {num: spec for num, spec, _ in TEST_CATALOG}
NUM_TO_DESC = {num: desc for num, _, desc in TEST_CATALOG}


def parse_test_arg(s: str) -> list[int]:
    """Parse --test=1,4,12 into [1, 4, 12]."""
    if not s or not s.strip():
        return []
    nums = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            n = int(part)
            if n not in NUM_TO_SPEC:
                sys.exit(f"Unknown test number: {n}. Valid: 1-{len(TEST_CATALOG)}")
            nums.append(n)
        except ValueError:
            sys.exit(f"Invalid test number: {part!r}")
    return sorted(set(nums))


def run_single(num: int, extra_args: list[str]) -> tuple[int, str, str]:
    """Run one test via run_tests.py --run=<spec>. Returns (exitcode, stdout, stderr)."""
    spec = NUM_TO_SPEC[num]
    cmd = [sys.executable, str(RUN_TESTS), f"--run={spec}"] + extra_args
    result = subprocess.run(
        cmd,
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def main():
    parser = argparse.ArgumentParser(
        description="Run numbered single tests via run_tests.py --run. Output: run_all_tests_results.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    Run all 24 tests
  python run_all_tests.py --test=1,4,12      Run tests 1, 4, 12
  python run_all_tests.py --list             List all tests
  python run_all_tests.py --test=1,2 --dry-run   Preview (no execution)
""",
    )
    parser.add_argument("--test", metavar="N,M,...", help="Run only tests N, M, ... (e.g. 1,4,12)")
    parser.add_argument("--list", action="store_true", help="List all numbered tests and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run without executing")
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop after first failure")
    args = parser.parse_args()

    if args.list:
        print("Numbered test catalog:")
        for num, spec, desc in TEST_CATALOG:
            print(f"  {num:2d}: {spec}")
            print(f"      {desc}")
        return 0

    extra = []
    if args.dry_run:
        extra.append("--dry-run")
    if args.stop_on_failure:
        extra.append("--stop-on-failure")

    if args.test:
        to_run = parse_test_arg(args.test)
    else:
        to_run = [num for num, _, _ in TEST_CATALOG]

    if not to_run:
        print("No tests to run.", file=sys.stderr)
        return 0

    if args.dry_run:
        print("Would run:")
        for num in to_run:
            print(f"  {num}: {NUM_TO_SPEC[num]}")
        return 0

    results: list[tuple[int, str, int, str, str, dict | None]] = []
    failed_count = 0

    for i, num in enumerate(to_run, 1):
        spec = NUM_TO_SPEC[num]
        desc = NUM_TO_DESC[num]
        print(f"[{i}/{len(to_run)}] Test {num}: {spec} ...", flush=True)
        code, stdout, stderr = run_single(num, extra)
        llm_debug = None
        if spec.startswith("pipeline/"):
            llm_path = TESTS_DIR / "last_llm_debug.json"
            if llm_path.exists():
                try:
                    llm_debug = json.loads(llm_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
        results.append((num, spec, code, stdout, stderr, llm_debug))
        if code != 0:
            failed_count += 1
            if args.stop_on_failure:
                print(f"  FAILED (exit {code}). Stopping (--stop-on-failure).", flush=True)
                break
        else:
            print(f"  OK", flush=True)

    # Write run_all_tests_results.md
    lines = [
        f"# Run All Tests Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        "| # | Spec | Result |",
        "|---|------|--------|",
    ]
    for num, spec, code, _, _, _ in results:
        status = "FAIL" if code != 0 else "OK"
        lines.append(f"| {num} | `{spec}` | {status} |")
    lines.extend([
        "",
        f"**Total: {len(results)} run, {failed_count} failed**",
        "",
        "## Details",
        "",
    ])
    for num, spec, code, stdout, stderr, llm_debug in results:
        lines.append(f"### Test {num}: {spec}")
        lines.append("")
        if llm_debug:
            lines.append("**Model:** " + llm_debug.get("model", "—"))
            lines.append("")
            lines.append("**Multistep:** yes" if llm_debug.get("multistep") else "**Multistep:** no")
            lines.append("")
            entries = llm_debug.get("entries", [])
            if entries:
                # Use first asset's prompt/response
                ent = entries[0]
                if ent.get("multistep") and "steps" in ent:
                    for j, step in enumerate(ent["steps"], 1):
                        lines.append(f"**Input prompt (step {j}):**")
                        lines.append("```")
                        lines.append((step.get("prompt") or "")[:8000])  # cap length
                        if len(step.get("prompt") or "") > 8000:
                            lines.append("... [truncated]")
                        lines.append("```")
                        lines.append("")
                        lines.append(f"**Model answer (step {j}):**")
                        lines.append("```")
                        lines.append((step.get("response") or "")[:8000])
                        if len(step.get("response") or "") > 8000:
                            lines.append("... [truncated]")
                        lines.append("```")
                        lines.append("")
                else:
                    lines.append("**Input prompt:**")
                    lines.append("```")
                    lines.append((ent.get("prompt") or "")[:8000])
                    if len(ent.get("prompt") or "") > 8000:
                        lines.append("... [truncated]")
                    lines.append("```")
                    lines.append("")
                    lines.append("**Model answer:**")
                    lines.append("```")
                    lines.append((ent.get("response") or "")[:8000])
                    if len(ent.get("response") or "") > 8000:
                        lines.append("... [truncated]")
                    lines.append("```")
                    lines.append("")
        if stdout:
            lines.append("**stdout:**")
            lines.append("```")
            lines.append(stdout.strip())
            lines.append("```")
            lines.append("")
        if stderr:
            lines.append("**stderr:**")
            lines.append("```")
            lines.append(stderr.strip())
            lines.append("```")
            lines.append("")
        lines.append(f"**Exit code:** {code}")
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Results written to {OUTPUT_FILE}")

    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
