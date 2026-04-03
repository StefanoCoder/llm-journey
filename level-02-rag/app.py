import os
from pathlib import Path
import streamlit as st
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = Path(__file__).parent / "docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

@st.cache_resource(show_spinner="Caricamento documenti in memoria...")
def init_rag():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client_chroma = chromadb.Client()
    collection = client_chroma.get_or_create_collection("documents")

    docs = list(DOCS_DIR.glob("*.txt")) + list(DOCS_DIR.glob("*.pdf"))
    for doc_path in docs:
        if doc_path.suffix == ".pdf":
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() for p in PdfReader(str(doc_path)).pages if p.extract_text())
        else:
            text = doc_path.read_text(encoding="utf-8")

        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i:i + CHUNK_SIZE]))
            i += CHUNK_SIZE - CHUNK_OVERLAP

        embeddings = model.encode(chunks).tolist()
        ids = [f"{doc_path.stem}_{i}" for i in range(len(chunks))]
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"source": doc_path.name}] * len(chunks),
        )

    return model, collection

def ask(question: str, model, collection) -> dict:
    query_embedding = model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    context = "\n\n".join(f"[{src}]\n{chunk}" for src, chunk in zip(sources, chunks))

    prompt = f"""Usa SOLO le informazioni fornite nel contesto per rispondere alla domanda.
Se la risposta non è nel contesto, rispondi: "Non ho questa informazione nei documenti."

CONTESTO:
{context}

DOMANDA: {question}"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"answer": response.content[0].text, "sources": list(set(sources)), "chunks": chunks}


# --- UI ---
st.set_page_config(page_title="RAG Assistant", page_icon="📚")
st.title("📚 RAG Assistant")
st.caption("Fai domande sui tuoi documenti")

model, collection = init_rag()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            st.caption(f"Fonti: {', '.join(msg['sources'])}")

if question := st.chat_input("Fai una domanda sui documenti..."):
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Cerco nei documenti..."):
            result = ask(question, model, collection)
        st.write(result["answer"])
        st.caption(f"Fonti: {', '.join(result['sources'])}")
        with st.expander("Chunk recuperati"):
            for chunk in result["chunks"]:
                st.text(chunk[:300])

    st.session_state.history.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
