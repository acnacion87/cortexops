import os
import pandas as pd
import time
import logging

from dotenv import load_dotenv
from datasets import Dataset, load_dataset
from lib.openai import query_openai_json
from lib.prompts import GENERATE_SYNTHETIC_KB_OPENAI_SYSTEM_PROMPT, GENERATE_SYNTHETIC_KB_OPENAI_USER_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[Seed KBs]')

# Generate the prompt to be used with the model
def make_user_prompt(short_desc, description, resolution):
    return GENERATE_SYNTHETIC_KB_OPENAI_USER_PROMPT.format(
        short_desc=short_desc,
        description=description,
        resolution=resolution)

def generate_doc(ticket):
    short_desc = ticket.get("short_description", "")
    description = ticket.get("description", "")
    resolution = ticket.get("resolution", "")

    system_prompt = GENERATE_SYNTHETIC_KB_OPENAI_SYSTEM_PROMPT
    prompt = make_user_prompt(short_desc, description, resolution)

    try:
        doc = query_openai_json(prompt=prompt, system_prompt=system_prompt)
        if doc:  # Ensure parsing returned usable data
            return doc
        else:
            print(f"Unable to generate documentation for: {short_desc}. Retrying")
    except Exception as e:
        print(f"Failed to generate doc for ticket {ticket.get('number', '?')}: {e}")
            

def generate_docs_from_tickets():
    INCIDENTS_SEED_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_SEED_DATASET_HF_REPO_ID")
    dataset = load_dataset(INCIDENTS_SEED_DATASET_HF_REPO_ID)

    data = dataset["train"]
    dataFrame = data.to_pandas()

    logger.info("Loaded %d incidents from %s", len(dataFrame), INCIDENTS_SEED_DATASET_HF_REPO_ID)

    data = []
    for idx, row in dataFrame.iterrows():
        doc = generate_doc(row)
        if doc:
            data.append(doc)
            logger.info("Generated %d/%d", len(data), len(dataFrame))
        
        time.sleep(1)

    if data:
        KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID = os.getenv("KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID")

        df = pd.DataFrame(data)
        dataset = Dataset.from_pandas(df)
        dataset.push_to_hub(
            repo_id=KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID,
            commit_message="Initial seed knowledge base articles to be used with SDV")

if __name__ == "__main__":
    load_dotenv()

    logger.info("Generating seed synthetic ServiceNow Knowledge Base style articles from seed synthetic incident tickets...")
    generate_docs_from_tickets()
