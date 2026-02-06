import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"  # low-memory model


def summarize_text(text: str, depth: str = "easy") -> str:
    prompt_map = {
        "easy": "Summarize the following text in simple bullet points:\n\n",
        "medium": "Provide a structured summary with headings:\n\n",
        "long": "Create detailed study notes from the following text:\n\n",
    }

    # Safety limit
    text = text[:3000]
    prompt = prompt_map.get(depth, prompt_map["easy"]) + text

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(response.text)

    return response.json().get("response", "").strip()


# =======================
# STREAMING VERSION (NEW)
# =======================

def summarize_text_stream(text: str, depth: str = "easy"):
    prompt_map = {
        "easy": "Summarize the following text in simple bullet points:\n\n",
        "medium": "Provide a structured summary with headings:\n\n",
        "long": "Create detailed study notes from the following text:\n\n",
    }

    text = text[:3000]
    prompt = prompt_map.get(depth, prompt_map["easy"]) + text

    with requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True,
        },
        stream=True,
        timeout=120,
    ) as response:

        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")
            if chunk:
                yield chunk
