import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """Sei un assistente utile, preciso e conciso.
Rispondi sempre in italiano a meno che l'utente non scriva in un'altra lingua."""

def chat():
    history = []
    print("Chatbot avviato. Scrivi 'exit' per uscire.\n")

    while True:
        user_input = input("Tu: ").strip()
        if user_input.lower() == "exit":
            print("Arrivederci!")
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        assistant_message = response.content[0].text
        history.append({"role": "assistant", "content": assistant_message})

        print(f"\nClaude: {assistant_message}\n")

if __name__ == "__main__":
    chat()
