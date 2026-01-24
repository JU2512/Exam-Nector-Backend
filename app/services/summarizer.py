import subprocess

OLLAMA_PATH = r"C:\Users\deepa\AppData\Local\Programs\Ollama\ollama.exe"

def summarize_text(text: str, depth: str = "easy") -> str:
    prompt_map = {
        "easy": "Summarize the following text in simple bullet points:\n\n",
        "medium": "Provide a structured summary with headings:\n\n",
        "long": "Create detailed study notes from the following text:\n\n",
    }

    prompt = prompt_map.get(depth, prompt_map["easy"]) + text

    result = subprocess.run(
        [OLLAMA_PATH, "run", "llama3.2:3b"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
