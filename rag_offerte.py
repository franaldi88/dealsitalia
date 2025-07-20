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

# 3. Trasforma ogni offerta in documento semantico + metadata
def offerta_to_doc(offer):
    return Document(
        page_content=(
            f"{offer['name']} - {offer['description']} | "
            f"{offer['category']}, {offer['city']} - €{offer['price']} "
            f"({offer['validFrom']} → {offer['validThrough']}) da {offer['seller']['name']}"
        ),
        metadata={
            "city": offer.get("city"),
            "category": offer.get("category"),
            "validFrom": offer.get("validFrom"),
            "validThrough": offer.get("validThrough"),
        }
    )

docs = [offerta_to_doc(o) for o in offerte]

# 4. Embedding e indicizzazione
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db = FAISS.from_documents(docs, embedding)

# 5. Motore RAG disponibile per altri script (es. app.py)
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=MODEL),
    chain_type="stuff",
    retriever=db.as_retriever()
)

# 6. Funzione per creare QA dinamico con documenti filtrati
def create_dynamic_qa(filtered_offers):
    if not filtered_offers:
        return qa
    
    # Per pochi documenti, usa un approccio diretto senza FAISS
    if len(filtered_offers) <= 3:
        from langchain.chains.question_answering import load_qa_chain
        filtered_docs = [offerta_to_doc(o) for o in filtered_offers]
        
        def direct_qa_invoke(params):
            from datetime import datetime
            chain = load_qa_chain(ChatOpenAI(model=MODEL), chain_type="stuff")
            
            # Aggiungi contesto temporale alla domanda
            today = datetime.now().strftime("%Y-%m-%d")
            enhanced_question = f"{params['query']} (Nota: la data di oggi è {today}. Rispondi basandoti solo sulle offerte fornite che sono valide per questa data.)"
            
            result = chain.invoke({"input_documents": filtered_docs, "question": enhanced_question})
            return {"result": result.get("output_text", result)}
        
        class DirectQA:
            def invoke(self, params):
                return direct_qa_invoke(params)
        
        return DirectQA()
    
    # Per molti documenti, usa FAISS
    filtered_docs = [offerta_to_doc(o) for o in filtered_offers]
    temp_db = FAISS.from_documents(filtered_docs, embedding)
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model=MODEL),
        chain_type="stuff", 
        retriever=temp_db.as_retriever()
    )
