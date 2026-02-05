# MyIbkrNewsTrader — Project Documentation

## Overview

**MyIbkrNewsTrader** is a portfolio analysis pipeline that:

1. **Fetches** open positions from Interactive Brokers (IBKR) and optionally a watchlist from Excel.
2. **Gathers** current prices (IBKR → Alpaca → web scraping), forex rates (EUR/USD), and recent news (Google News, Tiingo).
3. **Analyzes** each asset with an AI (Claude) to produce trading recommendations and rationale.
4. **Writes** results to Excel, one PDF per asset, and a log file.

The pipeline is designed for a German-speaking user: recommendations and explanations are in German (e.g. *Kaufen*, *Verkaufen*, *Halten*, *Begründung*).

---

## Inputs

### 1. Portfolio (primary: live from IBKR)

- **Source:** Live connection to **IBKR Gateway** (or TWS) at `127.0.0.1:4001`.
- The script requests all open positions via the IB API; no file is required if IBKR is connected.
- **Fallback:** If no live positions are returned, the script tries to read:
  - **`Open_Positions.xlsx`** in the project base directory (see *Paths* below).  
  Expected columns include: `Asset`, `Ticker`, `ISIN`, `Anzahl`, `Einkaufspreis` / `Purchase_Price`, `Waehrung`, etc.

### 2. Watchlist (optional)

- **File:** **`Watch_Positions.xlsx`** in the project base directory.
- Expected columns: `Asset` (or `Emittent`, which is mapped to `Asset`). Other columns (e.g. Ticker, ISIN) improve price/news lookup.
- Watchlist items are analyzed like portfolio positions but get PDFs prefixed with `CHECK_` and are written to the “Watchlist Analyse” sheet.

### 3. Environment / API keys

- **`env.txt`** is loaded from several locations (local `Scripts` folder, shared path, or MCP server `dist` folders).  
  Used keys:
  - `ANTHROPIC_API_KEY` — required for AI analysis (Claude).
  - `TIINGO_API_KEY` — optional; used for forex and news fallback.
  - `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` (or `ALPACA_*`) — optional; Alpaca price fallback.
  - `TRADE_REPUBLIC_PHONE` / `TRADE_REPUBLIC_PIN` — currently unused (Trade Republic integration disabled).

### 4. External services

- **IBKR:** Gateway/TWS must be running and logged in; client ID `2191` (or next free ID) is used.
- **MCP servers:** The script expects Python packages from:
  - `ibapi-mcp-server` (e.g. `IBGatewayClient`, positions, contract details, market data).
  - `tiingo-mcp-server` (e.g. Tiingo price/news).
  Path is set to `C:\Users\HMz\Documents\Source\McpServer`; if your setup differs, adjust `MCP_BASE` in the script.

### 5. Paths (hardcoded in script)

- **Base directory:** `G:\Meine Ablage\ShareFile\MyIbkrNewsTrader`  
  Used for:
  - `Open_Positions.xlsx` (fallback)
  - `Watch_Positions.xlsx`
  - `Analysen\` (output folder)
- **Web price cache:** `G:\Meine Ablage\ShareFile\NewsTrader\web_price_cache.json`  
  If you use another drive/folder, change these paths in `AnalyzeIbkrPortfolio.py`.

---

## Outputs

All outputs are written under **`Analysen\<YYMMDD>\`** (e.g. `Analysen\260114\`), where `YYMMDD` is the current date.

### 1. Excel summary

- **File:** `\<YYMMDD> Portfolio_Pipeline_Analyse.xlsx`
- **Sheets:**
  - **Portfolio Analyse** — one row per open position: asset, ticker, prices, news summary, AI recommendation (*Empfehlung*), *Empfohlene_Stueckzahl*, *Begründung*, *Grund_fuer_Menge*, etc.
  - **Watchlist Analyse** — same structure for watchlist items.
  - **Price Sources** — which source (IBKR, Alpaca, Web, etc.) supplied the price for each asset.
- Technical columns (e.g. `IBKR_ConID`, raw `IBKR_Price` dicts) are stripped for readability. Recommendation column is color-coded (e.g. green for buy, red for sell).

### 2. PDFs per asset

- **Portfolio:** `\<YYMMDD>_<SafeAssetName>.pdf` (e.g. `260114_NVIDIACORP.pdf`).  
  Contains: asset name, date, ticker, recommendation (and optional quantity/strategy), AI rationale, and a short “Daten” table.
- **Watchlist:** `\<YYMMDD>_CHECK_<SafeAssetName>.pdf` (e.g. `260114_CHECK_ShopifyInc.pdf`).  
  Same structure, with “CHECK” in the filename.

### 3. Log file

- **File:** `\<YYMMDD>_Pipeline.log`  
  Console output (including connection status, fetch steps, and errors) is echoed to this file. A new run overwrites the existing log for that day.

---

## How to Use the Scripts

### Prerequisites

- **Python 3** with packages from **`Scripts/requirements.txt`**:  
  `anthropic`, `pandas`, `openpyxl`, `claude_agent_sdk`  
  (and optionally Alpaca SDK; ReportLab is used for PDFs and may need to be installed if not already).
- **IBKR Gateway** (or TWS) running and logged in on the machine where the script runs.
- **env.txt** with at least `ANTHROPIC_API_KEY` in one of the searched paths.
- MCP server packages (`ibapi-mcp-server`, `tiingo-mcp-server`) on the path configured in `MCP_BASE`.

### Run via batch file (Windows)

```batch
Run_Ibkr_Analysis.bat
```

- Changes directory to `Scripts` and runs `python AnalyzeIbkrPortfolio.py`, then pauses so you can read the console.

### Run Python directly

```bash
cd Scripts
python AnalyzeIbkrPortfolio.py
```

- Ensure the current working directory is such that relative paths (and any path logic) match your setup. The script uses the hardcoded base dir for input/output, so the main requirement is that IBKR is reachable and env keys are found.

### What the script does (order of operations)

1. Loads environment from `env.txt`.
2. Connects to IBKR (`127.0.0.1:4001`).
3. Fetches EUR/USD (IBKR → Tiingo → Google Finance if needed).
4. Loads portfolio: live positions from IBKR, or fallback to `Open_Positions.xlsx`.
5. Loads watchlist from `Watch_Positions.xlsx` if present.
6. For each portfolio and watchlist asset:
   - Fetches price (IBKR → Alpaca → web “DeepDive” scrape).
   - Fetches news (Google News, Tiingo).
   - Calls Claude for recommendation and rationale.
   - Merges data and writes one PDF per asset.
7. Writes the summary Excel (all sheets) under `Analysen\<YYMMDD>\`.
8. Disconnects from IBKR.

If IBKR connection is lost during the run, the script exits with a fatal error. Ctrl+C triggers a clean disconnect and exit.

---

## Summary Table

| Type   | Name / Location | Description |
|--------|------------------|-------------|
| Input  | IBKR Gateway     | Live positions and market data (required for full run). |
| Input  | `Open_Positions.xlsx` | Fallback portfolio if no live positions. |
| Input  | `Watch_Positions.xlsx` | Optional watchlist (columns: Asset or Emittent). |
| Input  | `env.txt`        | API keys (Anthropic required; Tiingo, Alpaca optional). |
| Output | `Analysen\<YYMMDD>\<YYMMDD> Portfolio_Pipeline_Analyse.xlsx` | Summary workbook (Portfolio, Watchlist, Price Sources). |
| Output | `Analysen\<YYMMDD>\<YYMMDD>_<Name>.pdf` | One PDF per portfolio position. |
| Output | `Analysen\<YYMMDD>\<YYMMDD>_CHECK_<Name>.pdf` | One PDF per watchlist item. |
| Output | `Analysen\<YYMMDD>\<YYMMDD>_Pipeline.log` | Run log. |
