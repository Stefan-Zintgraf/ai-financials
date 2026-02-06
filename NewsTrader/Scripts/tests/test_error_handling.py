"""Tests invalid inputs produce non-zero exit. Uses try/finally for env.txt restoration."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_helpers import report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config")
    parser.add_argument("--filter", default=None, help="Filter params (ignored for error_handling)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent

    if args.dry_run:
        print("Would run: invalid_provider, model_check_bad_provider, missing_env_file")
        return 0

    failed = 0

    # invalid_provider
    cmd = [sys.executable, "AnalyzePortfolio_Pipeline.py", "--quick-analysis", "--provider=nonexistent"]
    try:
        result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        report("invalid_provider", False, "Timeout")
        failed += 1
    except Exception as e:
        report("invalid_provider", False, str(e))
        failed += 1
    else:
        if result.returncode != 0:
            report("invalid_provider", True, "OK")
        else:
            report("invalid_provider", False, f"Expected non-zero exit, got {result.returncode}")
            failed += 1

    # model_check_bad_provider
    cmd = [sys.executable, "AnalyzePortfolio_Pipeline.py", "--quick-analysis", "--model-check",
           "--provider=nonexistent"]
    try:
        result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        report("model_check_bad_provider", False, "Timeout")
        failed += 1
    except Exception as e:
        report("model_check_bad_provider", False, str(e))
        failed += 1
    else:
        if result.returncode != 0:
            report("model_check_bad_provider", True, "OK")
        else:
            report("model_check_bad_provider", False, f"Expected non-zero exit, got {result.returncode}")
            failed += 1

    # missing_env_file
    env_path = script_dir / "env.txt"
    backup_path = script_dir / "env.txt.bak_test"
    if not env_path.exists():
        report("missing_env_file", True, "OK (env.txt not present, skip)")
    else:
        try:
            os.rename(env_path, backup_path)
            cmd = [sys.executable, "AnalyzePortfolio_Pipeline.py", "--quick-analysis", "--model-check"]
            result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, timeout=args.timeout)
            if result.returncode != 0:
                report("missing_env_file", True, "OK")
            else:
                report("missing_env_file", False, f"Expected non-zero when env.txt missing, got {result.returncode}")
                failed += 1
        except Exception as e:
            report("missing_env_file", False, str(e))
            failed += 1
        finally:
            if backup_path.exists():
                try:
                    if env_path.exists():
                        env_path.unlink()
                    os.rename(backup_path, env_path)
                except Exception as e:
                    print(f"WARNING: Could not restore env.txt: {e}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
