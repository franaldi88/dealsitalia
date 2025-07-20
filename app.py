from flask import Flask, request, render_template
import json
from datetime import datetime
import os

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Carica dati JSON
with open("offerte_groupon_jsonld.json", "r") as f:
    raw_data = json.load(f)

# Funzione di filtro classico
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

# Homepage con filtri classici
@app.route("/", methods=["GET"])
def index():
    city = request.args.get("city", "")
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    sd = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    ed = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    results = [d for d in raw_data if is_valid_offer(d, city, category, sd, ed)]
    return render_template("index.html", results=results)

# Route /ask per linguaggio naturale
@app.route("/ask", methods=["GET"])
def ask():
    query = request.args.get("q", "")
    if not query:
        return "Fornisci una domanda con ?q=...", 400

    # Prepara documenti da JSON
    def json_to_doc(o):
        return Document(
            page_content=f"""{o["name"]} - {o["description"]} | {o["category"]}, {o["city"]} - €{o["price"]} ({o["validFrom"]} → {o["validThrough"]}) da {o["seller"]["name"]}""",
            metadata=o
        )

    docs = [json_to_doc(o) for o in raw_data]
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    retriever = db.as_retriever()
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    risposta = qa.run(query)
    return risposta

if __name__ == "__main__":
    app.run(debug=True)
