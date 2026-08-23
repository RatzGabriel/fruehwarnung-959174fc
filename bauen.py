#!/usr/bin/env python3
"""Baut index.html aus daten.json. Schreibt ausserdem verlauf.jsonl fort."""

import html
import json
import pathlib
from datetime import datetime, timezone

HIER = pathlib.Path(__file__).parent
DATEN = HIER / "daten.json"
ZIEL = HIER / "index.html"
VERLAUF = HIER / "verlauf.jsonl"

FARBE = {
    "ruhig": ("ok", "ruhig"),
    "beobachtung": ("watch", "Beobachtung"),
    "warnung": ("warn", "nah an der Schwelle"),
    "ausgeloest": ("alarm", "ausgelöst"),
}


def balken(s):
    """Positionsbalken fuer Sensoren mit numerischer Skala."""
    if not s.get("skala") or s.get("wert") is None:
        return ""
    lo, hi = s["skala"]
    spanne = hi - lo
    pos = max(0.0, min(1.0, (s["wert"] - lo) / spanne)) * 100
    marke = ""
    if s.get("schwelle") is not None:
        m = max(0.0, min(1.0, (s["schwelle"] - lo) / spanne)) * 100
        marke = (
            f'<span class="mark" style="left:{m:.1f}%"></span>'
            f'<span class="marklabel" style="left:{m:.1f}%">'
            f'{html.escape(s["schwelle_anzeige"])}</span>'
        )
    return (
        '<div class="scale">'
        f'<div class="track">{marke}'
        f'<span class="dot" style="left:{pos:.1f}%"></span></div>'
        f'<div class="ends"><span>{lo:g}</span><span>{hi:g}</span></div>'
        "</div>"
    )


def karte(s):
    kl, label = FARBE.get(s["status"], ("watch", s["status"]))
    return f"""      <article class="card {kl}">
        <header>
          <span class="badge">{html.escape(label)}</span>
          <h2>{html.escape(s['name'])}</h2>
          <p class="sub">{html.escape(s['kurz'])}</p>
        </header>
        <div class="value">{html.escape(s['anzeige'])}</div>
        <div class="gap">{html.escape(s['abstand'])}</div>
        {balken(s)}
        <p class="ctx">{html.escape(s['kontext'])}</p>
        <footer>
          <span>Stand {html.escape(s['stand_wert'])}</span>
          <span>{html.escape(s['frequenz'])}</span>
          <a href="{html.escape(s['quelle'])}" rel="noopener">{html.escape(s['quelle_name'])}</a>
        </footer>
      </article>"""


def termin(t):
    return (
        f"<tr><td class=\"d\">{html.escape(t['datum'])}</td>"
        f"<td>{html.escape(t['titel'])}</td>"
        f"<td class=\"v\">{html.escape(t['volumen'])}</td></tr>"
    )


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))

    zeile = {
        "zeit": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "werte": {s["id"]: s.get("wert") for s in d["sensoren"]},
        "status": {s["id"]: s["status"] for s in d["sensoren"]},
    }
    with VERLAUF.open("a", encoding="utf-8") as f:
        f.write(json.dumps(zeile, ensure_ascii=False) + "\n")

    alarme = sum(1 for s in d["sensoren"] if s["status"] in ("warnung", "ausgeloest"))
    ampel = "alarm" if any(s["status"] == "ausgeloest" for s in d["sensoren"]) else (
        "warn" if alarme else "ok")

    karten = "\n".join(karte(s) for s in d["sensoren"])
    termine = "\n            ".join(termin(t) for t in d.get("termine", []))

    ZIEL.write_text(SEITE.format(
        stand=html.escape(d["stand_anzeige"]),
        lage=html.escape(d["lage"]),
        ampel=ampel,
        anzahl=alarme,
        karten=karten,
        termine=termine,
    ), encoding="utf-8")
    print(f"index.html gebaut — {alarme} von {len(d['sensoren'])} Sensoren auffaellig")


SEITE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Frühwarnsystem</title>
<style>
:root{{
  --bg:#faf9f7; --panel:#ffffff; --line:#e6e2dc; --text:#1c1a17; --muted:#6f6a63;
  --ok:#2f7d55; --watch:#4a6fa5; --warn:#b06a12; --alarm:#b3341f;
  --okbg:#eaf4ee; --watchbg:#eaf0f8; --warnbg:#fbf1e2; --alarmbg:#fbeae7;
  --shadow:0 1px 2px rgba(0,0,0,.04),0 8px 24px rgba(0,0,0,.05);
}}
@media (prefers-color-scheme:dark){{
  :root{{
    --bg:#161513; --panel:#201f1c; --line:#33312c; --text:#f0ede8; --muted:#9d968c;
    --ok:#6fc292; --watch:#8fb0e0; --warn:#e6a94e; --alarm:#e8735c;
    --okbg:#1d2f26; --watchbg:#1e2733; --warnbg:#332918; --alarmbg:#33201d;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35);
  }}
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);
  font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1100px;margin:0 auto;padding:48px 24px 72px}}
header.top{{display:flex;flex-wrap:wrap;align-items:baseline;gap:14px;margin-bottom:8px}}
h1{{font-size:1.5rem;font-weight:660;letter-spacing:-.02em;margin:0}}
.stand{{color:var(--muted);font-size:.86rem;font-variant-numeric:tabular-nums}}
.lage{{margin:20px 0 36px;padding:20px 22px;background:var(--panel);border:1px solid var(--line);
  border-radius:14px;box-shadow:var(--shadow);max-width:76ch}}
.lage.alarm{{border-left:4px solid var(--alarm)}}
.lage.warn{{border-left:4px solid var(--warn)}}
.lage.ok{{border-left:4px solid var(--ok)}}
.lage p{{margin:0;color:var(--text)}}
.grid{{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:22px 22px 18px;box-shadow:var(--shadow);display:flex;flex-direction:column}}
.card h2{{font-size:1.06rem;font-weight:640;margin:.35rem 0 .15rem;letter-spacing:-.01em}}
.sub{{margin:0;color:var(--muted);font-size:.87rem}}
.badge{{display:inline-block;font-size:.72rem;font-weight:640;letter-spacing:.03em;
  text-transform:uppercase;padding:3px 9px;border-radius:999px}}
.card.ok .badge{{background:var(--okbg);color:var(--ok)}}
.card.watch .badge{{background:var(--watchbg);color:var(--watch)}}
.card.warn .badge{{background:var(--warnbg);color:var(--warn)}}
.card.alarm .badge{{background:var(--alarmbg);color:var(--alarm)}}
.value{{font-size:2.1rem;font-weight:680;letter-spacing:-.03em;margin:16px 0 2px;
  font-variant-numeric:tabular-nums}}
.card.warn .value{{color:var(--warn)}}
.card.alarm .value{{color:var(--alarm)}}
.gap{{color:var(--muted);font-size:.88rem}}
.scale{{margin:20px 0 4px}}
.track{{position:relative;height:6px;background:var(--line);border-radius:99px}}
.dot{{position:absolute;top:50%;width:13px;height:13px;border-radius:50%;
  background:var(--text);transform:translate(-50%,-50%);border:2px solid var(--panel)}}
.card.warn .dot{{background:var(--warn)}}
.card.alarm .dot{{background:var(--alarm)}}
.mark{{position:absolute;top:-5px;width:2px;height:16px;background:var(--alarm);
  transform:translateX(-50%);border-radius:2px}}
.marklabel{{position:absolute;top:16px;transform:translateX(-50%);font-size:.7rem;
  color:var(--alarm);white-space:nowrap;font-variant-numeric:tabular-nums}}
.ends{{display:flex;justify-content:space-between;margin-top:22px;font-size:.72rem;
  color:var(--muted);font-variant-numeric:tabular-nums}}
.ctx{{font-size:.9rem;color:var(--muted);margin:16px 0 0;flex:1}}
.card footer{{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:18px;padding-top:14px;
  border-top:1px solid var(--line);font-size:.76rem;color:var(--muted)}}
.card footer a{{color:var(--watch);text-decoration:none}}
.card footer a:hover{{text-decoration:underline}}
h3{{font-size:1.05rem;font-weight:640;margin:44px 0 14px;letter-spacing:-.01em}}
.tablewrap{{overflow-x:auto;background:var(--panel);border:1px solid var(--line);
  border-radius:14px;box-shadow:var(--shadow)}}
table{{border-collapse:collapse;width:100%;min-width:460px;font-size:.9rem}}
th,td{{text-align:left;padding:11px 18px;border-bottom:1px solid var(--line)}}
th{{font-size:.74rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);
  font-weight:620}}
tr:last-child td{{border-bottom:none}}
td.d,td.v{{font-variant-numeric:tabular-nums;white-space:nowrap}}
td.v{{text-align:right;color:var(--muted)}}
.foot{{margin-top:40px;font-size:.78rem;color:var(--muted);max-width:70ch}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>Frühwarnsystem</h1>
    <span class="stand">Stand {stand} · {anzahl} von 4 auffällig</span>
  </header>

  <div class="lage {ampel}"><p>{lage}</p></div>

  <div class="grid">
{karten}
  </div>

  <h3>Auktionstermine September</h3>
  <div class="tablewrap">
    <table>
      <thead><tr><th>Datum</th><th>Instrument</th><th>Volumen</th></tr></thead>
      <tbody>
            {termine}
      </tbody>
    </table>
  </div>

  <p class="foot">Wird täglich um 5:00 automatisch neu gebaut. Die Frequenzangabe je Karte
  sagt, wie oft sich der Wert überhaupt ändern kann — die Fed-Bilanz erscheint donnerstags,
  Auktionsergebnisse nur am Auktionstag. Keine Anlageberatung.</p>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
