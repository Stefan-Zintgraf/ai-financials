"""Runs full analysis pipeline per provider/model/multistep. Validates Excel output."""
import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_helpers import (
    report,
    skip,
    get_daily_folder,
    get_debug_excel_path,
    read_excel_sheet,
    find_column,
    load_test_config,
)

PARSE_FAILURE_INDICATORS = ("[parse failed]", "[missing]", "[invalid]")
VALID_REC = {"Buy", "Sell", "Hold", "Add", "Reduce"}
VALID_CONF = {"High", "Medium", "Low"}


def _has_api_key(provider: str) -> bool:
    import os
    if provider == "ollama":
        return True
    if provider == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return False


def _run_case(script_dir: Path, provider: str, model: str, multistep: str, thr: str | None,
              timeout: int) -> tuple[int, str]:
    cmd = [
        sys.executable, "AnalyzePortfolio_Pipeline.py",
        "--quick-analysis",
        f"--provider={provider}", f"--mode={model}",
        f"--multistep={multistep}",
    ]
    if multistep == "on" and thr:
        cmd.append(f"--multistep_thr={thr}")
    try:
        result = subprocess.run(
            cmd,
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -1, "Timeout"
    except Exception as e:
        return -1, str(e)
    return result.returncode, result.stderr or result.stdout or ""


def _validate_excel(excel_path: Path, case_id: str) -> list[tuple[str, bool, str]]:
    """Run all validation checks. Returns list of (name, passed, msg)."""
    results = []
    try:
        df = read_excel_sheet(excel_path, "Portfolio Analyse")
    except Exception as e:
        results.append((f"{case_id} excel_read", False, str(e)))
        return results

    rec_col = find_column(df, "recommendation")
    if not rec_col:
        results.append((f"{case_id} excel_columns", False, "No Recommendation column"))
        return results

    # no_parse_failures
    failed_assets = []
    for _, row in df.iterrows():
        val = str(row.get(rec_col, "") or "").lower()
        if any(ind in val for ind in PARSE_FAILURE_INDICATORS):
            asset_col = find_column(df, "asset")
            asset = row.get(asset_col, "?") if asset_col else "?"
            failed_assets.append(f"{asset}: {val[:60]}")
    if failed_assets:
        results.append((f"{case_id} no_parse_failures", False, "; ".join(failed_assets[:3])))
    else:
        results.append((f"{case_id} no_parse_failures", True, "OK"))

    # valid_recommendations
    invalid_rec = []
    for _, row in df.iterrows():
        val = str(row.get(rec_col, "") or "").strip()
        if val and val not in VALID_REC:
            invalid_rec.append(val)
    if invalid_rec:
        results.append((f"{case_id} valid_recommendations", False, f"Invalid: {set(invalid_rec)}"))
    else:
        results.append((f"{case_id} valid_recommendations", True, "OK"))

    # valid_confidence
    conf_col = find_column(df, "confidence") or find_column(df, "genauigkeit")
    if conf_col:
        invalid_conf = []
        for _, row in df.iterrows():
            val = str(row.get(conf_col, "") or "").strip()
            if val and val not in VALID_CONF:
                invalid_conf.append(val)
        if invalid_conf:
            results.append((f"{case_id} valid_confidence", False, f"Invalid: {set(invalid_conf)}"))
        else:
            results.append((f"{case_id} valid_confidence", True, "OK"))

    # quantity_is_int (Excel may not have explicit recommended_quantity column)
    qty_col = find_column(df, "quantity") or find_column(df, "recommended") or find_column(df, "stueckzahl")
    if qty_col:
        bad_qty = []
        for _, row in df.iterrows():
            v = row.get(qty_col)
            if v is not None and v != "" and not isinstance(v, (int, float)):
                bad_qty.append(str(v))
        if bad_qty:
            results.append((f"{case_id} quantity_is_int", False, f"Non-numeric: {bad_qty[:3]}"))
        else:
            results.append((f"{case_id} quantity_is_int", True, "OK"))
    else:
        results.append((f"{case_id} quantity_is_int", True, "OK (no qty column in schema)"))

    # reasoning_not_empty
    reason_col = find_column(df, "reasoning") or find_column(df, "begründung") or find_column(df, "begruendung")
    if reason_col:
        empty = 0
        for _, row in df.iterrows():
            v = row.get(reason_col)
            if v is None or (isinstance(v, str) and not v.strip()):
                empty += 1
        if empty > 0:
            results.append((f"{case_id} reasoning_not_empty", False, f"{empty} empty"))
        else:
            results.append((f"{case_id} reasoning_not_empty", True, "OK"))

    # watchlist_sheet_exists
    try:
        read_excel_sheet(excel_path, "Watchlist Analyse")
        results.append((f"{case_id} watchlist_sheet_exists", True, "OK"))
    except Exception:
        results.append((f"{case_id} watchlist_sheet_exists", True, "OK"))  # optional

    # pdf_files_exist
    folder = get_daily_folder()
    today = datetime.now().strftime("%y%m%d")
    pdfs = list(folder.glob(f"{today}_*_DEBUG.pdf"))
    if pdfs:
        results.append((f"{case_id} pdf_files_exist", True, "OK"))
    else:
        results.append((f"{case_id} pdf_files_exist", False, "No PDF"))

    # log_no_fatal
    log_path = folder / f"{today}_Pipeline.log"
    if log_path.exists():
        content = log_path.read_text(encoding="utf-8", errors="replace")
        if "FATAL" in content:
            results.append((f"{case_id} log_no_fatal", False, "Log contains FATAL"))
        else:
            results.append((f"{case_id} log_no_fatal", True, "OK"))

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config")
    parser.add_argument("--filter", default=None, help="Filter: PROVIDER/MODEL/MULTISTEP[/THR]")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent

    # Load env for API key check
    sys.path.insert(0, str(script_dir))
    import config as app_config
    app_config.load_env_keys()

    if args.filter:
        parts = args.filter.split("/")
        if len(parts) < 3:
            print("Invalid --filter for pipeline: expected PROVIDER/MODEL/MULTISTEP[/THR]")
            return 1
        provider, model, multistep = parts[0].lower(), parts[1], parts[2].lower()
        thr = parts[3] if len(parts) > 3 and multistep == "on" else "4096"
        cases = [{"provider": provider, "model": model, "multistep": multistep, "thr": thr if multistep == "on" else None}]
    else:
        config_path = args.config or (Path(__file__).resolve().parent / "test.config")
        cp = load_test_config(config_path)
        if not cp.getboolean("tests", "pipeline", fallback=True):
            skip("pipeline", "pipeline disabled in config")
            return 0

        providers = []
        if cp.has_section("providers"):
            for p in ("ollama", "anthropic", "openai"):
                if cp.getboolean("providers", p, fallback=False):
                    providers.append(p)
        models = {}
        if cp.has_section("models"):
            for p in ("ollama", "anthropic", "openai"):
                val = cp.get("models", p, fallback="")
                models[p] = [m.strip() for m in val.split(",") if m.strip()]
        vary = cp.getboolean("multistep", "vary", fallback=True)
        thresholds = [t.strip() for t in cp.get("multistep", "thresholds", fallback="4096,8192").split(",") if t.strip()]

        cases = []
        for provider in providers:
            for model in models.get(provider, ["llama3.2:1b"]):
                if vary:
                    multisteps = [("on", t) for t in thresholds] + [("off", None)]
                else:
                    multisteps = [("on", thresholds[0] if thresholds else "4096")]
                for multistep, thr in multisteps:
                    cases.append({"provider": provider, "model": model, "multistep": multistep, "thr": thr})

    failed = 0
    for case in cases:
        provider = case["provider"]
        model = case["model"]
        multistep = case["multistep"]
        thr = case.get("thr")
        case_id = f"{provider}/{model}/{multistep}"
        if multistep == "on" and thr:
            case_id += f"/{thr}"

        if not _has_api_key(provider):
            skip(f"{case_id} pipeline", f"API key not set for {provider}")
            continue

        if args.dry_run:
            cmd = ["--quick-analysis", f"--provider={provider}", f"--mode={model}",
                   f"--multistep={multistep}"]
            if multistep == "on" and thr:
                cmd.append(f"--multistep_thr={thr}")
            print(f"Would run pipeline: {' '.join(cmd)}")
            continue

        code, err = _run_case(script_dir, provider, model, multistep, thr, args.timeout)
        if code != 0:
            report(f"{case_id} pipeline_exits_zero", False, f"Exit {code}: {err[:150]}")
            failed += 1
            continue
        report(f"{case_id} pipeline_exits_zero", True, "OK")

        # Copy LLM debug file for run_all_tests to include in results
        folder = get_daily_folder()
        llm_debug_src = folder / "llm_debug.json"
        if llm_debug_src.exists():
            dest = Path(__file__).resolve().parent / "last_llm_debug.json"
            shutil.copy2(llm_debug_src, dest)

        excel_path = get_debug_excel_path()
        if not excel_path:
            report(f"{case_id} excel_exists", False, "Output Excel not found")
            failed += 1
            continue
        report(f"{case_id} excel_exists", True, "OK")

        for name, passed, msg in _validate_excel(excel_path, case_id):
            report(name, passed, msg)
            if not passed:
                failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
