import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

# 1. Carica variabili da .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")

# 2. Carica il file offerte
with open("offerte_groupon_jsonld.json", "r") as f:
    offerte = json.load(f)

# 3. Trasforma ogni offerta in documento semantico
def offerta_to_doc(offer):
    return Document(
        page_content=(
            f"{offer['name']} - {offer['description']} | "
            f"{offer['category']}, {offer['city']} - €{offer['price']} "
            f"({offer['validFrom']} → {offer['validThrough']}) da {offer['seller']['name']}"
        )
    )

docs = [offerta_to_doc(o) for o in offerte]

# 4. Embedding e indicizzazione
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db = FAISS.from_documents(docs, embedding)

# 5. Motore RAG disponibile per altri script (es. app.py)
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=MODEL),
    retriever=db.as_retriever()
)
