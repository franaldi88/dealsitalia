from flask import Flask, request, render_template
import json
from datetime import datetime

app = Flask(__name__)

with open("offerte_groupon_jsonld.json", "r") as f:
    data = json.load(f)

def is_valid_offer(offer, city, category, start_date, end_date):
    if city and offer.get("city", "").lower() != city.lower():
        return False
    if category and offer.get("category", "").lower() != category.lower():
        return False
    valid_from = datetime.strptime(offer["valid_from"], "%Y-%m-%d")
    valid_through = datetime.strptime(offer["valid_through"], "%Y-%m-%d")
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

if __name__ == "__main__":
    app.run(debug=True)
