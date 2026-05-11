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
- Fase 5B actief
- Streamlit frontend
- Live Google Sheets integratie actief
- Mockdata fallback actief
- Write-back alleen voor `Transacties` en `Saldi`
- Handmatige data opnieuw laden leest Google Sheets opnieuw
- Optionele Apps Script Web App refresh voor `refreshPortfolioOnly()`
- Handmatige snapshot via Apps Script `manualPortfolioSnapshot()` is beschikbaar na expliciete bevestiging
- Dashboard toont compacte BTC/TSWE koerscards met 24u, 7d, 30d en YTD performance uit `Historie`
- Transacties kunnen achter elkaar worden toegevoegd
- Recente transacties worden getoond in de Transactie-tab
- Veilige delete van maximaal de laatste 3 transacties per ticker is beschikbaar in Live mode
- Actieve navigatiesectie blijft behouden na interacties
- Portfolio holdings hebben een compacte mobielvriendelijke weergave
- Handmatige `Live Google Sheets` / `Demo / Mockdata` datamodus is beschikbaar
- Delete-flow gebruikt unieke widget keys om duplicate element IDs te voorkomen
- Mobile-first UX-refactor actief: compacte app-shell, `Beheer`-sectie, icon-navigatie en herbruikbare card-componenten

Niet gebouwd:

- write-back naar `Portfolio`
- directe write-back naar `Historie` vanuit Python
- write-back naar `Instellingen`
- automatische koersdata ophalen
- `dailyPortfolioSnapshot()` vanuit Streamlit
- Historie snapshots rechtstreeks schrijven vanuit Python
- e-mail versturen vanuit Streamlit
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

De app ondersteunt een handmatige datamodus plus veilige fallback.

- `Live Google Sheets`: gebruikt echte Google Sheets data wanneer credentials en Sheet geldig zijn.
- `Demo / Mockdata`: gebruikt altijd lokale mockdata.
- `Fallback actief`: Google configuratie is aanwezig, maar live laden faalt veilig.

De gekozen datamodus blijft in `session_state` staan tijdens reruns.

In `Demo / Mockdata`:

- `load_finance_data(force_mock=True)` laadt direct mockdata
- mockdata bestaat uit fictieve holdings, saldi, historie, dividend, transacties en koerswaarden
- er wordt geen Google Sheets call gedaan
- er wordt geen Apps Script call gedaan
- er wordt niets naar Google Sheets geschreven
- er wordt niets uit Google Sheets verwijderd
- write/delete knoppen zijn uitgeschakeld of verborgen
- `Portfolio bijwerken` toont een veilige melding en triggert niets
- `Snapshot maken` is niet beschikbaar en triggert niets
- de UI toont expliciet `Demo / Mockdata`

Write-back, delete, `Portfolio bijwerken` en `Snapshot maken` zijn alleen actief in echte `Live Google Sheets` mode.

In `Demo / Mockdata` en `Fallback actief`:

- previews blijven werken
- opslaan is niet beschikbaar
- er wordt nooit naar Google Sheets geschreven
- er wordt nooit uit Google Sheets verwijderd
- er wordt nooit een Apps Script actie aangeroepen

## Data Opnieuw Laden

Fase 5B gebruikt de knop `Data opnieuw laden`.

App-open is read-only:

- Streamlit leest data uit Google Sheets of mockdata
- Streamlit roept geen Apps Script aan bij startup
- Streamlit werkt Portfolio niet automatisch bij bij startup

Doel:

- Streamlit cache legen
- Google Sheets opnieuw lezen via de bestaande data-loader
- app opnieuw renderen

De refresh mag alleen lezen.

De refresh doet niet:

- Apps Script triggeren
- `updatePortfolio` starten
- naar `Historie` schrijven
- e-mail versturen
- live koersdata ophalen buiten de bestaande Sheet
- nieuwe write-back toevoegen

De knop werkt veilig in alle datamodes:

- `Live Google Sheets`
- `Demo / Mockdata`
- `Fallback actief`

Na succesvolle write-back naar `Transacties` of `Saldi` mag de app dezelfde refresh uitvoeren om stale data te vermijden.

## Portfolio Bijwerken

De app kan optioneel een Apps Script Web App endpoint aanroepen met de knop `Portfolio bijwerken`.

Doel:

- Apps Script action `refresh` uitvoeren
- Apps Script `refreshPortfolioOnly()` uitvoeren
- het `Portfolio` tabblad laten bijwerken door de bestaande Apps Script engine
- daarna Streamlit cache legen en Google Sheets opnieuw lezen

Deze actie is logisch gescheiden van `Data opnieuw laden`.

`Portfolio bijwerken` doet niet:

- naar `Historie` schrijven
- `dailyPortfolioSnapshot()` aanroepen
- e-mail versturen
- rechtstreeks naar het `Portfolio` tabblad schrijven vanuit Python
- Google Finance of portfolioformules vervangen

De knop werkt alleen in `Live Google Sheets` mode en alleen als de Apps Script configuratie aanwezig is. In `Demo / Mockdata` en `Fallback actief` toont de app een nette melding en wordt geen echte update geprobeerd.

Na succesvolle write-back naar `Transacties` of `Saldi`:

- als de Apps Script endpoint-configuratie aanwezig is, roept de app automatisch `refreshPortfolioOnly()` aan en leest daarna Google Sheets opnieuw
- als de configuratie ontbreekt, blijft de write-back geslaagd en toont de app dat Portfolio bijwerken nog niet geconfigureerd is

## Handmatige Snapshot

De app kan optioneel hetzelfde Apps Script Web App endpoint aanroepen met de knop `Snapshot maken`.

Doel:

- Apps Script action `manual_snapshot` uitvoeren
- Apps Script `manualPortfolioSnapshot()` uitvoeren
- het `Portfolio` tabblad laten bijwerken door de bestaande Apps Script engine
- precies een nieuwe `Historie`-regel laten schrijven door Apps Script
- daarna Streamlit cache legen en Google Sheets opnieuw lezen

`Snapshot maken` doet niet:

- `dailyPortfolioSnapshot()` aanroepen
- e-mail versturen
- rechtstreeks naar `Historie` schrijven vanuit Python
- rechtstreeks naar `Portfolio` schrijven vanuit Python
- Google Finance of portfolioformules vervangen

De flow vereist expliciete bevestiging:

1. Gebruiker klikt `Snapshot maken` in `Beheer`.
2. De app toont dat dit een nieuwe regel naar `Historie` schrijft maar geen e-mail verstuurt.
3. De app toont dat meerdere snapshots per dag zijn toegestaan maar historische grafieken beinvloeden.
4. Gebruiker vinkt `Ik bevestig dat ik handmatig een Historie-snapshot wil maken.` aan.
5. Gebruiker klikt `Snapshot definitief maken`.
6. Pas daarna roept Streamlit Apps Script aan met `action="manual_snapshot"`.
7. Na succes toont de app `Snapshot gemaakt` en laadt data opnieuw.

De actie is alleen beschikbaar in echte `Live Google Sheets` mode en alleen als de Apps Script configuratie aanwezig is. In `Demo / Mockdata` en `Fallback actief` wordt geen Apps Script call gedaan en wordt nooit naar `Historie` geschreven.

Meerdere handmatige snapshots per dag zijn toegestaan, maar alleen na deze bevestiging. De dagelijkse snapshot blijft apart in Apps Script via de 22:00 trigger. Streamlit roept `dailyPortfolioSnapshot()` niet aan. E-mailnotificaties blijven alleen bij de dagelijkse Apps Script trigger.

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
APPS_SCRIPT_REFRESH_URL=https://script.google.com/macros/s/.../exec
APPS_SCRIPT_REFRESH_SECRET=...
```

`APPS_SCRIPT_REFRESH_URL` en `APPS_SCRIPT_REFRESH_SECRET` zijn alleen nodig voor `Portfolio bijwerken` en `Snapshot maken`. De secret wordt via de JSON body naar het Web App endpoint gestuurd en mag niet hardcoded, gelogd of volledig in de UI getoond worden.

De Google Sheet moet met editorrechten gedeeld worden met het `client_email` adres uit het service-account JSON-bestand.

Scope:

```text
https://www.googleapis.com/auth/spreadsheets
```

Deze scope is nodig voor write-back naar `Transacties` en `Saldi`.

Secrets mogen nooit worden gecommit:

- `.env`
- `credentials/`
- service-account keys
- Apps Script refresh secret
- token files

## Debug en logging

De normale UI toont alleen de actieve databron:

- `Live Google Sheets`
- `Demo / Mockdata`
- `Fallback actief`

Veilige diagnostiek wordt intern gelogd zonder secrets of volledige Spreadsheet IDs.

Een tijdelijke debug-expander mag lokaal worden aangezet via:

```env
PORTFOLIO_DEBUG_GOOGLE=1
```

Deze expander mag geen credentials-inhoud of volledige Spreadsheet IDs tonen.

## Navigatiestructuur

De app bevat een compacte button-based icon-navigatie met vier hoofdsecties. De actieve sectie wordt in `session_state` bewaard zodat reruns na opslaan, verwijderen, filteren of saldo aanpassen niet terugvallen naar Dashboard.

1. Dashboard
2. Portfolio
3. Transactie
4. Saldi

## Beheer

Alle beheeracties staan in een compacte expander `Beheer`.

Beheer bevat:

- Datamodus `Live Google Sheets` / `Demo / Mockdata`
- `Data opnieuw laden`
- `Portfolio bijwerken`
- `Snapshot maken`
- het bevestigingspaneel voor `Snapshot definitief maken`

Buiten `Beheer` staan geen losse beheerknoppen. De header toont alleen titel, subtitel en statusbadge; daaronder staat de navigatie.

## Dashboard

Dashboard is een clean cockpit-overzicht.

Het dashboard bevat:

- een primaire card voor totaal vermogen
- compacte KPI-cards
- compacte koersperformancecards voor BTC en TSWE
- target progress cards

Het dashboard bevat geen grote grafieken, detailtabellen, recente activiteit of correctiefunctionaliteit. Analysevisuals staan op Portfolio.

KPI's:

- Totaal vermogen: waarde, geen performance badges
- Totaal belegd vermogen: waarde, winst/verlies, 24u, 7d, 30d, YTD
- Crypto: waarde, winst/verlies, 24u, 7d, 30d, YTD
- Aandelen: waarde, winst/verlies, 24u, 7d, 30d, YTD
- Dividend totaal: waarde, geen performance badges

Koerscards:

- Bitcoin koers: huidige koers uit `Portfolio` ticker `BTC`, kolom `Koers`
- TSWE koers: huidige koers uit `Portfolio` ticker `TSWE`, kolom `Koers`
- BTC performance: uit `Historie`, kolom `BTC Koers`
- TSWE performance: uit `Historie`, kolom `TSWE Koers`
- perioden: 24u, 7d, 30d, YTD
- geen externe koers API
- geen nieuwe Google Sheets tabs
- demo mode toont fictieve koerswaarden

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

1. Holdings-cards met compacte filter
2. Optionele tabelweergave in een expander
3. Detailvisuals

Holdings weergave:

- Ticker
- Aantal
- Inleg
- Waarde
- Winst
- ROI

UX-regels:

- Categorie blijft intern beschikbaar voor filtering en visuals, maar staat niet in de standaard holdings-tabel.
- Bedragen gebruiken `€` in de UI.
- Aantallen worden compact geformatteerd: BTC maximaal 6 decimalen, hele aandelen zonder overbodige decimalen.
- Winst/verlies toont plus/min waar logisch.
- ROI toont 1 decimaal.
- Holdings worden primair als cards/list-items getoond en voorkomen brede mobiele tabellen.
- De tabel is secundair en staat in `Tabelweergave`.

Categorieen:

- Crypto
- Aandelen

Onbekende niet-crypto tickers vallen voor nu onder Aandelen.

## Transactie-tab

De Transactie-tab heeft gecontroleerde write-back en veilige correcties.

Write-back:

- alleen in `Live Google Sheets`
- alleen append-only naar tabblad `Transacties`
- bestaande transacties worden niet gewijzigd
- nooit schrijven naar `Portfolio`, `Historie` of `Instellingen`

Flow:

1. Gebruiker vult formulier in.
2. App toont preview van exact de rij die naar Google Sheets gaat.
3. Gebruiker bevestigt expliciet.
4. App appendt pas daarna een rij naar `Transacties`.
5. App voorkomt dubbele submit van dezelfde transactie.
6. Na succes reset de app logische velden zoals `Aantal`, `Totaal` en bevestiging.
7. Daarna probeert de app automatisch `Portfolio bijwerken` en laadt data opnieuw.

Defaults na succesvolle transactie:

- Type = Buy
- Valuta = EUR
- Datum = vandaag
- Ticker mag blijven staan

Status na succesvolle write-back:

1. Opgeslagen in Google Sheets
2. Portfolio bijgewerkt
3. Data opnieuw geladen

Als Apps Script refresh faalt, blijft de transactie in Google Sheets staan. De app toont dat opslaan gelukt is maar Portfolio bijwerken mislukt is, en de gewone knop `Portfolio bijwerken` blijft beschikbaar voor een retry.

### Recente transacties

De Transactie-tab toont een compacte sectie `Recente transacties`.

Regels:

- toon minimaal de laatste 10 transacties totaal
- kolommen: Datum, Ticker, Type, Aantal, Totaal, Valuta
- gebruik live data wanneer beschikbaar
- in `Demo / Mockdata` en `Fallback actief` wordt alleen mock preview of een melding getoond
- in `Demo / Mockdata` wordt alleen mockdata getoond en nooit geschreven

### Veilige transactieverwijdering

Fase 5B bevat veilige correcties voor het tabblad `Transacties`.

Flow:

1. Gebruiker klikt op de kleine verwijderactie bij een recente transactie of op `Correctie verwijderen`.
2. App toont pas daarna het verwijderpaneel.
3. Gebruiker kiest een ticker.
4. App toont maximaal de laatste 3 transacties voor die ticker.
5. Preview toont Sheet-rijnummer, datum, ticker, type, aantal, totaal en valuta.
6. Gebruiker kiest exact een transactie.
7. Gebruiker bevestigt expliciet: `Ik begrijp dat deze transactie uit Google Sheets wordt verwijderd.`
8. App verwijdert maximaal een rij uit `Transacties`.
9. Daarna probeert de app automatisch `Portfolio bijwerken` en laadt data opnieuw.

Regels:

- verwijderen is alleen beschikbaar in `Live Google Sheets`
- niet beschikbaar in `Demo / Mockdata` of `Fallback actief`
- nooit meer dan een rij tegelijk
- geen bulk delete
- geen delete zonder preview en expliciete bevestiging
- alle delete-flow widgets hebben unieke, stabiele keys
- UI roept geen `worksheet.delete_rows` direct aan; delete loopt centraal via `src/sheets_client.py`
- als het Sheet-rijnummer niet veilig bepaald kan worden, wordt niet verwijderd
- header row wordt nooit verwijderd
- delete raakt geen `Portfolio`, `Historie`, `Saldi`, `Instellingen` of andere tabs
- na delete wordt geen `Historie` snapshot gemaakt en geen e-mail verstuurd

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

De Saldi-tab heeft gecontroleerde write-back.

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
9. App voorkomt dubbele submit.
10. Daarna probeert de app automatisch `Portfolio bijwerken` en laadt data opnieuw.

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

Verwijderd uit tabs:

- `Transacties`, maximaal een bestaande rij tegelijk via veilige correctieflow

Indirect bijgewerkt door Apps Script:

- `Portfolio` via `refreshPortfolioOnly()` en `manualPortfolioSnapshot()`
- `Historie` via `manualPortfolioSnapshot()` en de bestaande dagelijkse Apps Script trigger

Niet rechtstreeks geschreven door Streamlit:

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

Koerscards lezen:

- BTC koers uit ticker `BTC`, kolom `Koers (EUR)`
- TSWE koers uit ticker `TSWE`, kolom `Koers (EUR)`

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
- BTC Koers
- TSWE Koers

Oudere rijen mogen `BTC Koers` en `TSWE Koers` missen of leeg laten. De parser vult deze niet kunstmatig met 0 voor performance, maar slaat ongeldige koerspunten over.

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

- `0,12345678` -> `0.12345678`
- `2` -> `2`
- `426` -> `426`
- `34,81` -> `34.81`
- `EUR 12.345,67` -> `12345.67`
- `40,95%` -> `40.95`
- `8-5-2026`
- `8-5-2026 22:10:34`
- `31-01-2026`

Regels:

- komma is decimaalteken
- punten worden alleen als duizendtalscheiding verwijderd
- datums worden day-first geparsed
- fout geformatteerde cellen mogen de app niet crashen

## Buiten Scope

Niet bouwen:

- rechtstreeks schrijven naar `Portfolio` vanuit Python
- rechtstreeks schrijven naar `Historie` vanuit Python
- schrijven naar `Instellingen`
- bestaande transacties updaten
- bulk delete van transacties
- transacties verwijderen zonder preview en bevestiging
- saldi-rijen toevoegen of verwijderen
- Apps Script vervangen
- Apps Script `dailyPortfolioSnapshot()` vanuit Streamlit
- e-mail versturen vanuit Streamlit
- `Data opnieuw laden` die Apps Script triggert
- refresh die `Historie` schrijft
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
    |-- apps_script_client.py
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
- positieve performance is groen
- negatieve performance is rood
- neutrale of ontbrekende performance is gedempt/grijs

Dashboard blijft cockpit. Portfolio bevat details en analyse. Transactie en Saldi gebruiken preview + bevestiging voordat write-back plaatsvindt.
