# Frühwarnsystem

Vier Indikatoren, täglich um 5:00 (Europe/Vienna) von einem Claude-Cloud-Agent
aktualisiert. Seite: siehe Repo-Beschreibung.

## Aufbau

| Datei | Zweck |
| --- | --- |
| `daten.json` | die einzige Datei, die der Agent inhaltlich pflegt |
| `bauen.py` | rendert `index.html` aus `daten.json`, schreibt `verlauf.jsonl` fort |
| `index.html` | Ausgabe — nicht von Hand bearbeiten, wird überschrieben |
| `verlauf.jsonl` | eine Zeile je Lauf, für spätere Trendauswertung |
| `ANLEITUNG.md` | was der Agent bei jedem Lauf tut |

## Lokal bauen

    python3 bauen.py
