from flask import Flask, request, render_template, jsonify
import json
from datetime import datetime
from rag_offerte import qa  # Usa l’istanza qa già pronta dal tuo script

app = Flask(__name__)

# Carica le offerte
with open("offerte_groupon_jsonld.json", "r") as f:
    data = json.load(f)

# Filtraggio per città, categoria e date
def is_valid_offer(offer, city, category, start_date, end_date):
    if city and offer.get("city", "").lower() != city.lower():
        return False
    if category and offer.get("category", "").lower() != category.lower():
        return False
    if "validFrom" not in offer or "validThrough" not in offer:
        return False
    valid_from = datetime.strptime(offer["validFrom"], "%Y-%m-%d")
    valid_through = datetime.strptime(offer["validThrough"], "%Y-%m-%d")
    if start_date and valid_through < start_date:
        return False
    if end_date and valid_from > end_date:
        return False
    return True

@app.route("/", methods=["GET"])
def index():
    city = request.args.get("city", "")
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    sd = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    ed = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    results = [d for d in data if is_valid_offer(d, city, category, sd, ed)]
    return render_template("index.html", results=results)

# 🔍 Linguaggio naturale
@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.form.get("query", "")
    if not user_query:
        return jsonify({"error": "Nessuna query fornita"}), 400
    answer = qa.run(user_query)
    return jsonify({"query": user_query, "answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
