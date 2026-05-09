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
- transactie-preview
- saldi-preview
- read-only data ophalen uit Google Sheets

## Productstatus

Huidige status:

- App title: `Portfolio`
- Fase 3 afgerond
- Streamlit frontend
- Live Google Sheets read-only integratie actief
- Mockdata fallback actief
- Geen write-back

Write-back naar Google Sheets is nog niet gebouwd.

## Architectuur

Google Sheets functioneert als databron en rekenlaag.

Google Apps Script functioneert als bestaande backend/engine.

Streamlit functioneert als frontend/mobile interface.

De app gebruikt een data-adapterlaag:

- `src/sheets_client.py`: Google Sheets read-only client
- `src/data_loader.py`: live/mock loading, parsing en normalisatie
- `src/mock_data.py`: lokale fallbackdata

De UI gebruikt hetzelfde interne dataformaat, ongeacht of data uit Google Sheets of mockdata komt.

## Datamodes

De app ondersteunt drie datamodes:

- `Live Google Sheets`: credentials en Sheet zijn geldig.
- `Mockdata`: geen Google configuratie aanwezig.
- `Fallback actief`: Google configuratie is aanwezig, maar live laden faalt veilig.

De app moet in alle drie scenario's starten zonder crash.

## Configuratie

Google Sheets integratie gebruikt service-account authenticatie.

Verplichte environment variables voor live data:

```env
GOOGLE_SHEET_ID=...
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
```

Optioneel:

```env
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
PORTFOLIO_DEBUG_GOOGLE=0
```

De Google Sheet moet gedeeld worden met het `client_email` adres uit het service-account JSON-bestand.

Read-only scope:

```text
https://www.googleapis.com/auth/spreadsheets.readonly
```

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

### KPI's

Totaal vermogen:

- toont alleen waarde
- geen winst/verlies badge
- geen 24u/30d/YTD

Totaal belegd vermogen:

- waarde
- winst/verlies
- 24u
- 30d
- YTD

Crypto:

- waarde
- winst/verlies
- 24u
- 30d
- YTD

Aandelen:

- waarde
- winst/verlies
- 24u
- 30d
- YTD

Dividend totaal:

- toont alleen waarde
- geen 24u/30d/YTD

### Performance-metrics

Performance wordt berekend uit `Historie`.

Definities:

- 24u: laatste beschikbare waarde versus waarde op of voor 1 dag geleden
- 30d: laatste beschikbare waarde versus waarde op of voor 30 dagen geleden
- YTD: laatste beschikbare waarde versus waarde op of voor 31-01-2026

Kolommen:

- Belegd: `Belegd Vermogen`
- Crypto: `Crypto W.`
- Aandelen: `DeGiro W.`

Als een referentiedatum ontbreekt, gebruikt de app de dichtstbijzijnde eerdere datum. Als die niet bestaat, toont de app `n.v.t.`.

### Targets

Het dashboard toont drie target cards:

1. EUR 100.000 totaal vermogen
2. EUR 100.000 belegd vermogen
3. 0.5 BTC

Elke target card toont:

- huidige waarde
- doelwaarde
- percentage voortgang
- progress bar
- compacte uitleg

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

Detailvisuals:

- waarde per categorie
- ingelegd vermogen per categorie
- winst/verlies per categorie
- belegd vermogen vs ingelegd vermogen
- equity curve

Categorieen:

- Crypto
- Aandelen

TSWE valt voor nu onder Aandelen.

## Transactie-tab

De Transactie-tab is preview-only.

Er wordt in fase 3 niets naar Google Sheets geschreven.

Type-volgorde:

1. Buy
2. Sell
3. Dividend
4. Profit
5. Initial

Buy is de default.

Velden:

- Datum
- Ticker
- Type
- Aantal
- Prijs per stuk
- Totaal
- Valuta

Datumformaat:

- dd-mm-yyyy

Er is geen apart transactiekostenveld. `Totaal` is inclusief eventuele transactiekosten.

Voor Buy, Sell en Initial:

- Totaal is leidend.
- Als Aantal en Totaal zijn ingevuld, berekent de app Prijs per stuk.
- Prijs per stuk wordt duidelijk als berekende waarde getoond.

Voor Dividend en Profit:

- Datum, Ticker, Type, Totaal en Valuta zijn belangrijk.
- Aantal is optioneel of minder prominent.

Bevestigen schrijft in fase 3 niets weg.

## Saldi-tab

De Saldi-tab toont live saldi wanneer Google Sheets beschikbaar is, maar aanpassen blijft preview-only.

De tab bevat:

- totaal cashsaldo
- splitsing Spaar / Vakanties / Vrije ruimte
- formulier om saldo te wijzigen
- huidige waarde
- nieuwe waarde
- verschil
- bevestiging

Er wordt in fase 3 niets naar Google Sheets geschreven.

## Google Sheets datacontract

Fase 3 leest read-only data uit:

- `Portfolio`
- `Saldi`
- `Historie`

Optioneel read-only:

- `Transacties`, alleen voor `Dividend totaal`

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

Gebruik:

- `Categorie` voor categorie
- `Ticker` voor ticker
- `Aantal` voor aantal
- `Inleg` als ingelegd vermogen
- `Waarde (EUR)` als actuele waarde
- `Winst (EUR)` als winst/verlies
- `ROI %` als rendement

Als `Inleg` ontbreekt of niet parsebaar is:

- Ingelegd vermogen = Waarde - Winst

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

Gebruik:

- `Totaal` voor equity curve totaal vermogen
- `Belegd Vermogen` voor belegd vermogen
- `Crypto W.` voor crypto waarde
- `DeGiro W.` voor aandelen waarde
- `BTC Aant.` voor BTC target
- `Inleg Tot.` voor totaal ingelegd belegd vermogen
- `Crypto I.` voor ingelegd crypto
- `DeGiro I.` voor ingelegd aandelen

### Transacties

Optioneel read-only voor dividend:

- Datum
- Ticker
- Type
- Aantal
- Prijs per stuk
- Kosten
- Totaal
- Valuta

Gebruik:

- filter `Type == Dividend`
- sommeer `Totaal`
- als lezen faalt, gebruik veilige fallback

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
- percentages blijven numerieke percentagewaarden volgens de UI-conventie
- datums worden day-first geparsed
- fout geformatteerde cellen mogen de app niet crashen

## Buiten scope fase 3

Niet bouwen in fase 3:

- schrijven naar Google Sheets
- transacties toevoegen aan Sheet
- saldi updaten in Sheet
- Apps Script vervangen
- Google Finance vervangen
- ROI-engine herbouwen
- Historie berekenen
- automatische snapshots maken
- realtime koersdata buiten de bestaande Sheet ophalen
- deploy
- React
- Next.js

## Geplande fase 4

Fase 4 is write-back voor transacties, nog niet geimplementeerd.

Geplande scope:

- append transacties naar Google Sheets
- alleen naar tabblad `Transacties`
- flow: preview -> bevestigen -> append row
- geen directe saldi-mutaties
- geen automatische Apps Script triggers
- geen delete/update van bestaande rijen

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

Dashboard blijft cockpit. Portfolio bevat details en analyse. Transactie en Saldi blijven preview-only tot de write-back fase.
