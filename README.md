# Finance Companion

Fase 2 van de Streamlit finance app: een mobile-friendly dashboard met alleen mockdata.

## Scope fase 2

- Geen Google Sheets API
- Geen echte data
- Geen write-back functionaliteit
- Wel dashboard cards, portfolio tabel, historische grafiek en mock formulieren

## Starten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Structuur

```text
finance-app/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- docs/
|   `-- spec.md
`-- src/
    |-- __init__.py
    |-- config.py
    |-- dashboard.py
    |-- formatting.py
    |-- mock_data.py
    |-- portfolio.py
    |-- saldi.py
    |-- styles.py
    `-- transactions.py
```

## Volgende fases

Fase 3 kan de mockdata vervangen door read-only Google Sheets integratie. Schrijven naar transacties en saldi blijft pas voor latere fases.
