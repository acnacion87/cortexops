import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma:2b-instruct"
MAX_RETRIES = 3

def query_ollama(prompt, stream=False, model=None, temperature=0.7, maxOutTokens=512):
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
        res = requests.post(OLLAMA_URL, json={
            "model": model,
            "prompt": prompt.strip(),
            "stream": stream,
            "temperature": temperature,
            "num_predict": maxOutTokens
        })
        res.raise_for_status()
        content = res.json()["response"]
        
        return content
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None


def query_ollama_json(prompt, stream=False, model=None, temperature=0.7, maxOutTokens=512):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            content = query_ollama(prompt, stream, model, temperature, maxOutTokens)
            # Remove triple backticks (and optional language tag like ```json)
            content = re.sub(r"```(?:json)?\n?", "", content)  # removes opening ```
            content = content.replace("```", "")         # removes closing ``
            
            print(f"Generated content: {content}")
                
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt} failed: {e}.")
            if attempt == MAX_RETRIES:
                raise
            else:
                print("Retrying...")