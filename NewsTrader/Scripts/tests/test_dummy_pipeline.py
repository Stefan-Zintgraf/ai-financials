"""Runs pipeline with --quick-analysis --dummy-analysis. Validates Excel, PDF, log."""
import argparse
import glob
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
    count_input_assets,
    find_column,
)

PARSE_FAILURE_INDICATORS = ("[parse failed]", "[missing]", "[invalid]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to test.config")
    parser.add_argument("--filter", default=None, help="Filter params (ignored for dummy_pipeline)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent

    if args.dry_run:
        cmd = [sys.executable, "AnalyzePortfolio_Pipeline.py", "--quick-analysis", "--dummy-analysis"]
        print(f"Would run: {' '.join(cmd)}")
        return 0

    failed = 0

    # Run pipeline
    cmd = [sys.executable, "AnalyzePortfolio_Pipeline.py", "--quick-analysis", "--dummy-analysis"]
    try:
        result = subprocess.run(
            cmd,
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        report("pipeline_exits_zero", False, "Timeout")
        failed += 1
        return 1 if failed else 0
    except Exception as e:
        report("pipeline_exits_zero", False, str(e))
        failed += 1
        return 1 if failed else 0

    if result.returncode != 0:
        report("pipeline_exits_zero", False, f"Exit {result.returncode}: {result.stderr[:300]}")
        failed += 1
        return 1 if failed else 0
    report("pipeline_exits_zero", True, "OK")

    excel_path = get_debug_excel_path()
    if not excel_path:
        report("excel_exists", False, "Output Excel not found")
        failed += 1
        return 1 if failed else 0
    report("excel_exists", True, "OK")

    try:
        df = read_excel_sheet(excel_path, "Portfolio Analyse")
    except Exception as e:
        report("excel_has_portfolio_sheet", False, str(e))
        failed += 1
        return 1 if failed else 0
    rec_col = find_column(df, "recommendation")
    if not rec_col:
        report("excel_has_portfolio_sheet", False, "No Recommendation column")
        failed += 1
    else:
        report("excel_has_portfolio_sheet", True, "OK")

    n_portfolio, n_watchlist = count_input_assets()
    try:
        df_watch = read_excel_sheet(excel_path, "Watchlist Analyse")
    except Exception:
        if n_watchlist > 0:
            report("excel_has_watchlist_sheet", False, "Watchlist sheet missing but input has watchlist")
            failed += 1
        else:
            skip("excel_has_watchlist_sheet", "No watchlist input")
    else:
        report("excel_has_watchlist_sheet", True, "OK")

    df = read_excel_sheet(excel_path, "Portfolio Analyse")
    if len(df) != n_portfolio:
        report("excel_row_count_matches_input", False, f"Expected {n_portfolio} rows, got {len(df)}")
        failed += 1
    else:
        report("excel_row_count_matches_input", True, "OK")

    rec_col = find_column(df, "recommendation")
    all_hold = True
    for _, row in df.iterrows():
        val = str(row.get(rec_col, "") or "").strip()
        if val.lower() != "hold":
            all_hold = False
            break
    if all_hold:
        report("all_recommendations_hold", True, "OK")
    else:
        report("all_recommendations_hold", False, "Dummy mode should return Hold for all")
        failed += 1

    conf_col = find_column(df, "confidence") or find_column(df, "genauigkeit")
    all_low = True
    if conf_col:
        for _, row in df.iterrows():
            val = str(row.get(conf_col, "") or "").strip()
            if val.lower() != "low":
                all_low = False
                break
    if all_low:
        report("all_confidence_low", True, "OK")
    else:
        report("all_confidence_low", False, "Dummy mode should return Low for all")
        failed += 1

    folder = get_daily_folder()
    today = datetime.now().strftime("%y%m%d")
    pdfs = list(folder.glob(f"{today}_*_DEBUG.pdf"))
    if pdfs:
        report("pdf_files_exist", True, "OK")
    else:
        report("pdf_files_exist", False, f"No PDF in {folder}")
        failed += 1

    log_path = folder / f"{today}_Pipeline.log"
    if log_path.exists():
        report("log_file_exists", True, "OK")
    else:
        report("log_file_exists", False, f"Log not found: {log_path}")
        failed += 1

    if log_path.exists():
        content = log_path.read_text(encoding="utf-8", errors="replace")
        if "FATAL" in content:
            report("log_no_fatal", False, "Log contains FATAL")
            failed += 1
        else:
            report("log_no_fatal", True, "OK")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
