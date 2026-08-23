# Anleitung für den täglichen Lauf

Ziel: `daten.json` mit den aktuellen Werten füllen, `python3 bauen.py` laufen lassen,
Ergebnis pushen. `index.html` niemals von Hand schreiben.

## Die vier Sensoren

### 1. `us10y` — US-10-Jahres-Rendite
Schwelle **5,00 %**. Frequenz: täglich, nur Handelstage.
Quelle: `https://fred.stlouisfed.org/series/DGS10` oder eine Marktseite.
Status: `ruhig` unter 4,50 · `warnung` ab 4,50 · `ausgeloest` ab 5,00.

### 2. `brent` — Brent
Schwelle **100 USD**. Frequenz: täglich.
Status: `ruhig` unter 85 · `warnung` ab 85 · `ausgeloest` ab 100.
Wichtiger als der Tagesstand ist die Bewegung über vier Wochen — in `kontext` nennen.

### 3. `fed` — Fed-Bilanz
Quelle: H.4.1, **erscheint donnerstags 16:30 ET**. An anderen Tagen bleibt der Wert
der Vorwoche stehen; `stand_wert` dann unverändert lassen, nicht künstlich neu datieren.
QT endete im Dezember 2025, die Bilanz wächst wieder — der Sensor steht auf
`ausgeloest`. Neue sinnvolle Schwelle: Rückkehr zu aktiven Käufen (Reserve-Management-
Käufe zählen nicht) oder ein Wochenzuwachs über 25 Mrd USD.

### 4. `auktionen` — DE/FR-Auktionen
Kalender: `https://www.deutsche-finanzagentur.de/en/federal-securities/issuances/issuance-calendar`
und `https://www.aft.gouv.fr/en`.
An einem Auktionstag: Deckungsquote (bid-to-cover) und ob das Volumen gekürzt wurde
in `kontext` eintragen, Status auf `warnung` bei Deckung unter 1,2 oder bei Kürzung.
Sonst `beobachtung` und die kommenden Termine in `termine` pflegen.

## Ablauf

1. Werte recherchieren. Bei jedem Wert notieren, von welchem Tag er stammt.
2. `daten.json` schreiben: `stand_anzeige`, je Sensor `wert`, `anzeige`, `status`,
   `abstand`, `stand_wert`, `kontext`. `lage` ist ein Absatz, der die Sensoren
   zusammen liest — nicht die Kartentexte wiederholen.
3. `python3 bauen.py`
4. Committen und pushen (siehe unten).

## Regeln

- **Keine Zahl ohne Datum.** Ist ein Wert nicht auffindbar, den alten stehen lassen und
  das in `kontext` sagen. Niemals schätzen oder fortschreiben.
- **Nicht dramatisieren.** Ein Sensor, der sich seit gestern nicht bewegt hat, bekommt
  keinen neuen Alarmton.
- `lage` beschreibt die Lage, nicht die Meinung. Keine Handelsempfehlungen.
- Die Frequenzangaben stimmen lassen: Fed wöchentlich, Auktionen an Terminen.

## Push

    git add -A
    git -c user.email=gabrielratz84@gmail.com -c user.name=RatzGabriel \
        commit -q --amend -m "Stand $(date +%d.%m.%Y)"
    git push -q --force origin main

`--amend` plus `--force` hält das Repo bei genau einem Commit; `verlauf.jsonl` wächst
trotzdem mit, weil die Datei im Arbeitsverzeichnis bleibt.
