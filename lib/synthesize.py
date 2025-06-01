import time
from lib.ollama import query_ollama_json

def generate_synthetic_data(prompt, count=10, max_attempts=50):
    """
    Generate synthetic data using Ollama.
    
    Args:
        prompt (str): The text prompt to send to the model.
        count (int, optional): Number of samples to generate. Defaults to 10.
        max_attempts (int, optional): The maximum number of attemps to try

    Returns:
        Array of synthetically-generated data
    """
    data = []
    attempts = 0
    while len(data) < count and attempts < max_attempts:
        ticket = query_ollama_json(prompt)
        if ticket:
            data.append(ticket)
            print(f"Generated {len(data)}/{count}")
        else:
            print("Invalid response, skipping")
        attempts += 1
        time.sleep(1)  # Sleep for a while so we don't exhaust CPU
    return data