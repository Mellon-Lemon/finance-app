# Finance Companion App - Specificatie

## Doel

De applicatie wordt een mobile-friendly Streamlit webapp bovenop een bestaande Google Sheets + Google Apps Script finance engine.

De bestaande Google Sheet en Apps Script blijven verantwoordelijk voor:
- portfolio-berekeningen
- ROI-berekeningen
- historische snapshots
- Google Finance koersdata
- dividendlogica
- target tracking

De Streamlit app wordt verantwoordelijk voor:
- dashboard weergave
- mobiele bediening
- snelle transacties invoeren
- saldi aanpassen
- historische visualisatie

---

# Architectuur

## Huidige architectuur

Google Sheets functioneert als database.

Google Apps Script functioneert als backend engine.

De Streamlit app functioneert als frontend/mobile interface.

---

# Tabbladen

## Portfolio

Wordt gebruikt voor dashboardweergave.

Kolommen:

- Categorie
- Ticker
- Aantal
- Inleg
- Koers (€)
- Waarde (€)
- Winst (€)
- ROI %

Voorbeeld data:
- BTC
- GOOGL
- AMZN
- MSFT
- TSWE

---

## Saldi

Wordt gebruikt voor cash-overzicht.

Kolommen:
- Account
- Huidig Saldo

Accounts:
- Spaar
- Vakanties
- Vrije ruimte

---

## Instellingen

Wordt gebruikt als ticker-category mapping.

Kolommen:
- Ticker
- categorie

---

## Transacties

Wordt gebruikt als logboek van alle transacties.

Kolommen:
- Datum
- Ticker
- Type
- Aantal
- Prijs per stuk
- Kosten
- Totaal
- Valuta

Ondersteunde types:
- Initial
- Buy
- Sell
- Dividend
- Profit

---

## Historie

Wordt gebruikt voor historische grafieken en delta-analyse.

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

---

# MVP Scope

## Dashboard

De app moet tonen:
- totaal vermogen
- belegd vermogen
- cash totaal
- crypto waarde
- aandelen waarde
- winst totaal
- BTC positie
- target progressie
- equity curve

De app moet mobile-friendly zijn.

---

## Portfolio Tabel

Toon huidige holdings uit tabblad Portfolio.

Kolommen:
- ticker
- aantal
- waarde
- winst
- ROI

---

## Historische Grafiek

Gebruik data uit Historie.

Toon:
- totaal vermogen
- belegd vermogen
- crypto waarde
- aandelen waarde

Gebruik een line chart.

---

## Nieuwe Transactie Toevoegen

De app moet nieuwe transacties kunnen toevoegen aan tabblad Transacties.

Formulier velden:
- datum
- ticker
- type
- aantal
- prijs per stuk
- kosten
- totaal
- valuta

Voor verzending:
- validatie uitvoeren
- preview tonen
- bevestiging vragen

---

## Saldi Aanpassen

De app moet bestaande saldo’s kunnen aanpassen.

Functionaliteit:
- huidige waarde tonen
- nieuwe waarde invoeren
- verschil tonen
- bevestiging vragen

---

# Buiten Scope MVP

De volgende onderdelen mogen NIET gebouwd worden in MVP versie 1:

- Apps Script engine vervangen
- Google Finance vervangen
- eigen ROI engine bouwen
- Historie berekenen
- automatische snapshots maken
- realtime koersdata ophalen
- gebruikersaccounts
- multi-user support
- cloud deployment
- React frontend
- Next.js frontend
- database migratie

---

# Technische Richtlijnen

## Framework

Gebruik:
- Python
- Streamlit

Niet gebruiken:
- React
- Next.js

---

## Google Integratie

Gebruik:
- Google Sheets API v4
- service account credentials

Secrets:
- nooit committen naar GitHub
- opslaan via .env of credentials file

---

# Aanbevolen Mappenstructuur

```text
finance-app/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   └── spec.md
└── src/
    ├── config.py
    ├── sheets_client.py
    ├── dashboard.py
    ├── transactions.py
    └── saldi.py
```

---

# Implementatie Fases

## Fase 1
Specificatie en architectuur.

## Fase 2
Mock dashboard zonder Google API.

## Fase 3
Read-only Google Sheets integratie.

## Fase 4
Schrijven naar Transacties.

## Fase 5
Saldi aanpassen.

## Fase 6
UX polish en mobiele optimalisatie.

---

# UX Richtlijnen

Design:
- minimalistisch
- fintech stijl
- mobile-first
- snelle invoer
- grote touch targets

Belangrijk:
- snelle transacties onderweg
- snel cash aanpassen
- overzichtelijke portfolio cards
