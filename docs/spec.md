# Portfolio App - Specificatie

## Doel

Portfolio is een mobile-friendly Streamlit dashboard bovenop een bestaande Google Sheets + Google Apps Script finance engine.

De bestaande Google Sheet en Apps Script blijven verantwoordelijk voor:
- portfolio-berekeningen
- ROI-berekeningen
- historische snapshots
- Google Finance koersdata
- dividendlogica
- target tracking

De Streamlit app is verantwoordelijk voor:
- dashboardweergave
- mobiele bediening
- portfolio-analyse
- snelle transactie-preview
- saldi-preview

Fase 2 gebruikt alleen mockdata in Python. Fase 3 voegt read-only Google Sheets integratie toe. Mockdata blijft beschikbaar als fallback.

---

## Product

App title:
- Portfolio

Huidige status:
- Fase 2 mock MVP
- Streamlit frontend
- Geen Google Sheets API in de app
- Geen echte data
- Geen write-back

Volgende stap:
- Fase 3: read-only Google Sheets integratie

---

## Architectuur

### Huidige architectuur

Google Sheets functioneert als database.

Google Apps Script functioneert als backend/engine.

De Streamlit app functioneert als frontend/mobile interface.

Mockdata in Python functioneert als lokale fallback en ontwikkelbasis.

### Fase 3 architectuur

Fase 3 leest data read-only uit Google Sheets.

Fase 3 schrijft niets terug naar Google Sheets.

Fase 3 vervangt de Apps Script engine niet.

Fase 3 vervangt Google Finance niet.

---

## Tabstructuur

De Streamlit app bevat vier hoofdtabbladen:

1. Dashboard
2. Portfolio
3. Transactie
4. Saldi

---

## Dashboard

Dashboard is een clean cockpit-overzicht.

Het dashboard bevat:
- KPI overzicht
- target progress cards
- equity curve

De equity curve gebruikt Historie als bron en blijft read-only.

### KPI's

#### Totaal vermogen

Toont:
- waarde

Niet tonen:
- winst/verlies badge
- 24u
- 30d
- YTD

Definitie:
- totaal vermogen = cash + actuele beleggingswaarde

#### Totaal belegd vermogen

Toont:
- waarde
- winst/verlies
- 24-uurs wijziging
- afgelopen 30 dagen
- YTD

#### Crypto

Toont:
- waarde
- winst/verlies
- 24-uurs wijziging
- afgelopen 30 dagen
- YTD

#### Aandelen

Toont:
- waarde
- winst/verlies
- 24-uurs wijziging
- afgelopen 30 dagen
- YTD

TSWE wordt voor nu als Aandelen behandeld, niet als aparte ETF-hoofdcategorie.

#### Dividend totaal

Toont:
- waarde

Niet tonen:
- 24u
- 30d
- YTD

### Performance-metrics

Voor Totaal belegd vermogen, Crypto en Aandelen toont de app compacte performance-regels in deze vaste volgorde:

1. Waarde
2. Winst/verlies
3. 24u / 30d / YTD

YTD-definitie:
- startdatum: 31-01-2026
- fase 2 gebruikt mockwaarden
- fase 3 gebruikt de Historie sheet als read-only bron

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

---

## Portfolio-tab

Portfolio is het detail/analyse-tabblad.

Volgorde:

1. Holdings tabel
2. Detailvisuals

### Holdings tabel

De tabel toont minimaal:
- Ticker
- Categorie
- Aantal
- Ingelegd vermogen
- Waarde
- Winst
- ROI

Berekening:
- Ingelegd vermogen = Waarde - Winst

### Detailvisuals

Portfolio mag de volgende visualisaties tonen:
- waarde per categorie
- ingelegd vermogen per categorie
- winst/verlies per categorie
- belegd vermogen vs ingelegd vermogen

Visuals moeten rustig, consistent en mobile-friendly blijven.

### Categorieen

Huidige hoofdcategorieen:
- Crypto
- Aandelen

TSWE valt onder Aandelen.

---

## Transactie-tab

De Transactie-tab is in fase 2 en fase 3 mock/preview-only.

Er wordt niets naar Google Sheets geschreven.

### Type-volgorde

1. Buy
2. Sell
3. Dividend
4. Profit
5. Initial

Buy is de default.

### Velden

Algemene velden:
- Datum
- Ticker
- Type
- Aantal
- Prijs per stuk
- Totaal
- Valuta

Datumformaat:
- dd-mm-yyyy

Er is geen apart transactiekostenveld.

Totaal is inclusief eventuele transactiekosten.

### Buy / Sell / Initial

Voor Buy, Sell en Initial geldt:
- Totaal is het leidende invoerveld.
- Als Aantal en Totaal zijn ingevuld, berekent de app Prijs per stuk automatisch.
- Prijs per stuk wordt duidelijk als berekende waarde getoond.
- De app voorkomt dubbele waarheid tussen Aantal, Prijs per stuk en Totaal.

### Dividend / Profit

Voor Dividend en Profit geldt:
- Datum, Ticker, Type, Totaal en Valuta zijn de belangrijkste velden.
- Aantal is optioneel of minder prominent.
- Prijs per stuk mag berekend worden als Aantal is ingevuld.

### Preview

Voor verzending toont de app een duidelijke preview.

Bevestigen in fase 2 en fase 3 schrijft niets weg.

---

## Saldi-tab

De Saldi-tab is in fase 2 en fase 3 mock/preview-only.

Er wordt niets naar Google Sheets geschreven.

De tab toont:
- totaal cashsaldo
- splitsing Spaar / Vakanties / Vrije ruimte
- formulier om saldo te wijzigen
- huidige waarde
- nieuwe waarde
- verschil
- bevestiging

Het verschil wordt duidelijk getoond:
- positief als + bedrag
- negatief als - bedrag

---

## Google Sheets datacontract

Fase 3 leest read-only data uit deze tabs:

- Portfolio
- Saldi
- Historie

Fase 3 schrijft niet naar Google Sheets.

### Portfolio

Kolommen:
- Categorie
- Ticker
- Aantal
- Inleg
- Koers (€)
- Waarde (€)
- Winst (€)
- ROI %

Voorbeeld tickers:
- BTC
- GOOGL
- AMZN
- MSFT
- TSWE

Belangrijk:
- TSWE wordt in de app als Aandelen behandeld zolang de sheet dit zo mapt.

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

Historie wordt gebruikt voor:
- equity curve
- 30d performance
- YTD performance
- vergelijking belegd vermogen vs ingelegd vermogen

---

## Buiten scope fase 3

Niet bouwen in fase 3:

- schrijven naar Google Sheets
- transacties toevoegen aan Sheet
- saldi updaten in Sheet
- Apps Script engine vervangen
- Google Finance vervangen
- eigen ROI-engine herbouwen
- Historie berekenen
- automatische snapshots maken
- realtime koersdata ophalen buiten de bestaande sheet
- gebruikersaccounts
- multi-user support
- cloud deployment
- React frontend
- Next.js frontend
- database migratie

---

## Technische richtlijnen

Gebruik:
- Python
- Streamlit
- pandas
- plotly
- mockdata fallback
- service account voor latere Google Sheets integratie

Niet gebruiken:
- React
- Next.js
- write-back naar Google Sheets in fase 3

Secrets:
- nooit committen naar GitHub
- opslaan via .env, Streamlit secrets of credentials file
- .env en credentials files moeten in .gitignore staan

Google integratie fase 3:
- Google Sheets API v4
- service account credentials
- read-only scopes waar mogelijk
- duidelijke scheiding tussen data-loading en UI-rendering

---

## Aanbevolen projectstructuur

```text
finance-app/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- docs/
|   `-- spec.md
|-- assets/
|   `-- header-placeholder.svg
`-- src/
    |-- __init__.py
    |-- config.py
    |-- dashboard.py
    |-- formatting.py
    |-- mock_data.py
    |-- portfolio.py
    |-- saldi.py
    |-- styles.py
    |-- transactions.py
    `-- ui.py
```

Voor fase 3 kan een read-only data module worden toegevoegd, bijvoorbeeld:

```text
src/
|-- sheets_client.py
`-- data_loader.py
```

Daarbij blijft mockdata als fallback bestaan.

---

## Implementatiefases

### Fase 1

Specificatie en architectuur.

### Fase 2

Mock dashboard zonder Google API.

### Fase 2.5

Cleanup van mock MVP:
- realistischer mockdata
- clean dashboard cockpit
- Portfolio als analysepagina
- transactieformulier preview-only
- saldi preview-only

### Fase 3

Read-only Google Sheets integratie:
- Portfolio lezen
- Saldi lezen
- Historie lezen
- mockdata fallback behouden
- geen write-back

### Fase 4

Schrijven naar Transacties.

### Fase 5

Saldi aanpassen.

### Fase 6

UX polish en mobiele optimalisatie.

---

## UX richtlijnen

Design:
- minimalistisch
- fintech stijl
- mobile-first
- snelle invoer
- grote touch targets
- rustige spacing
- duidelijke card hierarchy

Belangrijk:
- Dashboard blijft cockpit, niet analysepagina.
- Portfolio bevat details en visualisaties.
- Transactie is snel en eenduidig voor mobiele invoer.
- Saldi voelt veilig en duidelijk door preview en bevestiging.
#### Future phase: manual live price refresh
- Eerst Google Sheets lezen.
- Dan transacties/saldi schrijven.
- Daarna live koers-refresh als aparte module.
- Niet automatisch pollen.
- Alleen op gebruikersactie.
- Geen standaard write-back zonder bevestiging.