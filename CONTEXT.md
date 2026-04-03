# CONTEXT — LLM Journey
> Documento di contesto per continuare il percorso in nuove sessioni.
> Aggiornato: Aprile 2026

---

## Chi è l'utente
- **GitHub:** StefanoCoder
- **Obiettivo:** Costruire sistemi AI basati su LLM, dall'integrazione API fino al fine-tuning di modelli open-source
- **PRD di riferimento:** `/Users/stefanomigliaccio/Downloads/PRD_LLM_Agenti.docx`
- **Approccio:** Build-first, velocità massima, niente teoria senza codice

---

## Ambiente di lavoro

| Tool | Versione / Info |
|------|----------------|
| Mac | macOS con chip Apple Silicon |
| Python | 3.11.15 (installato via Homebrew) |
| Homebrew | 5.1.3 (path: `/opt/homebrew`) |
| Node.js | v24.14.1 |
| npm | 11.11.0 |
| GitHub CLI | `gh` installato, autenticato come `StefanoCoder` |
| Editor | Da definire (VS Code non confermato) |

### Note importanti sull'ambiente
- `brew` richiede `eval "$(/opt/homebrew/bin/brew shellenv)"` per essere disponibile in sessione
- La `ANTHROPIC_API_KEY` va esportata manualmente ogni volta: `export ANTHROPIC_API_KEY="sk-ant-..."`
- Per evitare il problema della key, ogni progetto ha `.streamlit/secrets.toml` locale (non committato)
- Il `.gitignore` del repo esclude: `venv/`, `chroma_db/`, `.DS_Store`, `**/.streamlit/secrets.toml`

---

## Repository GitHub
- **URL:** https://github.com/StefanoCoder/llm-journey
- **Visibilità:** Pubblica (resa pubblica per Streamlit Cloud)
- **Path locale:** `~/llm-journey/`
- **Branch:** `main`

### Struttura attuale del repo
```
llm-journey/
├── CONTEXT.md                    ← questo file
├── .gitignore
├── level-01-api/
│   ├── app.py                    ← Streamlit chatbot (deployato)
│   ├── chatbot.py                ← CLI chatbot multi-turn
│   └── requirements.txt
├── level-02-rag/
│   ├── app.py                    ← RAG Assistant (deployato)
│   ├── docs/
│   │   ├── standard_sviluppo_team_agenti_ai.txt
│   │   ├── specifiche_tecniche_progetto_alpha.txt
│   │   └── guida_stile_ui_tailwind.txt
│   └── requirements.txt
├── level-03-agents/
│   ├── app.py                    ← Technical Architect Agent (Streamlit)
│   ├── agent.py                  ← ReAct loop con generator
│   ├── tools.py                  ← Tool: search_docs, create_file, read_file, list_files
│   ├── docs/                     ← Copia dei docs del level-02
│   ├── requirements.txt
│   └── output/                   ← Progetto generato dall'agente (non committato)
├── level-04-finetune/            ← Da fare
└── level-05-research/            ← Da fare
```

---

## Livelli completati

### ✅ Livello 1 — API & Prompt Engineering
**Status:** Completato e deployato

**Cosa è stato costruito:**
- `chatbot.py`: chatbot CLI con conversazione multi-turn, system prompt in italiano, gestione history
- `app.py`: interfaccia Streamlit con `st.chat_message`, `st.chat_input`, session state per la history

**Deploy:** Streamlit Cloud — app online e funzionante

**Concetti appresi:**
- Struttura chiamata API Anthropic: `client.messages.create(model, max_tokens, system, messages)`
- Differenza system prompt / user prompt
- Gestione history multi-turn come lista di `{"role": ..., "content": ...}`
- Deploy su Streamlit Cloud con secrets per la API key

---

### ✅ Livello 2 — RAG (Retrieval-Augmented Generation)
**Status:** Completato e deployato

**Cosa è stato costruito:**
- Sistema RAG completo in un singolo `app.py`
- Auto-ingest dei documenti all'avvio tramite `@st.cache_resource`
- Embedding con `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()` (usa onnxruntime, no PyTorch)
- Vector store in-memory con ChromaDB (ephemeral — si ricostruisce ad ogni cold start)
- Chunking: finestre da 500 parole con overlap da 50
- Retrieval: top-3 chunk per similarità coseno
- Generation: Claude riceve il contesto e risponde SOLO sui documenti

**Perché DefaultEmbeddingFunction e non sentence-transformers:**
- `sentence-transformers` porta PyTorch (~2GB) — incompatibile con Streamlit Cloud (timeout build)
- `DefaultEmbeddingFunction` usa `onnxruntime` — leggero, funziona su Streamlit Cloud

**Knowledge base attuale (3 documenti):**
1. `standard_sviluppo_team_agenti_ai.txt` — stack: React, TypeScript, Tailwind, Prisma, Supabase
2. `specifiche_tecniche_progetto_alpha.txt` — Progetto Alpha: Task Manager con categorizzazione AI
3. `guida_stile_ui_tailwind.txt` — classi Tailwind standard: bottoni, input, card, colori

**Deploy:** Streamlit Cloud — funzionante

**Lezione chiave:** Su Streamlit Cloud i secrets vanno aggiunti nel pannello Settings → Secrets in formato TOML. In locale si usa `.streamlit/secrets.toml` (escluso da git).

---

### ✅ Livello 3 — Agenti & Tool Use
**Status:** Funzionante in locale, da perfezionare e deployare

**Cosa è stato costruito:**
- **`tools.py`**: 4 tool disponibili all'agente
  - `search_docs(query)` → cerca nella knowledge base RAG
  - `create_file(path, content)` → scrive file in `output/`
  - `read_file(path)` → legge file esistenti
  - `list_files()` → lista tutti i file generati
- **`agent.py`**: ReAct loop come Python generator
  - Yield di eventi: `("thought", text)`, `("tool_call", {...})`, `("tool_result", {...})`, `("done", None)`
  - Loop: `while True` → chiamata API → processa blocchi → se `end_turn` break, altrimenti aggiunge tool results e richiama
- **`app.py`**: Streamlit che consuma il generator in modo sincrono
  - Mostra ragionamento, tool call e file creati in tempo reale
  - `for etype, data in run_agent(goal, api_key):`

**System prompt dell'agente (ruolo: Technical Architect):**
- Consulta SEMPRE `search_docs` prima di scrivere codice
- Rispetta stack: React + TypeScript + Tailwind + Prisma + Supabase
- Ogni componente React ha commenti sulle Props
- Costruisce file per file, spiega ogni scelta

**Progetto generato in `output/` (33 file):**
```
output/
├── package.json          (React 18, Supabase, Prisma, Lucide, Tailwind, Vite)
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.node.json
├── postcss.config.js
├── index.html
├── .env.example
├── prisma/schema.prisma
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── vite-env.d.ts
    ├── types/
    │   ├── index.ts
    │   └── task.ts
    ├── lib/
    │   ├── supabase.ts
    │   └── ai-categorizer.ts
    ├── services/
    │   ├── taskService.ts
    │   └── aiService.ts
    ├── hooks/
    │   ├── useTasks.ts
    │   └── useAuth.ts
    ├── styles/
    │   ├── globals.css
    │   └── index.css
    └── components/
        ├── Dashboard.tsx
        ├── TaskCard.tsx
        ├── TaskForm.tsx
        ├── auth/LoginForm.tsx
        ├── tasks/TaskForm.tsx
        └── ui/
            ├── Button.tsx
            ├── Card.tsx
            ├── Badge.tsx
            └── Input.tsx
```

**Come avviare il progetto generato:**
```bash
cd ~/llm-journey/level-03-agents/output
npm install && npm run dev
# → http://localhost:5173
```

**Bug risolti durante lo sviluppo:**
1. Threading Streamlit → blocchi → risolto con generator sincrono
2. `KeyError: 'content'` in app.py → `inp.get('content', '')`
3. `TypeError: create_file() missing argument 'content'` → `content: str = ""` default
4. `chroma_db/` committato per errore → rimosso e aggiunto a `.gitignore`
5. `secrets.toml` committato con API key → rimosso con `git rm --cached` + amend

---

## Prossimi step

### Step immediato — Completare Livello 3
- [ ] Avviare il progetto generato (`npm run dev`) e verificare che compili
- [ ] Configurare Supabase: creare progetto su supabase.com, ottenere URL e ANON KEY
- [ ] Aggiornare `.env.example` → `.env` con le credenziali Supabase reali
- [ ] Eseguire migrazione Prisma: `npx prisma migrate dev`
- [ ] Testare il flusso completo: login → crea task → categorizzazione AI
- [ ] Deploy dell'agente su Streamlit Cloud (nuovo app, `level-03-agents/app.py`)
- [ ] Aggiungere tool `run_command` per permettere all'agente di eseguire comandi shell
- [ ] Aggiungere tool `search_web` (via SerpAPI o Tavily) per ricerca esterna

### Livello 4 — Fine-tuning (da iniziare dopo aver completato il Livello 3)
**Obiettivo:** Addestrare un modello open-source (Llama 3 o Mistral) sui propri dati

**Prerequisiti da preparare:**
- Dataset in formato JSONL: `{"instruction": "...", "input": "...", "output": "..."}`
- Minimo 500 esempi, idealmente 2000+
- Account Google Colab Pro (~15$/mese) per GPU A100
- Account Hugging Face (gratuito) per scaricare modelli base e pubblicare il modello fine-tuned

**Stack:**
- `transformers` + `PEFT` (LoRA/QLoRA) di Hugging Face
- `Axolotl` o `Unsloth` per training semplificato
- `Weights & Biases` (W&B) per monitoraggio training
- `Ollama` o `llama.cpp` per inference locale del modello fine-tuned

**Progetto target Livello 4:**
- Modello fine-tuned che replica lo stile di scrittura personale (testi, note, email)
- Oppure modello specializzato sugli standard del team per generare codice conforme

### Livello 5 — Pre-training & Ricerca (futuro)
- Implementare GPT-2 da zero con nanoGPT (repo di Andrej Karpathy)
- Training su dataset Shakespeare come primo esperimento
- Lettura paper: "Attention is All You Need", GPT-3, Llama, Mistral

---

## Comandi utili da ricordare

```bash
# Attivare Homebrew in sessione
eval "$(/opt/homebrew/bin/brew shellenv)"

# Avviare Livello 1
cd ~/llm-journey/level-01-api && source venv/bin/activate && export ANTHROPIC_API_KEY="..." && streamlit run app.py

# Avviare Livello 2
cd ~/llm-journey/level-02-rag && source venv/bin/activate && streamlit run app.py

# Avviare Livello 3 (agente)
cd ~/llm-journey/level-03-agents && source venv/bin/activate && streamlit run app.py

# Avviare progetto generato dall'agente
cd ~/llm-journey/level-03-agents/output && npm run dev

# Push su GitHub
eval "$(/opt/homebrew/bin/brew shellenv)" && cd ~/llm-journey && git add -A && git commit -m "..." && git push
```

---

## Decisioni architetturali prese

| Decisione | Motivazione |
|-----------|-------------|
| ChromaDB in-memory invece di persistente | Streamlit Cloud non ha filesystem persistente |
| DefaultEmbeddingFunction invece di sentence-transformers | sentence-transformers porta PyTorch, troppo pesante per Streamlit Cloud |
| Generator per l'agente invece di threading | Streamlit non è thread-safe, il threading causava blocchi |
| Repo pubblica | Streamlit Cloud free tier richiede repo pubbliche |
| secrets.toml locale + Streamlit secrets in cloud | Separazione sicura tra ambiente locale e produzione |

---

## Note sui costi API
- Budget target: €10/mese per livelli 1-3
- Modello usato: `claude-opus-4-6` (più capace ma più costoso)
- Per ridurre i costi nei livelli 1-2: passare a `claude-haiku-4-5-20251001`
- L'agente (Livello 3) può fare decine di chiamate API per esecuzione — monitorare il consumo su console.anthropic.com
