# Portfolio

Mobile-friendly Streamlit portfolio dashboard.

Fase 3 leest Google Sheets data read-only wanneer credentials beschikbaar zijn. Zonder geldige configuratie start de app automatisch met mockdata fallback.

## Starten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

## Mockdata fallback

De app gebruikt mockdata wanneer:

- `.env` ontbreekt
- `GOOGLE_SHEET_ID` ontbreekt
- service-account credentials ontbreken
- Google Sheets tijdelijk niet bereikbaar is
- de verplichte tabs geen bruikbare data teruggeven

De header toont de actieve databron: `Mockdata`, `Live Google Sheets` of `Fallback actief`.

## Google Sheets read-only

Maak lokaal een `.env` bestand op basis van `.env.example`:

```env
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
```

Plaats het service-account JSON-bestand lokaal, bijvoorbeeld:

```text
credentials/service-account.json
```

De Google Sheet moet gedeeld worden met het `client_email` adres uit het service-account JSON-bestand.

Fase 3 gebruikt alleen read-only toegang. De app schrijft nog niets naar Google Sheets.

## Gelezen tabs

Verplicht read-only:

- `Portfolio`
- `Saldi`
- `Historie`

Optioneel read-only:

- `Transacties`, alleen om `Dividend totaal` te berekenen

## Veiligheid

Commit nooit echte credentials. `.env`, `credentials/`, `service-account.json`, `*.credentials.json` en `token.json` staan in `.gitignore`.

## Scope fase 3

Wel:

- live data lezen als configuratie geldig is
- mockdata fallback behouden
- Nederlandse getalnotatie robuust parsen
- bestaande Streamlit UI behouden

Niet:

- schrijven naar Google Sheets
- transacties toevoegen
- saldi updaten
- Apps Script vervangen
- Google Finance vervangen
- live koersrefresh bouwen
