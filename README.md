# Portfolio

Mobile-friendly Streamlit portfolio dashboard bovenop een bestaande Google Sheets + Google Apps Script finance engine.

## Projectstatus

Fase 3 is afgerond:

- Google Sheets read-only integratie werkt.
- Mockdata fallback blijft beschikbaar.
- De app toont de actieve datamode: `Live Google Sheets`, `Mockdata` of `Fallback actief`.
- Write-back is nog niet actief.

Nog niet gebouwd:

- transacties opslaan naar Google Sheets
- saldi updaten in Google Sheets
- bestaande Sheet-rijen wijzigen of verwijderen

## Setup

Installeer Python en maak daarna lokaal een virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Maak een lokaal `.env` bestand op basis van `.env.example`:

```env
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
```

Plaats het service-account JSON-bestand lokaal, bijvoorbeeld:

```text
credentials/service-account.json
```

De Google Sheet moet gedeeld worden met het `client_email` adres uit dit service-account bestand.

## Starten

```powershell
python -m streamlit run app.py
```

## Datamodes

De app kiest automatisch de best beschikbare databron:

- `Live Google Sheets`: `.env`, credentials en Sheet zijn geldig.
- `Mockdata`: er is geen Google configuratie aanwezig.
- `Fallback actief`: Google configuratie is aanwezig, maar live data laden faalt veilig.

In alle gevallen moet de app blijven starten.

## Google Sheets

Read-only tabs:

- `Portfolio`
- `Saldi`
- `Historie`

Optioneel read-only:

- `Transacties`, alleen voor `Dividend totaal`

De app gebruikt de read-only scope:

```text
https://www.googleapis.com/auth/spreadsheets.readonly
```

Nederlandse getalnotatie wordt centraal geparsed, bijvoorbeeld `0,46499113`, `EUR 22.465,00` en `40,95%`.

## Security

Commit nooit secrets:

- `.env`
- `credentials/`
- service-account keys
- token files

De service-account key blijft lokaal geheim. De app toont geen credentials-inhoud en geen volledige Spreadsheet IDs.

## Debug

Veilige Google Sheets diagnostiek wordt naar de terminal gelogd zonder secrets.

Een tijdelijke debug-expander in de UI kan lokaal worden aangezet met:

```env
PORTFOLIO_DEBUG_GOOGLE=1
```

Laat deze waarde uit of zet hem op `0` voor normaal gebruik.

## Geplande fase 4

Fase 4 is nog niet geimplementeerd. De geplande scope:

- append transacties naar het tabblad `Transacties`
- flow: preview -> bevestigen -> append row
- geen directe saldi-mutaties
- geen automatische Apps Script triggers
- geen delete/update van bestaande rijen
