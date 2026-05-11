# Portfolio

Mobile-friendly Streamlit portfolio dashboard bovenop een bestaande Google Sheets + Google Apps Script finance engine.

## Projectstatus

Fase 5B is actief:

- Google Sheets live data werkt.
- Mockdata fallback blijft beschikbaar.
- Write-back is beschikbaar voor `Transacties` en `Saldi`.
- Write-back werkt alleen in `Live Google Sheets` mode.
- Handmatig data opnieuw laden leest Google Sheets opnieuw in.
- Optioneel kan Streamlit `refreshPortfolioOnly()` aanroepen via een Apps Script Web App endpoint.
- Streamlit kan handmatig `manualPortfolioSnapshot()` aanroepen via hetzelfde Apps Script endpoint, alleen na expliciete bevestiging.
- Dashboard toont compacte BTC/TSWE koerscards met 24u, 7d, 30d en YTD performance uit `Historie`.
- Transacties kunnen achter elkaar worden toegevoegd.
- Recente transacties zijn zichtbaar in de Transactie-tab.
- De laatste 3 transacties per ticker kunnen veilig individueel worden verwijderd in Live mode.
- Navigatie blijft op de actieve sectie na interacties.
- Portfolio heeft een compacte, mobielvriendelijke holdingsweergave.
- Demo / Mockdata mode is handmatig beschikbaar om de app veilig te tonen zonder privédata.
- De UI gebruikt een mobile-first app-shell met compacte header, `Beheer`-sectie en icon-navigatie.

Niet gebouwd:

- schrijven naar `Portfolio`
- direct schrijven naar `Historie` vanuit Python
- schrijven naar `Instellingen`
- bestaande transacties wijzigen
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

Optioneel voor `Portfolio bijwerken` en `Snapshot maken` via Apps Script:

```env
APPS_SCRIPT_REFRESH_URL=https://script.google.com/macros/s/.../exec
APPS_SCRIPT_REFRESH_SECRET=your-refresh-secret
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

De app heeft een handmatige `Datamodus` in de compacte actiebalk boven de navigatie:

- `Live Google Sheets`: gebruikt echte Google Sheets data wanneer `.env`, credentials en Sheet geldig zijn.
- `Demo / Mockdata`: gebruikt altijd lokale mockdata en probeert geen Google Sheets of Apps Script aan te roepen.
- `Fallback actief`: Google configuratie is aanwezig, maar live data laden faalt veilig.

Write-back, delete, `Portfolio bijwerken` en `Snapshot maken` zijn alleen actief bij echte `Live Google Sheets` data.

In `Demo / Mockdata` en `Fallback actief` blijven previews werken, maar schrijft of verwijdert de app nooit iets in Google Sheets en roept de app geen Apps Script acties aan. Demo mode is bedoeld voor demonstraties en screenshots zonder echte financiële data en gebruikt fictieve holdings, saldi, historie, dividend, transacties en koerswaarden.

## UX Structuur

De app is ingedeeld als mobile-first finance app:

- Dashboard: rustige cockpit met totaal vermogen, kern-KPI's, BTC/TSWE performancecards en targets.
- Portfolio: holdings als cards, compacte filters, optionele tabel en analysevisuals.
- Transactie: snelle invoerflow, recente transacties en verborgen correctieflow.
- Saldi: compact cashbeheer en saldo wijzigen.

De app-shell gebruikt een compacte header, statusbadge, `Beheer`-expander en icon-navigatie. Grafieken en detailanalyse staan op Portfolio, niet op Dashboard. De actieve sectie blijft behouden na interacties en reruns.

`Beheer` bevat alle beheeracties: datamodus, `Data opnieuw laden`, `Portfolio bijwerken` en `Snapshot maken`. Positieve performance is groen, negatieve performance is rood en ontbrekende/neutrale performance is grijs.

## Opnieuw Laden, Bijwerken En Snapshot

App-open is read-only: bij het openen leest Streamlit alleen data. De app triggert niet automatisch Apps Script en werkt Portfolio niet vanzelf bij. Datamodus en beheeracties staan samen in de compacte sectie `Beheer`.

Gebruik `Data opnieuw laden` om de Streamlit cache te legen en de gegevens opnieuw uit Google Sheets te lezen.

Deze knop:

- leest alleen opnieuw
- schrijft niets naar `Historie`
- triggert geen Apps Script
- verstuurt geen e-mail
- haalt geen live koersdata buiten de bestaande Sheet op
- werkt veilig in `Demo / Mockdata` en `Fallback actief`

Gebruik `Portfolio bijwerken` om het Apps Script Web App endpoint aan te roepen. Deze actie:

- stuurt `action="refresh"` naar het Apps Script endpoint
- roept alleen `refreshPortfolioOnly()` aan
- werkt het `Portfolio` tabblad bij via Apps Script
- schrijft niet naar `Historie`
- roept `dailyPortfolioSnapshot()` niet aan
- verstuurt geen e-mail
- leest daarna de Google Sheets data opnieuw
- werkt alleen in `Live Google Sheets` mode met `APPS_SCRIPT_REFRESH_URL` en `APPS_SCRIPT_REFRESH_SECRET`
- is uitgeschakeld in `Demo / Mockdata`

Gebruik `Snapshot maken` voor een handmatige Historie-snapshot zonder e-mail. Deze actie:

- is beschikbaar in de expander `Beheer`
- vereist eerst de knop `Snapshot maken`
- vereist daarna de checkbox `Ik bevestig dat ik handmatig een Historie-snapshot wil maken.`
- draait pas na `Snapshot definitief maken`
- stuurt `action="manual_snapshot"` naar hetzelfde Apps Script endpoint
- roept alleen `manualPortfolioSnapshot()` aan
- werkt het `Portfolio` tabblad bij via Apps Script
- schrijft een regel naar `Historie` via Apps Script
- roept `dailyPortfolioSnapshot()` niet aan
- verstuurt geen e-mail
- leest daarna de Google Sheets data opnieuw
- is uitgeschakeld in `Demo / Mockdata` en `Fallback actief`

Als de Apps Script endpoint-configuratie ontbreekt, blijft de app werken en blijft `Data opnieuw laden` beschikbaar. Na een succesvolle transactie- of saldi-write probeert de app `Portfolio bijwerken` automatisch uit te voeren als dit geconfigureerd is.

De dagelijkse snapshot blijft buiten Streamlit: Apps Script voert `dailyPortfolioSnapshot()` apart uit via de 22:00 trigger. E-mailnotificaties blijven alleen bij die dagelijkse trigger.

Dashboard koerscards gebruiken geen externe koers API. De huidige BTC- en TSWE-koers komt uit de bestaande `Portfolio` data, op ticker uit de kolom `Koers`. De koersperformance komt uit `Historie` met de snapshotkolommen `BTC Koers` en `TSWE Koers`.

## Google Sheets

Gelezen tabs:

- `Portfolio`
- `Saldi`
- `Historie`
- `Transacties`, optioneel voor `Dividend totaal`

`Historie` mag oudere rijen zonder `BTC Koers` en `TSWE Koers` bevatten. Die lege punten worden overgeslagen voor koersperformance.

Geschreven tabs:

- `Transacties`: append-only nieuwe transactierijen
- `Saldi`: update-only bestaande `Huidig Saldo` cel van een bestaand account

Indirect bijgewerkt door Apps Script:

- `Portfolio`: via `refreshPortfolioOnly()` en `manualPortfolioSnapshot()`
- `Historie`: alleen via `manualPortfolioSnapshot()` of de bestaande dagelijkse Apps Script trigger

Veilige correctie:

- `Transacties`: delete van maximaal een bestaande rij tegelijk, alleen na preview en expliciete bevestiging

De app gebruikt de scope:

```text
https://www.googleapis.com/auth/spreadsheets
```

Nederlandse getalnotatie wordt centraal geparsed, bijvoorbeeld `0,12345678`, `EUR 12.345,67` en `40,95%`.

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

Na een succesvolle transactie reset de app logische invoervelden zoals `Aantal` en `Totaal`, zodat meerdere transacties achter elkaar kunnen worden toegevoegd zonder dubbele submit van dezelfde preview. Datum, type en valuta vallen terug op handige defaults.

De Transactie-tab toont ook `Recente transacties` met de laatste 10 transacties. In `Demo / Mockdata` of `Fallback actief` wordt nooit geschreven of verwijderd.

Veilige correcties zijn beschikbaar in `Live Google Sheets` mode:

- klik eerst op de kleine verwijderactie bij een recente transactie of `Correctie verwijderen`
- kies een ticker
- bekijk maximaal de laatste 3 transacties voor die ticker
- selecteer exact een rij
- bevestig expliciet dat de rij uit Google Sheets wordt verwijderd
- verwijder maximaal een transactie tegelijk

Delete raakt alleen het tabblad `Transacties`. Daarna probeert de app `Portfolio bijwerken` en laadt data opnieuw. Er wordt geen `Historie` snapshot gemaakt en er wordt geen e-mail verstuurd.

De delete-flow gebruikt expliciete widget keys, zodat het verwijderpaneel zonder `StreamlitDuplicateElementId` opent.

## Portfolio

De Portfolio-weergave gebruikt standaard compacte, scanbare holdings-cards. De tabelweergave blijft beschikbaar in de expander `Tabelweergave`.

- `Categorie` staat niet meer in de holdings-tabel
- `Ingelegd vermogen` heet `Inleg`
- bedragen tonen `€`
- aantallen, winst/verlies en ROI worden compact geformatteerd
- holdings-cards voorkomen brede mobiele tabellen als primaire ervaring

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
- Apps Script refresh secret
- token files

De service-account key en Apps Script secret blijven lokaal geheim. De app toont geen credentials-inhoud, geen volledige Spreadsheet IDs en geen refresh secret.

## Debug

Veilige Google Sheets diagnostiek wordt naar de terminal gelogd zonder secrets.

Een tijdelijke debug-expander in de UI kan lokaal worden aangezet met:

```env
PORTFOLIO_DEBUG_GOOGLE=1
```

Laat deze waarde uit of zet hem op `0` voor normaal gebruik.
