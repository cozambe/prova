# I miei ascolti

Statistiche sulla musica che ascolto su Spotify: artisti, brani, generi, orari e giorni.

Il risultato è la pagina [`report.html`](report.html).

## Da dove arrivano i dati

| Fonte | Cosa contiene | Come arriva |
|---|---|---|
| `dati/ascolti_recenti.csv` | ultimi brani ascoltati, **senza orario** | Claude li annota ogni giorno |
| `dati/Streaming_History_Audio_*.json` | tutto lo storico, **con orario** | richiesta a Spotify (vedi sotto) |

### Come chiedere lo storico completo a Spotify

1. Vai su <https://www.spotify.com/it/account/privacy/>.
2. Spunta **"Cronologia di streaming estesa"** e clicca **Richiedi dati**.
3. Conferma dall'email. Spotify manda i file entro qualche giorno (al massimo 30).
4. Mettili nella cartella `dati/`, o mandali a Claude.

## I generi

Spotify non dice il genere dei brani. Lo decido io in [`generi.json`](generi.json), artista per artista.
Quando lo script trova un artista non classificato, lo segnala.

## Aggiornare il report

```
python3 analizza.py
```
