import os
import pandas as pd
import time

from dotenv import load_dotenv
from datasets import Dataset, load_dataset
from lib.openai import query_openai_json
from lib.prompts import GENERATE_SYNTHETIC_DOCS_OPENAI_PROMPT

load_dotenv()
INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")
CONFLUENCE_DATASET_HF_REPO_ID = os.getenv("CONFLUENCE_DATASET_HF_REPO_ID")

dataset = load_dataset(INCIDENTS_DATASET_HF_REPO_ID)

data = dataset["train"]
dataFrame = data.to_pandas()

# Generate the prompt to be used with the model
def make_prompt(short_desc, description, resolution):
    return GENERATE_SYNTHETIC_DOCS_OPENAI_PROMPT.format(
        short_desc=short_desc,
        description=description,
        resolution=resolution)

def generate_doc(ticket):
    short_desc = ticket.get("short_description", "")
    description = ticket.get("description", "")
    resolution = ticket.get("resolution", "")

    prompt = make_prompt(short_desc, description, resolution)

    try:
        doc = query_openai_json(prompt)
        if doc:  # Ensure parsing returned usable data
            return doc
        else:
            print(f"Unable to generate documentation for: {short_desc}. Retrying")
    except Exception as e:
        print(f"Failed to generate doc for ticket {ticket.get('number', '?')}: {e}")
            

def generate_docs_from_tickets():
    print(f"Loaded {len(dataFrame)} incidents from {INCIDENTS_DATASET_HF_REPO_ID}")

    data = []
    for idx, row in dataFrame.iterrows():
        doc = generate_doc(row)
        if doc:
            data.append(doc)
            print(f"Generated {len(data)}/{len(dataFrame)}")
        
        time.sleep(1)

    if data:
        df = pd.DataFrame(data)
        dataset = Dataset.from_pandas(df)
        dataset.push_to_hub(
            repo_id=CONFLUENCE_DATASET_HF_REPO_ID,
            commit_message="Final version generated using GPT3.5-Turbo")

if __name__ == "__main__":
    print("Generating synthetic Confluence-style documentation from synthetic incident tickets...")
    generate_docs_from_tickets()
