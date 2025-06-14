import os

from dotenv import load_dotenv
from datasets import Dataset, load_dataset

import pandas as pd

from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer

from faker import Faker

def get_seed_dataset():
    KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID = os.getenv("KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID")

    seed_dataset = load_dataset(KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID)
    return pd.DataFrame(seed_dataset["train"])

def get_metadata():
    metadata = SingleTableMetadata()
    metadata.add_column("sys_id", sdtype="id", regex_format="^[A-Z]{3}[0-9]{5}$")
    metadata.add_column("number", sdtype="id", regex_format="^KB[0-9]{5}$")
    metadata.add_column("short_description", sdtype="categorical")
    metadata.add_column("text", sdtype="categorical")
    metadata.add_column("kb_knowledge_base", sdtype="categorical")
    metadata.add_column("category", sdtype="categorical")
    metadata.add_column("workflow_state", sdtype="categorical")
    metadata.add_column("published", sdtype="boolean")
    metadata.add_column("valid_to", sdtype="datetime", datetime_format="%Y-%m-%dT%H:%M:%SZ")
    metadata.add_column("created", sdtype="datetime", datetime_format="%Y-%m-%dT%H:%M:%SZ")
    metadata.add_column("updated", sdtype="datetime", datetime_format="%Y-%m-%dT%H:%M:%SZ")
    metadata.add_column("created_by", sdtype="text")
    metadata.add_column("updated_by", sdtype="text")
    metadata.add_column("keywords", sdtype="categorical")
    metadata.add_column("views", sdtype="categorical")
    metadata.add_column("helpful_count", sdtype="categorical")
    metadata.add_column("not_helpful_count", sdtype="categorical")

    return metadata

def synthesize_incidents(num_rows=10):
    df = get_seed_dataset()
    metadata = get_metadata()
    synthesizer = CTGANSynthesizer(
        metadata=metadata,
        verbose=True
    )

    synthesizer.fit(df)
    return synthesizer.sample(num_rows=num_rows)

if __name__ == "__main__":
    load_dotenv()

    fake = Faker()

    df = synthesize_incidents(150)
    df["created_by"] = [fake.name() for _ in range(len(df))]
    df["updated_by"] = [fake.name() for _ in range(len(df))]

    KNOWLEDGE_BASE_DATASET_HF_REPO_ID = os.getenv("KNOWLEDGE_BASE_DATASET_HF_REPO_ID")

    dataset = Dataset.from_pandas(df)
    dataset.push_to_hub(
       repo_id=KNOWLEDGE_BASE_DATASET_HF_REPO_ID,
       commit_message="SDV generated synthetic knowledge base articles"
    )
