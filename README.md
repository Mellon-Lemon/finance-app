# Portfolio

Mobile-friendly Streamlit portfolio dashboard bovenop een bestaande Google Sheets + Google Apps Script finance engine.

## Projectstatus

Fase 4 is actief:

- Google Sheets live data werkt.
- Mockdata fallback blijft beschikbaar.
- Write-back is beschikbaar voor `Transacties` en `Saldi`.
- Write-back werkt alleen in `Live Google Sheets` mode.

Niet gebouwd:

- schrijven naar `Portfolio`
- schrijven naar `Historie`
- schrijven naar `Instellingen`
- bestaande transacties wijzigen of verwijderen
- Apps Script vervangen
- Google Finance vervangen

## Setup

Installeer Python en maak lokaal een virtual environment:

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

De Google Sheet moet met editorrechten gedeeld worden met het `client_email` adres uit dit service-account bestand. Er zijn geen extra Google Cloud rollen nodig buiten toegang tot de Sheet.

## Starten

```powershell
python -m streamlit run app.py
```

## Datamodes

De app kiest automatisch de best beschikbare databron:

- `Live Google Sheets`: `.env`, credentials en Sheet zijn geldig.
- `Mockdata`: er is geen Google configuratie aanwezig.
- `Fallback actief`: Google configuratie is aanwezig, maar live data laden faalt veilig.

Write-back is alleen actief bij `Live Google Sheets`.

In `Mockdata` en `Fallback actief` blijven previews werken, maar schrijft de app nooit naar Google Sheets.

## Google Sheets

Gelezen tabs:

- `Portfolio`
- `Saldi`
- `Historie`
- `Transacties`, optioneel voor `Dividend totaal`

Geschreven tabs:

- `Transacties`: append-only nieuwe transactierijen
- `Saldi`: update-only bestaande `Huidig Saldo` cel van een bestaand account

De app gebruikt de scope:

```text
https://www.googleapis.com/auth/spreadsheets
```

Nederlandse getalnotatie wordt centraal geparsed, bijvoorbeeld `0,46499113`, `EUR 22.465,00` en `40,95%`.

## Transacties

Nieuwe transacties worden pas geschreven na:

1. invoer
2. preview van de exacte Sheet-rij
3. expliciete bevestiging
4. klik op `Transactie opslaan`

De app schrijft naar `Transacties` met kolommen:

```text
Datum, Ticker, Type, Aantal, Prijs per stuk, Kosten, Totaal, Valuta
```

`Kosten` wordt altijd als `0` geschreven. `Totaal` is inclusief eventuele transactiekosten.

## Saldi

Saldo-updates worden pas geschreven na:

1. account kiezen
2. nieuwe waarde invoeren
3. preview controleren
4. expliciete bevestiging
5. klik op `Saldo opslaan`

De app update alleen de bestaande `Huidig Saldo` cel in het tabblad `Saldi`.

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
