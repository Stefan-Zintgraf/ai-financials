# Developer Documentation - NewsTrader Pipeline

## 1. Bug Fixes & Stabilität

### 🛑 KeyboardInterrupt (Ctrl+C) Tracebacks
**Problem**: Bei manuellem Abbruch des Skripts mit `Ctrl+C` wurden lange, unübersichtliche Python-Tracebacks angezeigt, da der Interrupt tief in `asyncio` oder `threading`-Warten-Operationen ausgelöst wurde.
**Lösung**: Implementierung eines globalen `signal.signal(signal.SIGINT, ...)` Handlers. Dieser fängt das Signal auf Betriebssystem-Ebene ab, führt eine saubere Trennung von IBKR durch und beendet den Prozess sofort mit `os._exit(0)`, was die Anzeige von Tracebacks komplett unterdrückt.

### 🧠 AI JSON Analysis Error (Invalid Control Character)
**Problem**: Claude hat in seinen Antworten manchmal Zeilenumbrüche innerhalb von JSON-Strings zurückgegeben (z.B. in der Begründung), was zu einem `json.JSONDecodeError` ("Invalid control character") führte.
**Lösung**: Verwendung von `json.loads(json_str, strict=False)`. Das Flag `strict=False` erlaubt explizit Steuerzeichen wie Zeilenumbrüche innerhalb von JSON-Strings. Zusätzlich wurde der JSON-Extraktions-Algorithmus robuster gestaltet.

### 🔌 IBKR Client ID Konflikte
**Problem**: Wenn das Skript abstürzt oder manuell beendet wird, bleibt die Client-ID manchmal für kurze Zeit im IBKR Gateway blockiert ("Client ID already in use").
**Lösung**: Die Funktion `init_ib_connection` versucht nun automatisch bis zu 5 verschiedene Client-IDs (startend von der konfigurierten ID), bis eine erfolgreiche Verbindung hergestellt werden kann.

### 📊 Excel "NaN" Crash (Empty Rows)
**Problem**: Leere Zeilen am Ende der `Open_Positions.xlsx` führten dazu, dass das Skript versuchte, ein `float` Objekt (NaN) als Asset-Namen zu verarbeiten, was zum Absturz führte (`'float' object has no attribute 'lower'`).
**Lösung**: Die Liste der Assets wird nun nach dem Einlesen der Excel-Datei gefiltert: `df = df.dropna(subset=['Asset'])`.

### 🔄 Trade Republic "Loop Conflict"
**Problem**: Bei der Abfrage von Trade Republic Kursen kam es zu `RuntimeError: got Future attached to a different loop`.
**Lösung**: Die asynchrone Abfrage wurde durch einen Aufruf der synchronen Methode `tr_get_quote_sync` ersetzt, die mittels `await asyncio.to_thread(...)` in einem separaten Thread ausgeführt wird. Dies kapselt das interne Loop-Management von `pytr` sauber ab.

### 🔇 Noisy IBKR Errors
**Problem**: Bei Derivaten gab IBKR häufig Fehlermeldungen wie "321 - Invalid security type" aus, da das Skript verschiedene Typen durchprobiert.
**Lösung**: Eine Subklasse `FilteredIBClient` filtert diese spezifischen Benachrichtigungs-Fehler (Codes 300, 321, 2104, 2106, 2107, 2158) nun aus.

## 2. Feature-Details

### 🎯 Derivate-Handling (Underlying Extraction)
Für Zertifikate (Calls, Puts, Turbos etc.) sucht das Skript nicht nach dem Namen des Derivats (z.B. "HSBC Call..."), sondern extrahiert den **Basiswert** (Underlying) für die News-Suche.
- **Logik**: Filtert Banknamen und Derivat-Keywords heraus.
- **Ergebnis**: Sucht gezielt nach "Zalando", "E.ON", "MDAX" etc.

### 📰 News-Suche & Filter
- **Such-Modus**: Verwendet jetzt konsequent `"Firmenname" +Aktie/stock` für maximale Präzision.
- **Strict Keyword Filter**: Um False-Positives (wie den Apex-Teenager-Mordfall) zu vermeiden, müssen Schlagzeilen Finanz-Keywords wie *stock, market, Börse, Ergebnis* enthalten, wenn der Firmenname sehr kurz ist.
- **Datum**: Filtert hart auf das heutige Datum (ISO-Format).

## 3. Betrieb & Best Practices

### 🔄 Prozess-Management
**WICHTIG**: Da das Skript persistente Verbindungen zu IBKR (über Ports) und Trade Republic (über WebSockets) aufbaut, sollten vor jedem neuen Start **alle aktiven Python-Prozesse beendet werden**. Dies verhindert:
1.  **Client-ID Konflikte** bei IBKR.
2.  **Port-Belegungen**, die den Start eines neuen Gateways oder Clients verhindern.
3.  **Zombies**, die im Hintergrund weiter News crawlen oder API-Limits verbrauchen.

Befehl zum Beenden: `taskkill /F /IM python.exe /T` (Windows)

---
*Stand: 14.01.2026*
