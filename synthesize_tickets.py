import os
import random
import time

from dotenv import load_dotenv
from lib.openai import query_openai_json
from lib.prompts import GENERATE_SYNTHETIC_INCIDENTS_OPENAI_PROMPT

from datasets import Dataset
import pandas as pd

load_dotenv()
INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")

num_generations=100 #number of synthetic data to generate
batch_size=5 #number of data to generate per batch

def generate_unique_incident_id(existing_ids):
    while True:
        new_id = f"INC{random.randint(0, 99999):05d}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id
        
if __name__ == "__main__":
    print("Generating synthetic incident tickets...")
    synthetic_data = []
    used_ids = set()

    for i in range(0, num_generations, batch_size):
        count = min(batch_size, num_generations - i)
        prompt = GENERATE_SYNTHETIC_INCIDENTS_OPENAI_PROMPT.format(count=count).strip()

        response = query_openai_json(prompt=prompt)
        if response:
            for item in response:
                item["number"] = generate_unique_incident_id(used_ids)

            synthetic_data.extend(response)
            time.sleep(3)
    
    df = pd.DataFrame(synthetic_data)
    dataset = Dataset.from_pandas(df)
    dataset.push_to_hub(
        repo_id=INCIDENTS_DATASET_HF_REPO_ID,
        commit_message="Final version generated using GPT3.5-Turbo"
    )