from flask import Flask, request, render_template
import json
from datetime import datetime, date
from rag_offerte import qa
from dateparser.search import search_dates

app = Flask(__name__)

# Carica il JSON delle offerte
with open("offerte_groupon_jsonld.json", "r") as f:
    data = json.load(f)

# Funzione di parsing date da testo

def estrai_data_da_query(query):
    try:
        results = search_dates(query, languages=["it"])
        for _, parsed in results or []:
            if parsed:
                return parsed.date()
    except Exception:
        return None
    return None

# Funzione di filtraggio

def is_valid_offer_for_date(offer, target_date):
    if "validFrom" not in offer or "validThrough" not in offer:
        return False
    valid_from = datetime.strptime(offer["validFrom"], "%Y-%m-%d").date()
    valid_through = datetime.strptime(offer["validThrough"], "%Y-%m-%d").date()
    return valid_from <= target_date <= valid_through

# Route principale
@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("query", "")
    city = request.args.get("city", "")
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    sd = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    ed = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

    results = []
    answer = None

    if query:
        query_date = estrai_data_da_query(query)
        print(f"Query: {query} → Data rilevata: {query_date}")
        filtered_docs = data
        if query_date:
            filtered_docs = [d for d in data if is_valid_offer_for_date(d, query_date)]
        answer = qa.invoke({"query": query, "input_documents": filtered_docs})["result"]
    else:
        results = [d for d in data if
                   (not city or d.get("city", "").lower() == city.lower()) and
                   (not category or d.get("category", "").lower() == category.lower()) and
                   (not sd or datetime.strptime(d["validThrough"], "%Y-%m-%d") >= sd) and
                   (not ed or datetime.strptime(d["validFrom"], "%Y-%m-%d") <= ed)]

    return render_template("index.html", results=results, answer=answer, query=query)

if __name__ == "__main__":
    app.run(debug=True)
