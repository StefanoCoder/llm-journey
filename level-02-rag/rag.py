"""
rag.py — Prende una domanda, cerca i chunk rilevanti nel DB, chiede a Claude.
"""

import os
from pathlib import Path
import chromadb
import anthropic
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(__file__).parent / "chroma_db"
TOP_K = 3

model = SentenceTransformer("all-MiniLM-L6-v2")
client_chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client_chroma.get_or_create_collection("documents")
client_anthropic = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def ask(question: str) -> dict:
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
Se la risposta non è nel contesto, dì esplicitamente "Non ho questa informazione nei documenti."

CONTESTO:
{context}

DOMANDA: {question}"""

    response = client_anthropic.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "answer": response.content[0].text,
        "sources": list(set(sources)),
        "chunks": chunks,
    }
