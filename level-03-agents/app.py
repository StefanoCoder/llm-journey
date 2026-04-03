import os
import threading
import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Technical Architect Agent", page_icon="🏗️", layout="wide")
st.title("🏗️ Technical Architect Agent")
st.caption("L'agente consulta i tuoi standard e costruisce il progetto autonomamente")

api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")

DEFAULT_GOAL = """Costruisci il progetto 'Task Manager Intelligente' (Progetto Alpha) seguendo gli standard del team.

Prima consulta i documenti per capire:
- Lo stack tecnologico da usare
- Gli standard di sviluppo
- Le funzionalità richieste
- Le classi Tailwind standard

Poi genera tutti i file necessari per un progetto Vite + React + TypeScript + Tailwind funzionante,
includendo: struttura del progetto, componenti principali, configurazione Tailwind, tipi TypeScript."""

goal = st.text_area("Obiettivo dell'agente", value=DEFAULT_GOAL, height=150)

if st.button("🚀 Avvia Agente", type="primary", disabled=not api_key):
    st.divider()
    log_container = st.container()

    events = []
    done = threading.Event()

    def on_event(etype, data):
        events.append((etype, data))

    def run():
        run_agent(goal, api_key, on_event=on_event)
        done.set()

    thread = threading.Thread(target=run)
    thread.start()

    with log_container:
        while not done.is_set() or events:
            while events:
                etype, data = events.pop(0)

                if etype == "thought":
                    with st.expander("💭 Ragionamento", expanded=False):
                        st.markdown(data)

                elif etype == "tool_call":
                    name = data["name"]
                    inp = data["input"]
                    if name == "search_docs":
                        st.info(f"🔍 **search_docs** → `{inp['query']}`")
                    elif name == "create_file":
                        st.success(f"📄 **create_file** → `{inp['path']}`")
                    elif name == "read_file":
                        st.info(f"📖 **read_file** → `{inp['path']}`")
                    elif name == "list_files":
                        st.info("📁 **list_files**")

                elif etype == "tool_result":
                    name = data["name"]
                    result = data["result"]
                    if name == "list_files":
                        st.code(result, language="")
                    elif name == "create_file":
                        st.caption(f"✅ {result}")

            if not done.is_set():
                import time
                time.sleep(0.2)
                st.empty()

    thread.join()
    st.success("✅ Agente completato! Controlla la cartella `level-03-agents/output/`")

elif not api_key:
    st.warning("ANTHROPIC_API_KEY non trovata. Aggiungila nei secrets o come variabile d'ambiente.")
