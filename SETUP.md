# Preparing Your Development Environment
- [Preparing Your Development Environment](#preparing-your-development-environment)
  - [Anaconda/Miniconda](#anacondaminiconda)
    - [Create Conda Environment Using the YML Config](#create-conda-environment-using-the-yml-config)
    - [Manual Setup](#manual-setup)
  - [Configure Environment Variables](#configure-environment-variables)
  - [Run the Ingest Script](#run-the-ingest-script)
  - [Run the API Server](#run-the-api-server)
  - [Run the Chainlit UI](#run-the-chainlit-ui)
  - [Submitting New Incident Requests](#submitting-new-incident-requests)

## Anaconda/Miniconda
- Install Anaconda - https://www.anaconda.com/download or you may also choose the lightweight Miniconda distro

### Create Conda Environment Using the YML Config
This repository contains an exported conda environment configuration which can be used to create a new environment.

```sh
conda env create -f environment.yml
```

### Manual Setup
You may also choose to setup the conda environment manually.

- Setup a new Conda environment with Python 3.10
```sh
conda create -n <your environment name> python=3.10
```
- Activate your environment
```sh
conda activate <your environment name>
```
- Install the dependencies
```sh
pip install -r requirements.txt
```

## Configure Environment Variables
- Create a `.env` file at the root folder and add the following contents:
```properties
# Datasets
INCIDENTS_DATASET_HF_REPO_ID=6StringNinja/synthetic-servicenow-incidents
INCIDENTS_SEED_DATASET_HF_REPO_ID=6StringNinja/synthetic-incidents-seed

KNOWLEDGE_BASE_SEED_DATASET_HF_REPO_ID=6StringNinja/synthetic-kb-seed
KNOWLEDGE_BASE_DATASET_HF_REPO_ID=6StringNinja/synthetic-kb

CONFLUENCE_DATASET_HF_REPO_ID=6StringNinja/synthetic-documentations

# FAISS Index
INDEX_PATH=data/index

# V2 Params
INCIDENTS_INDEX_PATH=data/index/incidents
KNOWLEDGE_BASE_INDEX_PATH=data/index/kb

# Hugging Face
HF_TOKEN=Your HuggingFace API Token>

# OpenAI
OPENAI_API_KEY=<Your OpenAI API KEY>
```

## Run the Ingest Script
```sh
python ingest.py
```

## Run the API Server
```sh
./run_api.sh
```

## Run the Chainlit UI
```sh
./run_ui.sh
```

**Note:** Both API and UI requires a Redis server running. You can either install it directly or use a Docker container.

## Submitting New Incident Requests
Checkout `new_incident.http` file. You can either use the payloads with Postman or install the `REST Client` plugin to Cursor or VS Code and you should be able to execute those payloads within Cursor/VS Code.