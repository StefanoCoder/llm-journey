"""
ingest.py — Legge i documenti dalla cartella docs/, crea gli embedding e li salva in ChromaDB.
Eseguire una volta sola (o ogni volta che aggiungi nuovi documenti).
"""

import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = Path(__file__).parent / "docs"
CHROMA_DIR = Path(__file__).parent / "chroma_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + size])
        chunks.append(chunk)
        i += size - overlap
    return chunks

def ingest():
    print("Caricamento modello embedding...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection("documents")

    docs = list(DOCS_DIR.glob("*.txt")) + list(DOCS_DIR.glob("*.pdf"))
    if not docs:
        print("Nessun documento trovato in docs/")
        return

    for doc_path in docs:
        print(f"Processing: {doc_path.name}")

        if doc_path.suffix == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(doc_path))
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            text = doc_path.read_text(encoding="utf-8")

        chunks = chunk_text(text)
        embeddings = model.encode(chunks).tolist()

        ids = [f"{doc_path.stem}_{i}" for i in range(len(chunks))]
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"source": doc_path.name}] * len(chunks),
        )
        print(f"  → {len(chunks)} chunk salvati")

    print(f"\nIngest completato. Totale documenti nel DB: {collection.count()}")

if __name__ == "__main__":
    ingest()
