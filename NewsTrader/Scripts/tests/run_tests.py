"""Test orchestrator: discovers and runs test_*.py scripts, writes test_results.md.

Uses test.config when run normally. With --run=<spec>, bypasses config and runs
only the specified test(s) with explicit parameters.

Usage:
  python run_tests.py                        # Run all enabled tests from test.config
  python run_tests.py --dry-run              # Show what would run
  python run_tests.py --free-models          # Only ollama provider
  python run_tests.py --stop-on-failure      # Stop after first failure
  python run_tests.py --run=unit_ai_analysis # Run one module (no config)
  python run_tests.py --run=pipeline/ollama/mistral:latest/on/4096  # Single pipeline test
"""
import argparse
import configparser
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = TESTS_DIR.parent

# Module name -> script filename
MODULE_TO_SCRIPT = {
    "unit_ai_analysis": "test_unit_ai_analysis.py",
    "dummy_pipeline": "test_dummy_pipeline.py",
    "model_check": "test_model_check.py",
    "pipeline": "test_pipeline.py",
    "error_handling": "test_error_handling.py",
    "data_providers": "test_data_providers.py",
}

# Pattern to parse sub-test output
RESULT_PATTERN = re.compile(r"^(PASS|FAIL|SKIP):\s+(.+?)\s+\|\s+(.+)$", re.MULTILINE)

EXAMPLES = """
Examples:
  python run_tests.py                              Run all enabled tests from test.config
  python run_tests.py --dry-run                    Show what would run without executing
  python run_tests.py --free-models                Only test ollama provider
  python run_tests.py --stop-on-failure            Stop after first failure
  python run_tests.py --run=unit_ai_analysis       Run only unit tests (no config needed)
  python run_tests.py --run=dummy_pipeline,error_handling
                                                    Run two specific test modules
  python run_tests.py --run=model_check/ollama/mistral:latest
                                                    Check one specific model
  python run_tests.py --run=pipeline/ollama/mistral:latest/on/4096
                                                    Run one specific pipeline test
  python run_tests.py --run=pipeline/ollama/llama3.2:1b/off
                                                    Pipeline test with multistep off

Note: --run uses / (slash) as separator because model names may contain dots.
Configuration: test.config (see run_tests.md for details)
"""


def load_config(free_models: bool = False) -> configparser.ConfigParser:
    """Load test.config with defaults. If free_models, override providers to ollama only."""
    cp = configparser.ConfigParser()
    path = TESTS_DIR / "test.config"
    if path.exists():
        cp.read(path, encoding="utf-8")
    # Ensure sections exist
    if not cp.has_section("general"):
        cp.add_section("general")
    if not cp.has_section("tests"):
        cp.add_section("tests")
    if not cp.has_section("providers"):
        cp.add_section("providers")
    if not cp.has_section("models"):
        cp.add_section("models")
    if not cp.has_section("multistep"):
        cp.add_section("multistep")
    # Defaults
    cp.set("general", "stop_on_failure", cp.get("general", "stop_on_failure", fallback="false"))
    cp.set("general", "timeout", cp.get("general", "timeout", fallback="300"))
    for key in ("unit_ai_analysis", "dummy_pipeline", "model_check", "pipeline", "error_handling", "data_providers"):
        cp.set("tests", key, cp.get("tests", key, fallback="true"))
    for p in ("ollama", "anthropic", "openai"):
        if free_models:
            cp.set("providers", p, "true" if p == "ollama" else "false")
        else:
            cp.set("providers", p, cp.get("providers", p, fallback="true"))
    return cp


def parse_run_spec(spec: str) -> list[tuple[str, str | None]]:
    """Parse --run spec. Returns [(module, filter_params), ...]."""
    entries = [e.strip() for e in spec.split(",") if e.strip()]
    result = []
    for entry in entries:
        parts = entry.split("/")
        module = parts[0].strip().lower()
        if module not in MODULE_TO_SCRIPT:
            raise SystemExit(f"Unknown module in --run: {module}. Valid: {list(MODULE_TO_SCRIPT)}")
        if module in ("unit_ai_analysis", "dummy_pipeline", "error_handling", "data_providers"):
            if len(parts) > 1:
                raise SystemExit(f"Module {module} has no parameters. Use --run={module}")
            result.append((module, None))
        elif module == "model_check":
            if len(parts) != 3:
                raise SystemExit(f"model_check requires PROVIDER/MODEL. Got: {entry}")
            result.append((module, f"{parts[1]}/{parts[2]}"))
        elif module == "pipeline":
            if len(parts) < 4:
                raise SystemExit(f"pipeline requires PROVIDER/MODEL/MULTISTEP[/THR]. Got: {entry}")
            provider, model, multistep = parts[1], parts[2], parts[3].lower()
            if multistep == "on":
                if len(parts) < 5:
                    raise SystemExit(f"pipeline multistep=on requires PROVIDER/MODEL/on/THR. Got: {entry}")
                thr = parts[4]
                filter_val = f"{provider}/{model}/{multistep}/{thr}"
            else:
                filter_val = f"{provider}/{model}/{multistep}"
            result.append((module, filter_val))
        else:
            result.append((module, None))
    return result


def run_subtest(script_path: Path, config_path: Path | None, filter_param: str | None,
                dry_run: bool, timeout: int) -> tuple[int, str, list[tuple[str, str, str]]]:
    """Run sub-test, return (exitcode, stdout, [(PASS|FAIL|SKIP, name, msg), ...])."""
    cmd = [sys.executable, str(script_path)]
    if config_path:
        cmd.extend(["--config", str(config_path)])
    if filter_param:
        cmd.extend(["--filter", filter_param])
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend(["--timeout", str(timeout)])
    try:
        result = subprocess.run(
            cmd,
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout + 30,
        )
    except subprocess.TimeoutExpired:
        return -1, "", [("FAIL", "orchestrator", "Subprocess timeout")]
    except Exception as e:
        return -1, "", [("FAIL", "orchestrator", str(e))]
    out = result.stdout or ""
    parsed = []
    for m in RESULT_PATTERN.finditer(out):
        parsed.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return result.returncode, out, parsed


def main():
    parser = argparse.ArgumentParser(
        description="Run NewsTrader pipeline tests. Use test.config or --run for single tests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES,
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would run without executing")
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop after first failure")
    parser.add_argument("--free-models", action="store_true", help="Only test ollama provider")
    parser.add_argument("--run", metavar="SPEC", help="Run only specified test(s), bypasses test.config")
    args = parser.parse_args()

    os.chdir(SCRIPT_DIR)

    if args.run:
        try:
            run_entries = parse_run_spec(args.run)
        except SystemExit as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        config_path = None
        config_obj = None
        tests_to_run = [(mod, MODULE_TO_SCRIPT[mod], filt) for mod, filt in run_entries]
    else:
        config_obj = load_config(free_models=args.free_models)
        if args.stop_on_failure:
            config_obj.set("general", "stop_on_failure", "true")
        config_path = TESTS_DIR / "test.config"
        timeout = config_obj.getint("general", "timeout", fallback=300)
        tests_to_run = []
        for mod, script in MODULE_TO_SCRIPT.items():
            if config_obj.getboolean("tests", mod, fallback=True):
                tests_to_run.append((mod, script, None))

    timeout = 300
    if config_obj and config_obj.has_section("general"):
        timeout = config_obj.getint("general", "timeout", fallback=300)
    stop_on_fail = args.stop_on_failure or (
        config_obj.getboolean("general", "stop_on_failure", fallback=False) if config_obj else False
    )

    results_by_module = {}
    total_pass, total_fail, total_skip = 0, 0, 0

    for mod, script, filt in tests_to_run:
        script_path = TESTS_DIR / script
        if not script_path.exists():
            print(f"Warning: {script} not found, skipping", file=sys.stderr)
            continue
        if args.dry_run:
            print(f"Would run: {script}" + (f" --filter={filt}" if filt else ""))
            continue
        code, stdout, parsed = run_subtest(
            script_path,
            config_path,
            filt,
            dry_run=False,
            timeout=timeout,
        )
        results_by_module[mod] = {"code": code, "parsed": parsed}
        for kind, name, msg in parsed:
            if kind == "PASS":
                total_pass += 1
            elif kind == "FAIL":
                total_fail += 1
            else:
                total_skip += 1
        if stop_on_fail and total_fail > 0:
            break

    if args.dry_run:
        return 0

    # Write test_results.md
    lines = [
        f"# Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        "| Test | Result |",
        "|------|--------|",
    ]
    for mod in MODULE_TO_SCRIPT:
        if mod not in results_by_module:
            continue
        r = results_by_module[mod]
        parsed = r["parsed"]
        fails = sum(1 for k, _, _ in parsed if k == "FAIL")
        skips = sum(1 for k, _, _ in parsed if k == "SKIP")
        if fails > 0:
            status = "FAILED"
        elif skips == len(parsed) and parsed:
            status = "SKIPPED"
        else:
            status = "OK"
        lines.append(f"| {mod} | {status} |")
    lines.extend([
        "",
        f"**Total: {total_pass} passed, {total_fail} failed, {total_skip} skipped**",
        "",
        "## Details",
        "",
    ])
    for mod in MODULE_TO_SCRIPT:
        if mod not in results_by_module:
            continue
        lines.append(f"### {mod}")
        for kind, name, msg in results_by_module[mod]["parsed"]:
            lines.append(f"- {kind}: {name} | {msg}")
        lines.append("")

    out_path = TESTS_DIR / "test_results.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Results written to {out_path}")

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
