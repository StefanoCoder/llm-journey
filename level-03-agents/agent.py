"""
agent.py — ReAct loop: l'agente ragiona, usa tool, agisce in modo autonomo.
"""

import anthropic
from tools import TOOLS, TOOL_MAP

SYSTEM_PROMPT = """Sei un Technical Architect AI specializzato nello sviluppo web moderno.

Il tuo obiettivo è costruire progetti completi seguendo RIGOROSAMENTE gli standard del team.

REGOLE FONDAMENTALI:
1. Prima di scrivere qualsiasi codice, usa `search_docs` per recuperare gli standard pertinenti.
2. Rispetta sempre lo stack: React + TypeScript + Tailwind + Prisma + Supabase.
3. Ogni componente React deve avere commenti sulle Props.
4. Costruisci il progetto file per file in modo sistematico.
5. Dopo ogni file creato, spiega brevemente cosa hai fatto e perché.
6. Quando hai finito, usa `list_files` per mostrare il progetto completo."""

def run_agent(goal: str, api_key: str, on_event=None):
    """
    Esegue il loop agentivo fino al completamento del task.
    on_event(type, data) — callback per aggiornare la UI in tempo reale.
    """
    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": goal}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "text" and block.text.strip():
                if on_event:
                    on_event("thought", block.text)

            elif block.type == "tool_use":
                if on_event:
                    on_event("tool_call", {"name": block.name, "input": block.input})

                result = TOOL_MAP[block.name](**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

                if on_event:
                    on_event("tool_result", {"name": block.name, "result": result})

        if response.stop_reason == "end_turn":
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return messages
