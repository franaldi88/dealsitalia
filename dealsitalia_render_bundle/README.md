# DealsItalia

Una webapp di esempio per esplorare offerte locali in Italia (in stile Groupon). Costruita con Flask e interfaccia Bootstrap, permette di filtrare per città, categoria e date.

## Come funziona

- Backend: Flask
- Frontend: HTML + Bootstrap
- Dataset: offerte in formato JSON-LD

## Esempio di utilizzo

Cerca "offerte a Bologna questo weekend" oppure "attività outdoor a Milano".

## Avvio locale

```
pip install -r requirements.txt
python app.py
```

## Deploy

Per ambienti come Render, assicurati che il `Procfile` contenga:
```
web: python app.py
```
