"""Statistiche dei miei ascolti Spotify.

Legge i file nella cartella dati/:
  - Streaming_History_Audio_*.json  storico esteso di Spotify (con orari)
  - StreamingHistory*.json           storico base di Spotify (ultimo anno, con orari)
  - ascolti_recenti.csv              rilevazioni giornaliere (senza orario)

e genera report.html con le classifiche per artista, brano, genere, ora e giorno.

Uso: python3 analizza.py
"""

import csv
import glob
import html
import json
import os
from collections import Counter
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

CARTELLA = os.path.dirname(os.path.abspath(__file__))
DATI = os.path.join(CARTELLA, "dati")
FUSO = ZoneInfo("Europe/Rome")
MIN_MS = 30_000  # sotto i 30 secondi lo consideriamo un salto, non un ascolto
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]


def carica_ascolti():
    """Restituisce una lista di dict: artista, brano, minuti, quando (datetime o None)."""
    ascolti = []

    for percorso in sorted(glob.glob(os.path.join(DATI, "Streaming_History_Audio_*.json"))):
        with open(percorso, encoding="utf-8") as f:
            for r in json.load(f):
                artista = r.get("master_metadata_album_artist_name")
                if not artista or r.get("ms_played", 0) < MIN_MS:
                    continue
                quando = datetime.fromisoformat(r["ts"].replace("Z", "+00:00")).astimezone(FUSO)
                ascolti.append({
                    "artista": artista,
                    "brano": r.get("master_metadata_track_name") or "?",
                    "minuti": r["ms_played"] / 60_000,
                    "quando": quando,
                })

    for percorso in sorted(glob.glob(os.path.join(DATI, "StreamingHistory*.json"))):
        with open(percorso, encoding="utf-8") as f:
            for r in json.load(f):
                if r.get("msPlayed", 0) < MIN_MS:
                    continue
                # Nello storico base endTime è in UTC
                quando = datetime.strptime(r["endTime"], "%Y-%m-%d %H:%M")
                quando = quando.replace(tzinfo=timezone.utc).astimezone(FUSO)
                ascolti.append({
                    "artista": r["artistName"],
                    "brano": r["trackName"],
                    "minuti": r["msPlayed"] / 60_000,
                    "quando": quando,
                })

    # Le rilevazioni giornaliere servono solo se manca lo storico ufficiale
    recenti = os.path.join(DATI, "ascolti_recenti.csv")
    if not ascolti and os.path.exists(recenti):
        with open(recenti, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ascolti.append({"artista": r["artista"], "brano": r["brano"], "minuti": 0, "quando": None})

    return ascolti


def barre(titolo, conteggi, ordina=True, unita="ascolti"):
    voci = conteggi.most_common(15) if ordina else list(conteggi.items())
    if not voci:
        return ""
    massimo = max(v for _, v in voci) or 1
    righe = "".join(
        f'<div class="riga"><span class="etichetta">{html.escape(str(k))}</span>'
        f'<span class="barra"><span style="width:{100 * v / massimo:.1f}%"></span></span>'
        f'<span class="valore">{v:g}</span></div>'
        for k, v in voci
    )
    return f'<section><h2>{titolo}</h2><p class="unita">{unita}</p>{righe}</section>'


def genera_report(ascolti, generi):
    con_orario = [a for a in ascolti if a["quando"]]
    artisti = Counter(a["artista"] for a in ascolti)
    brani = Counter(f'{a["brano"]} · {a["artista"]}' for a in ascolti)
    per_genere = Counter(generi.get(a["artista"], "Non classificato") for a in ascolti)
    minuti_artista = Counter()
    for a in ascolti:
        minuti_artista[a["artista"]] += round(a["minuti"])

    sezioni = [
        barre("Artisti più ascoltati", artisti),
        barre("Brani più ascoltati", brani),
        barre("Generi", per_genere),
    ]

    if con_orario:
        ore = Counter({f"{h:02d}:00": 0 for h in range(24)})
        ore.update(f'{a["quando"].hour:02d}:00' for a in con_orario)
        giorni = Counter({g: 0 for g in GIORNI})
        giorni.update(GIORNI[a["quando"].weekday()] for a in con_orario)
        mesi = Counter(a["quando"].strftime("%Y-%m") for a in con_orario)
        sezioni += [
            barre("Minuti per artista", minuti_artista, unita="minuti"),
            barre("A che ora ascolto", ore, ordina=False),
            barre("In che giorno ascolto", giorni, ordina=False),
            barre("Mese per mese", Counter(dict(sorted(mesi.items()))), ordina=False),
        ]
        inizio = min(a["quando"] for a in con_orario).strftime("%d/%m/%Y")
        fine = max(a["quando"] for a in con_orario).strftime("%d/%m/%Y")
        periodo = f"dal {inizio} al {fine}"
        nota = ""
    else:
        periodo = "rilevazioni giornaliere"
        nota = ('<p class="nota">Statistiche per orario e giorno non ancora disponibili: '
                "servono i file dello storico Spotify nella cartella <code>dati/</code>.</p>")

    ore_totali = sum(a["minuti"] for a in ascolti) / 60
    riepilogo = (f'<div class="kpi"><div><b>{len(ascolti)}</b>ascolti</div>'
                 f'<div><b>{len(artisti)}</b>artisti</div>'
                 f'<div><b>{ore_totali:.0f}</b>ore</div></div>')

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>I miei ascolti</title>
<style>
  :root {{ --sfondo:#faf8f5; --testo:#1f1d1a; --tenue:#6b665e; --barra:#c2410c; --traccia:#ece7df; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --sfondo:#171615; --testo:#ece9e4; --tenue:#a19b91; --barra:#fb923c; --traccia:#2a2826; }}
  }}
  body {{ background:var(--sfondo); color:var(--testo); font:16px/1.5 system-ui, sans-serif;
         max-width:760px; margin:0 auto; padding:24px 16px; }}
  h1 {{ margin:0; }} .periodo {{ color:var(--tenue); margin:4px 0 20px; }}
  .kpi {{ display:flex; gap:12px; margin-bottom:8px; }}
  .kpi div {{ flex:1; background:var(--traccia); border-radius:10px; padding:12px; color:var(--tenue); }}
  .kpi b {{ display:block; font-size:28px; color:var(--testo); }}
  section {{ margin-top:32px; }} h2 {{ margin:0; font-size:20px; }}
  .unita {{ color:var(--tenue); margin:0 0 8px; font-size:14px; }}
  .riga {{ display:grid; grid-template-columns:minmax(0,38%) 1fr 48px; gap:10px; align-items:center; margin:4px 0; }}
  .etichetta {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:14px; }}
  .barra {{ background:var(--traccia); border-radius:4px; height:14px; }}
  .barra span {{ display:block; height:100%; background:var(--barra); border-radius:4px; }}
  .valore {{ text-align:right; font-variant-numeric:tabular-nums; font-size:14px; color:var(--tenue); }}
  .nota {{ background:var(--traccia); padding:12px; border-radius:10px; margin-top:24px; }}
</style>
</head>
<body>
<h1>I miei ascolti</h1>
<p class="periodo">{periodo}</p>
{riepilogo}
{nota}
{''.join(sezioni)}
</body>
</html>
"""


def main():
    with open(os.path.join(CARTELLA, "generi.json"), encoding="utf-8") as f:
        generi = json.load(f)
    ascolti = carica_ascolti()
    destinazione = os.path.join(CARTELLA, "report.html")
    with open(destinazione, "w", encoding="utf-8") as f:
        f.write(genera_report(ascolti, generi))
    senza_genere = sorted({a["artista"] for a in ascolti} - generi.keys())
    print(f"{len(ascolti)} ascolti analizzati -> {destinazione}")
    if senza_genere:
        print("Artisti senza genere in generi.json:", ", ".join(senza_genere))


if __name__ == "__main__":
    main()
