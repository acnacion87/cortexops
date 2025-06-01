import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

def query_ollama(prompt, stream=False, model=None):
    """
    Generate a response from the specified LLM via Ollama.

    Args:
        prompt (str): The text prompt to send to the model.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        model (str, optional): The model name (e.g., "llama3.2"). Defaults to "llama3.2:3b" if None.

    Returns:
        The response text from Ollama
    """
    model = model or DEFAULT_MODEL
    try:
        res = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": stream})
        res.raise_for_status()
        content = res.json()["response"]
        
        return content
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None


def query_ollama_json(prompt, stream=False, model=None):
    try:
        content = query_ollama(prompt, stream, model)

        # Extract JSON from potential preamble or markdown formatting
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_text = content[json_start:json_end]

        return json.loads(json_text)
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None