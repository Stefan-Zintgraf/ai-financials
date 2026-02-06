# NewsTrader – Project Overview

**NewsTrader** is a portfolio analysis and news-driven trading support tool. It reads your open positions and watchlist from Excel, fetches live prices and recent news from multiple sources, and uses AI (Anthropic Claude) to generate **buy / hold / sell** recommendations with short justifications. Results are written to Excel and PDF reports in a dated output folder.

---

## Purpose

- **Portfolio analysis**: For each position (and optionally a watchlist), the pipeline collects current prices, profit/loss, and today’s news.
- **AI recommendations**: Claude analyzes news sentiment and context and returns a recommendation (e.g. *Kaufen*, *Halten*, *Verkaufen*, *Teilverkauf*) with a brief reason.
- **Structured output**: One Excel file per run (with main sheet, watchlist sheet, and price sources) plus one PDF per asset in a daily folder under `Analysen/`.

The project supports **stocks and derivatives** (e.g. certificates, turbos); for derivatives it derives the underlying name for news search. Prices are obtained from **IBKR**, **Tiingo**, **Alpaca**, and web scraping (e.g. Onvista, Ariva, Comdirect) with currency conversion (EUR/USD) where needed.

---

## Project Layout

| Path | Description |
|------|-------------|
| **Scripts/** | Main Python scripts and batch launcher |
| **Analysen/** | Output folder: one subfolder per date (YYMMDD) with Excel, PDFs, and log |
| **Trades/** | Trade PDFs and portfolio-generation script |
| **Open_Positions.xlsx** | Input: current portfolio (Asset, WKN, ISIN, quantity, etc.) |
| **Watch_Positions.xlsx** | Input (optional): watchlist to analyze in the same run |

---

## Main Scripts and Functionality

### 1. `AnalyzePortfolio_Pipeline.py` (main pipeline)

**Location:** `Scripts/AnalyzePortfolio_Pipeline.py`

**What it does:**

1. Loads **Open_Positions.xlsx** and **Watch_Positions.xlsx** (if present).
2. Fetches **EUR/USD** (Tiingo or Google Finance).
3. For each asset:
   - **Price**: IBKR (if configured), then Tiingo, Alpaca, then web “deep dive” (Onvista, Ariva, Comdirect, BNP, etc.).
   - **News**: Google News RSS and/or Tiingo/Alpaca news, filtered to today; for derivatives, news is searched by **underlying** name.
4. Sends collected data (positions, prices, news) to **Claude** and gets **Empfehlung** + **Begründung**.
5. Writes:
   - **Excel**: `Analysen/<YYMMDD>/<YYMMDD> Portfolio_Pipeline_Analyse.xlsx` (main sheet, watchlist sheet, Price Sources sheet).
   - **PDFs**: one per asset in the same folder.
   - **Log**: `<YYMMDD>_Pipeline.log` in the same folder.

**Testing:** Use `--dummy-analysis` to skip AI calls and use debug input files (`Open_Positions_Debug.xlsx`, `Watch_Positions_Debug.xlsx`). Output files then get a `_DEBUG` suffix (e.g. `260206 Portfolio_Pipeline_Analyse_DEBUG.xlsx`).

**How to run:**

- From `Scripts/`:  
  `python AnalyzePortfolio_Pipeline.py` (add `--dummy-analysis` for testing)
- Or use the batch file:  
  `Scripts/Run_Analysis.bat`  
  (it only changes to `Scripts` and runs the pipeline).

**Requirements:** API keys and config in `env.txt` (or paths configured in the script): e.g. `TIINGO_API_KEY`, `ANTHROPIC_API_KEY`, `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY`. IBKR Gateway must be running and reachable if you use IBKR for prices.  
**Paths:** The script uses hardcoded base paths (e.g. for `Open_Positions.xlsx`, `Analysen`, log, and MCP/server dirs). Adjust them at the top of the script if your project lives elsewhere.

---

### 2. `Run_Analysis.bat`

**Location:** `Scripts/Run_Analysis.bat`

Runs the main pipeline: changes to `Scripts` and executes `python AnalyzePortfolio_Pipeline.py`. Double-click or call from a shell.

---

### 3. `ResolveIBKRSymbols.py`

**Location:** `Scripts/ResolveIBKRSymbols.py`

**What it does:** Connects to **IBKR** (Gateway on port 4001), and for each row in **Open_Positions.xlsx** and **Watch_Positions.xlsx** that does not yet have IBKR contract data, resolves **ISIN** or **Ticker** to a contract and writes:

- `IBKR_Symbol`, `IBKR_SecType`, `IBKR_Exchange`, `IBKR_Currency`, `IBKR_ConID`, `IBKR_PrimaryExchange`

**How to run:** From project root or `Scripts/` (depending on how paths are set in the script):

```text
python Scripts/ResolveIBKRSymbols.py
```

Script expects `Open_Positions.xlsx` and `Watch_Positions.xlsx` under the same base directory used in the script (e.g. `G:\Meine Ablage\ShareFile\NewsTrader`). **IBKR Gateway must be running** before execution.

---

### 4. `generate_portfolio.py` (Trades)

**Location:** `Trades/generate_portfolio.py`

**What it does:** Builds a **portfolio Excel** from:

- Trade PDFs (e.g. Consorsbank confirmations) in the `Trades/` folder, and/or  
- A source like **Trade_Zusammenfassung.xlsx** (if used in the script).

It extracts WKN/ISIN from PDFs, maps WKN to readable names and Yahoo/ariva tickers, fetches prices (Yahoo Finance, ariva.de), and writes **Portfolio_Open_Positions.xlsx** (or similar) with positions, quantities, and profit. Used to **create or update** the open positions list that the main pipeline reads (e.g. after copying/renaming to `Open_Positions.xlsx` in the project root).

**How to run:** From project root:

```text
python Trades/generate_portfolio.py
```

(Exact input/output file names and paths are defined inside the script.)

---

### 5. `ask_claude.py`

**Location:** `Scripts/ask_claude.py`

**What it does:** Alternative, **MCP-based** workflow using the **Claude Agent SDK**. It asks Claude to:

1. Get US stock symbols from a **cTrader** MCP server (e.g. account 5122894).
2. Use **Tiingo** and **Alpaca** MCP servers to read news and suggest a short list of “best US stocks to buy.”

So this script is for **US-focused, MCP-driven** analysis rather than the Excel-based pipeline.

**How to run:** From `Scripts/`:

```text
python ask_claude.py
```

Requires `claude_agent_sdk` and configured MCP servers (ctrader, tiingo, alpaca). Paths and account IDs inside the script may need to be adjusted.

---

### 6. `TestIBKRConnection.py`

**Location:** `Scripts/TestIBKRConnection.py`

**What it does:** Checks that the **IBKR** connection works via the IBKR MCP server: sets connection mode (e.g. gateway, port 4001) and requests a mid price for a symbol (e.g. AAPL).

**How to run:** From `Scripts/`:

```text
python TestIBKRConnection.py
```

Useful after installing or changing IBKR Gateway/MCP setup.

---

## Other Files (Scripts)

- **DEVELOPER_DOCS.md** – Bug fixes, stability notes (e.g. Ctrl+C handling, IBKR client ID conflicts, JSON parsing, Excel NaN handling), and feature details (derivatives/underlying, news filters).
- **requirements.txt** – Lists `anthropic`, `pandas`, `openpyxl`, `claude_agent_sdk`; the pipeline also uses `requests`, `reportlab`, `ibapi`, etc. Install with `pip install -r Scripts/requirements.txt` and add any missing dependencies as needed.
- **scan_prints.py**, **test_anthropic_models.py**, **test_sdk.py**, **test_sdk_error.py** – Debug/test helpers; not required for normal use.

---

## Typical Workflow

1. **Prepare positions**
   - Either maintain **Open_Positions.xlsx** (and optionally **Watch_Positions.xlsx**) by hand, or  
   - Run **Trades/generate_portfolio.py** from trade PDFs and then use/copy its output as **Open_Positions.xlsx**.

2. **Optional: resolve IBKR symbols**  
   Run **ResolveIBKRSymbols.py** once (or when you add new instruments) so the pipeline can use IBKR prices where available.

3. **Run the main analysis**  
   Use **Run_Analysis.bat** or `python Scripts/AnalyzePortfolio_Pipeline.py`. Ensure:
   - `env.txt` (or equivalent) has the needed API keys.
   - IBKR Gateway is running if you use IBKR.

4. **Check results**  
   Open `Analysen/<YYMMDD>/` and use:
   - `<YYMMDD> Portfolio_Pipeline_Analyse.xlsx` for the summary and price sources.
   - PDFs and `<YYMMDD>_Pipeline.log` for per-asset details and debugging.

---

## Configuration and Paths

- **API keys / env:** Stored in `env.txt` (e.g. under `Scripts/` or paths referenced in the pipeline). Variables used include `TIINGO_API_KEY`, `ANTHROPIC_API_KEY`, `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`; optional: Trade Republic, IBKR.
- **Paths:** Several scripts use **hardcoded** base directories (e.g. `G:\Meine Ablage\ShareFile\NewsTrader`, `C:\Users\...\McpServer`). If you move the project or use another machine, search for these paths in `AnalyzePortfolio_Pipeline.py`, `ResolveIBKRSymbols.py`, `ask_claude.py`, and `TestIBKRConnection.py` and update them.

---

## Summary Table

| Script | Purpose | How to run |
|--------|--------|------------|
| **AnalyzePortfolio_Pipeline.py** | Main pipeline: prices + news + AI → Excel + PDFs | `python Scripts/AnalyzePortfolio_Pipeline.py` or `Run_Analysis.bat` |
| **Run_Analysis.bat** | Launcher for the pipeline | Double-click or `Scripts\Run_Analysis.bat` |
| **ResolveIBKRSymbols.py** | Fill IBKR contract fields in position Excel files | `python Scripts/ResolveIBKRSymbols.py` |
| **Trades/generate_portfolio.py** | Build portfolio Excel from trade PDFs | `python Trades/generate_portfolio.py` |
| **ask_claude.py** | MCP-based US stocks + news via Claude | `python Scripts/ask_claude.py` |
| **TestIBKRConnection.py** | Test IBKR MCP connection | `python Scripts/TestIBKRConnection.py` |
