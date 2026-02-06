"""Shared utilities for NewsTrader test scripts."""
import configparser
import sys
from pathlib import Path

# Ensure Scripts/ is on path for imports
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import pandas as pd


def report(name: str, passed: bool, msg: str) -> None:
    """Print PASS or FAIL line to stdout."""
    prefix = "PASS" if passed else "FAIL"
    print(f"{prefix}: {name} | {msg}")


def skip(name: str, reason: str) -> None:
    """Print SKIP line to stdout."""
    print(f"SKIP: {name} | {reason}")


def get_daily_folder() -> Path:
    """Return today's Analysen/{yymmdd}/ path."""
    from datetime import datetime
    base_dir = _SCRIPTS.parent
    today = datetime.now().strftime("%y%m%d")
    return base_dir / "Analysen" / today


def get_debug_excel_path() -> Path | None:
    """Return path to today's _DEBUG.xlsx output if it exists."""
    from datetime import datetime
    folder = get_daily_folder()
    today = datetime.now().strftime("%y%m%d")
    path = folder / f"{today} Portfolio_Pipeline_Analyse_DEBUG.xlsx"
    return path if path.exists() else None


def read_excel_sheet(path: Path, sheet: str) -> pd.DataFrame:
    """Read Excel sheet by name. Thin wrapper around pd.read_excel."""
    return pd.read_excel(path, sheet_name=sheet)


def count_input_assets() -> tuple[int, int]:
    """Read debug input files, return (n_portfolio, n_watchlist)."""
    base_dir = _SCRIPTS.parent
    pos_file = base_dir / "Open_Positions_Debug.xlsx"
    watch_file = base_dir / "Watch_Positions_Debug.xlsx"
    n_portfolio = 0
    n_watchlist = 0
    if pos_file.exists():
        df = pd.read_excel(pos_file)
        if "Asset" in df.columns:
            n_portfolio = len(df.dropna(subset=["Asset"]))
    if watch_file.exists():
        df = pd.read_excel(watch_file)
        if "Asset" in df.columns:
            n_watchlist = len(df.dropna(subset=["Asset"]))
        elif "Emittent" in df.columns:
            n_watchlist = len(df.dropna(subset=["Emittent"]))
    return n_portfolio, n_watchlist


def find_column(df: pd.DataFrame, keyword: str) -> str | None:
    """Case-insensitive column lookup. Returns column name or None."""
    kw = keyword.lower()
    for c in df.columns:
        if c and kw in str(c).lower():
            return c
    return None


def load_test_config(config_path: str | Path) -> configparser.ConfigParser:
    """Load test.config via configparser. Returns the config object."""
    cp = configparser.ConfigParser()
    path = Path(config_path)
    if path.exists():
        cp.read(path, encoding="utf-8")
    return cp
