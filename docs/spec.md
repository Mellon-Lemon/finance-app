# Portfolio App - Specificatie

## Doel

Portfolio is een mobile-friendly Streamlit dashboard bovenop een bestaande Google Sheets + Google Apps Script finance engine.

Google Sheets en Apps Script blijven leidend voor:

- portfolio-berekeningen
- ROI-berekeningen
- historische snapshots
- Google Finance koersdata
- dividendlogica
- target tracking

De Streamlit app is de frontend/interface voor:

- dashboardweergave
- portfolio-analyse
- transactie-invoer met gecontroleerde write-back
- saldi-aanpassing met gecontroleerde write-back
- live data ophalen uit Google Sheets
- mockdata fallback

## Productstatus

Huidige status:

- App title: `Portfolio`
- Fase 4 actief
- Streamlit frontend
- Live Google Sheets integratie actief
- Mockdata fallback actief
- Write-back alleen voor `Transacties` en `Saldi`

Niet gebouwd:

- write-back naar `Portfolio`
- write-back naar `Historie`
- write-back naar `Instellingen`
- Apps Script triggers vanuit de app
- automatische koersdata ophalen
- deploy

## Architectuur

Google Sheets functioneert als databron en rekenlaag.

Google Apps Script functioneert als bestaande backend/engine.

Streamlit functioneert als frontend/mobile interface.

De app gebruikt een data-adapterlaag:

- `src/sheets_client.py`: Google Sheets client voor lezen en beperkte write-back
- `src/data_loader.py`: live/mock loading, parsing en normalisatie
- `src/mock_data.py`: lokale fallbackdata

De UI gebruikt hetzelfde interne dataformaat, ongeacht of data uit Google Sheets of mockdata komt.

## Datamodes

De app ondersteunt drie datamodes:

- `Live Google Sheets`: credentials en Sheet zijn geldig.
- `Mockdata`: geen Google configuratie aanwezig.
- `Fallback actief`: Google configuratie is aanwezig, maar live laden faalt veilig.

Write-back is alleen actief in `Live Google Sheets`.

In `Mockdata` en `Fallback actief`:

- previews blijven werken
- opslaan is niet beschikbaar
- er wordt nooit naar Google Sheets geschreven

## Configuratie

Google Sheets integratie gebruikt service-account authenticatie.

Verplichte environment variables:

```env
GOOGLE_SHEET_ID=...
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
```

Optioneel:

```env
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
PORTFOLIO_DEBUG_GOOGLE=0
```

De Google Sheet moet met editorrechten gedeeld worden met het `client_email` adres uit het service-account JSON-bestand.

Scope:

```text
https://www.googleapis.com/auth/spreadsheets
```

Deze scope is nodig voor fase 4 write-back naar `Transacties` en `Saldi`.

Secrets mogen nooit worden gecommit:

- `.env`
- `credentials/`
- service-account keys
- token files

## Debug en logging

De normale UI toont alleen de actieve databron:

- `Live Google Sheets`
- `Mockdata`
- `Fallback actief`

Veilige diagnostiek wordt intern gelogd zonder secrets of volledige Spreadsheet IDs.

Een tijdelijke debug-expander mag lokaal worden aangezet via:

```env
PORTFOLIO_DEBUG_GOOGLE=1
```

Deze expander mag geen credentials-inhoud of volledige Spreadsheet IDs tonen.

## Tabstructuur

De app bevat vier hoofdtabbladen:

1. Dashboard
2. Portfolio
3. Transactie
4. Saldi

## Dashboard

Dashboard is een clean cockpit-overzicht.

Het dashboard bevat:

- KPI overzicht
- target progress cards
- equity curve

KPI's:

- Totaal vermogen: waarde, geen performance badges
- Totaal belegd vermogen: waarde, winst/verlies, 24u, 30d, YTD
- Crypto: waarde, winst/verlies, 24u, 30d, YTD
- Aandelen: waarde, winst/verlies, 24u, 30d, YTD
- Dividend totaal: waarde, geen performance badges

Performance wordt berekend uit `Historie`.

YTD-start:

- 31-01-2026

Targets:

- EUR 100.000 totaal vermogen
- EUR 100.000 belegd vermogen
- 0.5 BTC

## Portfolio-tab

Portfolio is het detail/analyse-tabblad.

Volgorde:

1. Holdings tabel
2. Detailvisuals

Holdings tabel:

- Ticker
- Categorie
- Aantal
- Ingelegd vermogen
- Waarde
- Winst
- ROI

Categorieen:

- Crypto
- Aandelen

TSWE valt voor nu onder Aandelen.

## Transactie-tab

De Transactie-tab heeft in fase 4 gecontroleerde write-back.

Write-back:

- alleen in `Live Google Sheets`
- alleen append-only naar tabblad `Transacties`
- nooit update/delete van bestaande transacties
- nooit schrijven naar `Portfolio`, `Historie` of `Instellingen`

Flow:

1. Gebruiker vult formulier in.
2. App toont preview van exact de rij die naar Google Sheets gaat.
3. Gebruiker bevestigt expliciet.
4. App appendt pas daarna een rij naar `Transacties`.

Kolomvolgorde `Transacties`:

1. Datum
2. Ticker
3. Type
4. Aantal
5. Prijs per stuk
6. Kosten
7. Totaal
8. Valuta

Type-volgorde:

1. Buy
2. Sell
3. Dividend
4. Profit
5. Initial

Buy is de default.

Datumformaat:

- dd-mm-yyyy

Kosten:

- geen apart UI-veld
- altijd `0` naar de Sheet
- `Totaal` is inclusief eventuele transactiekosten

Buy, Sell en Initial:

- Aantal vereist
- Totaal vereist
- Prijs per stuk = Totaal / Aantal

Dividend:

- Aantal = 0
- Prijs per stuk = 0
- Kosten = 0
- Totaal moet groter zijn dan 0

Profit:

- Aantal = 0
- Prijs per stuk = 0
- Kosten = 0
- Totaal mag positief of negatief zijn

## Saldi-tab

De Saldi-tab heeft in fase 4 gecontroleerde write-back.

Write-back:

- alleen in `Live Google Sheets`
- alleen naar tabblad `Saldi`
- alleen update van bestaande rij
- alleen kolom `Huidig Saldo`
- geen nieuwe saldi-rijen
- geen delete
- geen accountnaam-wijziging
- geen Historie-update

Flow:

1. App toont huidig totaal cashsaldo.
2. App toont splitsing Spaar / Vakanties / Vrije ruimte.
3. Gebruiker kiest account.
4. App toont huidige waarde.
5. Gebruiker vult nieuwe waarde in.
6. App toont verschil en preview.
7. Gebruiker bevestigt expliciet.
8. App update alleen de juiste `Huidig Saldo` cel.

Validatie:

- account moet bestaan
- nieuwe waarde moet numeriek zijn
- waarde mag 0 zijn
- waarde mag niet negatief zijn

## Google Sheets datacontract

Gelezen tabs:

- `Portfolio`
- `Saldi`
- `Historie`
- `Transacties`, optioneel voor dividend

Geschreven tabs:

- `Transacties`
- `Saldi`

Niet geschreven tabs:

- `Portfolio`
- `Historie`
- `Instellingen`
- alle andere tabs

### Portfolio

Kolommen:

- Categorie
- Ticker
- Aantal
- Inleg
- Koers (EUR)
- Waarde (EUR)
- Winst (EUR)
- ROI %

### Saldi

Kolommen:

- Account
- Huidig Saldo

Accounts:

- Spaar
- Vakanties
- Vrije ruimte

### Historie

Kolommen:

- Datum
- Totaal
- Spaar
- Vakanties
- Vrije Ruimte
- Belegd Vermogen
- Crypto W.
- Crypto I.
- DeGiro W.
- DeGiro I.
- BTC Aant.
- Inleg Tot.

### Transacties

Kolommen:

- Datum
- Ticker
- Type
- Aantal
- Prijs per stuk
- Kosten
- Totaal
- Valuta

## Nederlandse parsing

Parsing staat centraal in `src/data_loader.py`.

Ondersteunde voorbeelden:

- `0,46499113` -> `0.46499113`
- `2` -> `2`
- `426` -> `426`
- `34,81` -> `34.81`
- `EUR 22.465,00` -> `22465.00`
- `40,95%` -> `40.95`
- `8-5-2026`
- `8-5-2026 22:10:34`
- `31-01-2026`

Regels:

- komma is decimaalteken
- punten worden alleen als duizendtalscheiding verwijderd
- datums worden day-first geparsed
- fout geformatteerde cellen mogen de app niet crashen

## Buiten scope fase 4

Niet bouwen in fase 4:

- schrijven naar `Portfolio`
- schrijven naar `Historie`
- schrijven naar `Instellingen`
- bestaande transacties updaten
- bestaande transacties verwijderen
- saldi-rijen toevoegen of verwijderen
- Apps Script vervangen
- Apps Script triggers vanuit Streamlit
- Google Finance vervangen
- ROI-engine herbouwen
- automatische snapshots maken
- realtime koersdata buiten de bestaande Sheet ophalen
- deploy
- React
- Next.js

## Projectstructuur

```text
finance-app/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- docs/
|   `-- spec.md
|-- assets/
|   `-- header-placeholder.svg
`-- src/
    |-- __init__.py
    |-- config.py
    |-- dashboard.py
    |-- data_loader.py
    |-- formatting.py
    |-- mock_data.py
    |-- portfolio.py
    |-- saldi.py
    |-- sheets_client.py
    |-- styles.py
    |-- transactions.py
    `-- ui.py
```

## UX richtlijnen

- minimalistisch
- fintech stijl
- mobile-first
- snelle invoer
- grote touch targets
- rustige spacing
- duidelijke card hierarchy

Dashboard blijft cockpit. Portfolio bevat details en analyse. Transactie en Saldi gebruiken preview + bevestiging voordat write-back plaatsvindt.
