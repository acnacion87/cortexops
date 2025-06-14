import os
import random
import time
import logging
import sys

from dotenv import load_dotenv
from lib.openai import query_openai_json
from lib.prompts import GENERATE_SYNTHETIC_INCIDENTS_OPENAI_SYSTEM_PROMPT, GENERATE_SYNTHETIC_INCIDENTS_OPENAI_USER_PROMPT

from datasets import Dataset
import pandas as pd

num_generations=20 #number of synthetic data to generate
batch_size=5 #number of data to generate per batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[Seed Incidents]')

def generate_unique_incident_id(existing_ids):
    while True:
        new_id = f"INC{random.randint(0, 99999):05d}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id
        
if __name__ == "__main__":
    load_dotenv()

    logger.info("Generating synthetic incident tickets...")

    INCIDENTS_SEED_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_SEED_DATASET_HF_REPO_ID")

    synthetic_data = []
    used_ids = set()

    # Feature/Functionality for the LLM to focus on when generating synthetic incidents
    feature = [
        "Sales Agent onboarding merchant in Sales UI",
        "Sales Agent selecting equipments and configuring fees/services",
        "Merchant logging in to Customer UI to review and e-sign a Merchant Agreement (PDF)",
        "Sales Agent onboarding an additional location for an existing merchant ID",
        "Partners onboarding merchants through REST API"
    ]

    for functionality in feature:
        for i in range(0, num_generations, batch_size):
            count = min(batch_size, num_generations - i)
            
            prompt = GENERATE_SYNTHETIC_INCIDENTS_OPENAI_USER_PROMPT.format(count=count, functionality=functionality).strip()

            response = query_openai_json(prompt=prompt, system_prompt=GENERATE_SYNTHETIC_INCIDENTS_OPENAI_SYSTEM_PROMPT)
            if response:
                synthetic_data.extend(response)
                time.sleep(3)
    
    for item in synthetic_data:
        item["number"] = generate_unique_incident_id(used_ids)

    df = pd.DataFrame(synthetic_data)
    
    logger.info("Pushing seed synthetic incident tickets to %s", INCIDENTS_SEED_DATASET_HF_REPO_ID)
    dataset = Dataset.from_pandas(df)
    dataset.push_to_hub(
        repo_id=INCIDENTS_SEED_DATASET_HF_REPO_ID,
        commit_message="Initial seed incidents to be used with SDV"
    )