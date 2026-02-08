import json
import os
import requests


def build_system_prompt():
    return (
        "Eres un asistente legal general para una app. "
        "Brindas orientación inicial en lenguaje claro, sin prometer resultados. "
        "No sustituyes a un abogado; sugiere consultar a un profesional cuando sea necesario. "
        "Sé breve y directo, y pregunta una sola cosa de seguimiento si ayuda a aclarar el caso."
    )


def ask_legal_chat(message: str):
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("APIKEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY no está configurada.")

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": message},
        ],
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=40,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenAI error {response.status_code}: {response.text}"
        )

    data = response.json()
    if data.get("output_text"):
        return data["output_text"].strip()

    output = data.get("output", [])
    for item in output:
        if item.get("type") == "message":
            content = item.get("content", [])
            parts = []
            for block in content:
                if block.get("type") == "output_text":
                    parts.append(block.get("text", ""))
            if parts:
                return "\n".join(parts).strip()

    return "Lo siento, no pude generar una respuesta en este momento."
