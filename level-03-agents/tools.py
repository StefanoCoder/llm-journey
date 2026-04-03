"""
tools.py — Definizione dei tool che l'agente può usare.
"""

import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DOCS_DIR = Path(__file__).parent / "docs"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- Setup RAG ---
_embed_fn = DefaultEmbeddingFunction()
_chroma = chromadb.Client()
_collection = _chroma.get_or_create_collection("docs", embedding_function=_embed_fn)

def _load_docs():
    docs = list(DOCS_DIR.glob("*.txt")) + list(DOCS_DIR.glob("*.pdf"))
    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i:i + 300]))
            i += 250
        ids = [f"{doc_path.stem}_{j}" for j in range(len(chunks))]
        _collection.upsert(ids=ids, documents=chunks, metadatas=[{"source": doc_path.name}] * len(chunks))

_load_docs()

# --- Tool functions ---

def search_docs(query: str) -> str:
    """Cerca nella knowledge base degli standard del team."""
    results = _collection.query(query_texts=[query], n_results=3, include=["documents", "metadatas"])
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return "\n\n".join(f"[{src}]\n{chunk}" for src, chunk in zip(sources, chunks))

def create_file(path: str, content: str) -> str:
    """Crea un file nel progetto in output/."""
    full_path = OUTPUT_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return f"File creato: output/{path}"

def read_file(path: str) -> str:
    """Legge un file esistente in output/."""
    full_path = OUTPUT_DIR / path
    if not full_path.exists():
        return f"File non trovato: {path}"
    return full_path.read_text(encoding="utf-8")

def list_files() -> str:
    """Lista tutti i file generati in output/."""
    files = list(OUTPUT_DIR.rglob("*"))
    files = [f for f in files if f.is_file()]
    if not files:
        return "Nessun file generato ancora."
    return "\n".join(str(f.relative_to(OUTPUT_DIR)) for f in sorted(files))


# --- Tool schema per Anthropic API ---
TOOLS = [
    {
        "name": "search_docs",
        "description": "Cerca negli standard e nelle specifiche del team (React, Tailwind, Prisma, Supabase, budget, ecc.). Usa questo tool PRIMA di scrivere qualsiasi codice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "La query di ricerca"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_file",
        "description": "Crea un file nel progetto. Usa path relativi (es. 'src/components/Button.tsx').",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relativo del file"},
                "content": {"type": "string", "description": "Contenuto del file"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Legge un file già creato nel progetto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relativo del file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "Lista tutti i file generati finora nel progetto.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

TOOL_MAP = {
    "search_docs": search_docs,
    "create_file": create_file,
    "read_file": read_file,
    "list_files": list_files,
}
