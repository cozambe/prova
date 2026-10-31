# Nota Spese PIVA

Strumenti per gestire la nota spese della partita IVA.

## Componenti

| Cosa | Dove | Come funziona |
|---|---|---|
| App nota spese | `app/nota-spese.html`, pubblicata come artifact privato su claude.ai | Registro spese con database condiviso, foto degli scontrini (Claude legge data, fornitore, totale e IVA), note con scadenza, chiusura del mese, export CSV (separatore `;`, decimali con virgola) |
| Scansione Gmail | Attività programmata "Scansione Gmail spese PIVA", ogni lunedì alle 07:43 (Europe/Rome) | Cerca ricevute e fatture degli ultimi 8 giorni, le registra come "da verificare" assegnando l'intestatario (PIVA, Srl o personale), con link all'email, ed etichetta i thread `PIVA-Spese` |
| Promemoria | Google Calendar, "Chiusura mensile nota spese PIVA" | Ultimo giorno lavorativo del mese, 17:30 |

## Dati

Collezioni nel database dell'artifact:

- `spese`: `data`, `intestatario` (`piva` · `srl` = Edilmontaggi Project Srl · `personale`), `fornitore`, `descrizione`, `categoria`, `totale`, `iva`, `metodo`, `deducibile` (%), `tipo`, `stato` (`da_verificare` · `registrata` · `inviata`), `fonte` (`scontrino` · `email` · `manuale`), `note`, `ricevutaId`/`ricevutaUrl` (foto o PDF), `emailId`/`emailLink`/`emailOggetto`, `createdAt`, `updatedAt`
- `note`: `testo`, `scadenza`, `fatta`, `createdAt`

Le percentuali di deducibilità per categoria sono indicative (vitto 75%, auto 20%, telefono 80%): vanno confermate col commercialista e non si applicano al regime forfettario.

## Aggiornare l'app

Modifica `app/nota-spese.html` e ripubblicala sullo stesso URL dell'artifact.
