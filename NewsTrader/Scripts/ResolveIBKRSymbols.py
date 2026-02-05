import sys
import os
import json
import time
import pandas as pd
import threading
from datetime import datetime
from ibapi.contract import Contract

# --- PATH CONFIGURATION ---
MCP_BASE = r"C:\Users\HMz\Documents\Source\McpServer"
sys.path.append(os.path.join(MCP_BASE, "ibapi-mcp-server"))

try:
    from ibapi_mcp_server.ibapi_functions import IBGatewayClient
except ImportError as e:
    print(f"❌ critical Import Error: {e}")
    sys.exit(1)

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# --- CONSTANTS ---
IB_HOST = "127.0.0.1"
IB_PORT = 4001
IB_CLIENT_ID = 888  # Dedicated ID for resolution

def resolve_positions(filename):
    if not os.path.exists(filename):
        print(f"⚠️ File not found: {filename}")
        return

    print(f"\n📂 Opening {filename}...")
    df = pd.read_excel(filename)
    
    # Ensure columns exist
    for col in ['IBKR_Symbol', 'IBKR_SecType', 'IBKR_Exchange', 'IBKR_Currency', 'IBKR_ConID', 'IBKR_PrimaryExchange']:
        if col not in df.columns:
            df[col] = None

    # Connect to IBKR
    client = IBGatewayClient()
    api_thread = threading.Thread(target=client.run, daemon=True)
    
    try:
        print(f"🔌 Connecting to IBKR (Client {IB_CLIENT_ID})...")
        client.connect(IB_HOST, IB_PORT, IB_CLIENT_ID)
        api_thread.start()
        
        # Wait for connection
        if not client._connected.wait(timeout=10):
            print("❌ Connection failed!")
            sys.exit(1)
            
        print("✅ Connected!")
        
        updates_count = 0
        
        for index, row in df.iterrows():
            asset_name = row.get('Asset') or "Unknown"
            
            # Skip if already resolved (has ConID)
            if pd.notna(row.get('IBKR_ConID')) and str(row.get('IBKR_ConID')).strip() != "":
                continue

            isin = row.get('ISIN')
            ticker = row.get('Ticker')
            
            if not isin and not ticker:
                print(f"  ⏭️ Skipping {asset_name}: No ISIN or Ticker.")
                continue

            print(f"  🔍 Resolving {asset_name} ({isin or ticker})...")
            
            # Prepare Contract
            contract = Contract()
            contract.secType = "STK" # Default
            
            # Clean up ISIN/Ticker
            if pd.notna(isin) and str(isin).strip():
                # IBKR uses ISIN as secId with secIdType="ISIN" in reqContractDetails?
                # Actually, specialized reqContractDetails usage is safer via symbol/localSymbol.
                # Standard practice: symbol=ISIN and potentially setting exchange causes issues.
                # Best way for ISIN lookup:
                contract.symbol = str(isin).strip()
                contract.secIdType = "ISIN"
                contract.secId = str(isin).strip()
                # Important: When using secId, symbol can be empty or same.
                contract.exchange = "SMART" # Look everywhere
                contract.currency = "EUR" # Default guess, will refine
            elif pd.notna(ticker):
                contract.symbol = str(ticker).strip()
                contract.currency = "USD" # Default guess
                contract.exchange = "SMART"

            # Execute Request
            req_id = index + 1000
            client.contract_details = [] # Clear previous
            client._contract_details_done.clear()
            
            client.reqContractDetails(req_id, contract)
            
            # Wait
            got_data = client._contract_details_done.wait(timeout=5)
            
            if got_data and client.contract_details:
                # Pick best match (e.g. Primary Exchange)
                # For now, just take the first one
                details = client.contract_details[0]
                
                print(f"    ✅ Found: {details['symbol']} ({details['exchange']}) ID:{details['conId']}")
                
                df.at[index, 'IBKR_Symbol'] = details['symbol']
                df.at[index, 'IBKR_SecType'] = details['secType']
                df.at[index, 'IBKR_Exchange'] = details['exchange']
                df.at[index, 'IBKR_Currency'] = details['currency']
                df.at[index, 'IBKR_ConID'] = details['conId']
                df.at[index, 'IBKR_PrimaryExchange'] = details.get('primaryExchange', '')
                
                updates_count += 1
            else:
                print(f"    ❌ Not Found.")
        
        if updates_count > 0:
            print(f"💾 Saving {updates_count} updates to {filename}...")
            df.to_excel(filename, index=False)
        else:
            print("✨ No updates needed.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()
        if api_thread.is_alive(): api_thread.join(timeout=2)

if __name__ == "__main__":
    base_dir = r"G:\Meine Ablage\ShareFile\NewsTrader"
    resolve_positions(os.path.join(base_dir, "Open_Positions.xlsx"))
    resolve_positions(os.path.join(base_dir, "Watch_Positions.xlsx"))
