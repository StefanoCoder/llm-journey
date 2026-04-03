import streamlit as st
from rag import ask

st.set_page_config(page_title="RAG Assistant", page_icon="📚")
st.title("📚 RAG Assistant")
st.caption("Fai domande sui tuoi documenti")

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
            result = ask(question)
        st.write(result["answer"])
        st.caption(f"Fonti: {', '.join(result['sources'])}")
        with st.expander("Debug: chunk recuperati"):
            for chunk in result["chunks"]:
                st.text(chunk[:300])

    st.session_state.history.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
