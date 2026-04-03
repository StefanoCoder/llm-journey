import os
import streamlit as st
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """Sei un assistente utile, preciso e conciso.
Rispondi sempre in italiano a meno che l'utente non scriva in un'altra lingua."""

st.set_page_config(page_title="Claude Chatbot", page_icon="🤖")
st.title("🤖 Claude Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Scrivi un messaggio..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=st.session_state.history,
            )
            answer = response.content[0].text
            st.write(answer)

    st.session_state.history.append({"role": "assistant", "content": answer})
