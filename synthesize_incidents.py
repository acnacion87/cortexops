import os

from dotenv import load_dotenv
from datasets import Dataset, load_dataset

import pandas as pd

from sdv.metadata import SingleTableMetadata
from sdv.single_table import CTGANSynthesizer


def get_seed_dataset():
    INCIDENTS_SEED_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_SEED_DATASET_HF_REPO_ID")

    seed_dataset = load_dataset(INCIDENTS_SEED_DATASET_HF_REPO_ID)
    return pd.DataFrame(seed_dataset["train"])

def get_metadata():
    metadata = SingleTableMetadata()
    metadata.add_column("number", sdtype="id", regex_format="^INC[0-9]{5}$")
    metadata.add_column("short_description", sdtype="categorical")
    metadata.add_column("description", sdtype="categorical")
    metadata.add_column("urgency", sdtype="categorical")
    metadata.add_column("impact", sdtype="categorical")
    metadata.add_column("category", sdtype="categorical")
    metadata.add_column("assignment_group", sdtype="categorical")
    metadata.add_column("resolution", sdtype="categorical")

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

    df = synthesize_incidents(500)

    INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")

    dataset = Dataset.from_pandas(df)
    dataset.push_to_hub(
        repo_id=INCIDENTS_DATASET_HF_REPO_ID,
        commit_message="SDV generated synthetic incidents"
    )
