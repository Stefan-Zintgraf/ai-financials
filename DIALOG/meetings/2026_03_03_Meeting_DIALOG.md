## Inhaltsverzeichnis

1. [Kontext](#kontext)
   - [Projektidee](#projektidee)
   - [Ausgangslage](#ausgangslage)
   - [Asset-Klassen im Scope](#asset-klassen-im-scope)
   - [Technologie-Interessen](#technologie-interessen)
2. [Meeting Strategie](#meeting-strategie)
3. [Prio 1 — MUSS im Meeting geklärt werden](#prio-1--muss-im-meeting-geklärt-werden)
4. [Prio 2 — SOLLTE im Meeting besprochen werden](#prio-2--sollte-im-meeting-besprochen-werden)
5. [Prio 3 — KANN per Follow-up geklärt werden](#prio-3--kann-per-follow-up-geklärt-werden)
6. [Tipps für das Meeting](#tipps-für-das-meeting)
7. [Nach dem Meeting](#nach-dem-meeting)

---

## Kontext

### Projektidee

Entwicklung eines KI-Assistenten, der einen Vermögensverwalter in seiner täglichen Arbeit unterstützt. Schwerpunkt liegt auf dem **Sammeln und Auswerten von Informationen** für fundierte Anlageentscheidungen.

### Ausgangslage

- **Stefan Zintgraf:** Entwickler mit LLM-Erfahrung, Domäne Vermögensverwaltung ist neu
- **Heinrich Munz:** Hat die Idee unabhängig ebenfalls entwickelt, bringt bessere Domänenkenntnisse mit
- **DIALOG:** Kleine Vermögensverwaltung (~5 Personen), weiß grundsätzlich über das Vorhaben Bescheid
- **Bekannte Fakten:** Kein Bloomberg Terminal im Einsatz

### Asset-Klassen im Scope

1. **Aktien** — Hauptfokus
2. **Anleihen / Rentenpapiere**
3. **Kryptowährungen** — berücksichtigt, aber kein Schwerpunkt
4. **Edelmetalle** — je nach Kundenbedarf

### Technologie-Interessen

Prompting, Workflow-Automatisierung, Vektordatenbanken, RAG, autonome Agenten

---

## Meeting Strategie

- Hmz traegt PPT vor, ggf. Handsup und Mockup
- Szf macht Notizen, wie DIALOG darauf reagiert und was als Input fuer uns dienen kann
- Falls Fragen von unten beantwortet wurden: Antwort dazuschreiben

---

## Prio 1 — MUSS im Meeting geklärt werden

*Das Fundament — ohne diese Antworten kann nicht sinnvoll weitergearbeitet werden.*

### Arbeitsalltag verstehen

| # | Frage | Notizen |
|---|-------|---------|
| 1 | Können Sie uns durch einen typischen Arbeitstag führen? | |
| 2 | Wo verbringen Sie und Ihr Team die meiste Zeit — und wo wünschen Sie sich Entlastung? | |

- Regulatorien (Vertraege pruefen)
- Arbeitsvertraege
- Marktreport und Prognosen
- Youtube Video skripten


### Informationslandschaft erfassen

| # | Frage | Notizen |
|---|-------|---------|
| 3 | Welche Informationsquellen nutzen Sie täglich? (Nachrichtenportale, Datenbanken, Newsletter, etc.) | |

- TraderFox hat historischen Daten

| 4 | Wie speichern und organisieren Sie Ihre Recherche-Ergebnisse aktuell? | |


### KI-Vision und Erwartungen

| # | Frage | Notizen |
|---|-------|---------|
| 5 | Was erhoffen Sie sich am meisten von einem KI-Assistenten? | |
| 6 | Was wäre ein konkretes Ergebnis, bei dem Sie sagen würden: "Das hat sich gelohnt"? | |
| 7 | Gibt es eine Aufgabe, die Sie uns als erstes Pilotprojekt vorschlagen würden? | |
| 8 | Wo sehen Sie die größten Risiken oder Bedenken beim Einsatz von KI? | |

---

## Prio 2 — SOLLTE im Meeting besprochen werden

*Vertiefung — wichtig für die Lösungsarchitektur, aber notfalls per Follow-up nachholbar.*

### Entscheidungsprozesse & Fachliches

| # | Frage | Notizen |
|---|-------|---------|
| 9 | Wie sieht Ihr Entscheidungsprozess aus, wenn Sie eine Aktie kaufen oder verkaufen? | |
| 10 | Welche Kennzahlen sind für Sie bei der Bewertung am wichtigsten? (KGV, Sharpe Ratio, etc.) | |
| 11 | Welche weiteren Asset-Klassen betreuen Sie neben Aktien, Anleihen und Krypto — z.B. Edelmetalle, Rohstoffe, Immobilienfonds? | |

### Tools & Systeme

| # | Frage | Notizen |
|---|-------|---------|
| 12 | Welche Software nutzen Sie für die Portfolioverwaltung? | |

### Kundenkommunikation

| # | Frage | Notizen |
|---|-------|---------|
| 13 | Wie oft und in welchem Format berichten Sie Ihren Kunden? (PDF, E-Mail, persönlich?) | |
| 14 | Wie viel Zeit investieren Sie oder Ihr Team in die Erstellung dieser Berichte? | |

### KI-Readiness

| # | Frage | Notizen |
|---|-------|---------|
| 15 | Haben Sie schon Erfahrung mit KI-Tools gemacht? (ChatGPT, Copilot, etc.) | |
| 16 | Wie steht Ihr Team dem Thema KI gegenüber? | |

---

## Prio 3 — KANN per Follow-up geklärt werden

*Detail-Fragen, die erst relevant werden wenn die Richtung klar ist. Per E-Mail oder kurzes Webmeeting nachliefern.*

### Regulatorik & Compliance

| # | Frage | Notizen |
|---|-------|---------|
| 17 | Welche regulatorischen Anforderungen bestimmen Ihren Alltag am stärksten? | |
| 18 | Wie dokumentieren Sie heute Ihre Anlageentscheidungen? | |
| 19 | Gibt es Vorgaben, die den Einsatz von KI-Tools einschränken könnten? | |
| 20 | Wie sensibel sehen Sie das Thema Kundendaten im Zusammenhang mit KI? | |
| 21 | Haben Sie einen Compliance-Beauftragten oder externe Berater? | |

### Reporting-Details

| # | Frage | Notizen |
|---|-------|---------|
| 22 | Was fragen Ihre Kunden am häufigsten? | |
| 23 | Gibt es standardisierte Vorlagen für Berichte oder wird individuell erstellt? | |

### Technische Details

| # | Frage | Notizen |
|---|-------|---------|
| 24 | Gibt es Schnittstellen oder APIs bei den Tools, die Sie aktuell nutzen? | |

---

## Tipps für das Meeting

- **Zuhören > Reden:** Lasst den Verwalter erzählen. Die besten Erkenntnisse kommen aus Geschichten, nicht aus direkten Antworten.
- **Notizen machen:** Einer sollte mitschreiben, der andere führt das Gespräch.
- **Nicht sofort Lösungen versprechen:** Erst verstehen, dann vorschlagen.
- **Konkrete Beispiele erfragen:** Wenn er sagt "Recherche dauert lange" — nachfragen: "Können Sie ein konkretes Beispiel geben?"
- **Prio 3 nicht erzwingen:** Wenn die Zeit knapp wird, freundlich ansprechen: "Die restlichen Detailfragen können wir gerne per E-Mail oder in einem kurzen Folgetermin klären."

---

## Nach dem Meeting

- [ ] Notizen zusammenfassen und mit Heinrich Munz abgleichen
- [ ] Erste Use-Case-Hypothese formulieren
- [ ] Follow-up E-Mail mit offenen Prio-3-Fragen senden
- [ ] Nächsten Termin vereinbaren
- [ ] BMAD Brainstorming [BP] oder Produkt-Brief [CB] starten, basierend auf den Erkenntnissen
