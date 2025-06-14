import os
import logging

from dotenv import load_dotenv
from datasets import load_dataset
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List
from lib.embeddings import get_embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[Ingest]')

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

# Preprocess synthetic tickets dataset to LangChain Documents
def tickets_dataset_to_documents():
    INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")

    logger.info("Loding synthetic dataset for customer support tickets: %s", INCIDENTS_DATASET_HF_REPO_ID)
    tickets_dataset = load_dataset(INCIDENTS_DATASET_HF_REPO_ID)

    docs = []
    for item in tickets_dataset["train"]:
        short_desc = (item.get("short_description") or "").strip()
        description = (item.get("description") or "").strip()
        resolution = (item.get("resolution") or "").strip()

        if not short_desc or not description or not resolution:
            continue

        # Combine content for embedding
        content = f"Short Description: {short_desc}\nDescription: {description}\nResolution: {resolution}"
        metadata = {
            "type": "incident",
            "number": item["number"],
            "category": item["category"],
            "impact": item["impact"],
            "urgency": item["urgency"],
            "assignment_group": item["assignment_group"]
        }
        docs.append(Document(page_content=content, metadata=metadata))
    logger.info("Prepare %d incident tickets for indexing", len(docs))

    return docs

# Preprocess synthetic knowledge base dataset to LangChain Documents
def kb_dataset_to_documents():
    KNOWLEDGE_BASE_DATASET_HF_REPO_ID = os.getenv("KNOWLEDGE_BASE_DATASET_HF_REPO_ID")

    logger.info("Loading synthetic dataset for ServiceNow Knowledge Base: %s", KNOWLEDGE_BASE_DATASET_HF_REPO_ID)
    docs_dataset = load_dataset(KNOWLEDGE_BASE_DATASET_HF_REPO_ID)

    docs = []
    for item in docs_dataset["train"]:
        short_description = (item.get("short_description") or "").strip()
        text = (item.get("text") or "").strip()

        # Combine content for embedding
        content = f"{short_description}\n\n{text}"
        metadata = {
            "number": item["number"],
            "category": item["category"],
            "knowledge_base": item["kb_knowledge_base"],
            "created": item["created"],
            "updated": item["updated"],
            "keywords": item["keywords"],
        }
        docs.append(Document(page_content=content, metadata=metadata))
    logger.info("Prepared %d knowledge base articles for indexing.", len(docs))

    return docs

def build_faiss_index(documents: List[Document]):
    INDEX_PATH = os.getenv("INDEX_PATH")

    embed_instruction = (
        "Represent the Merchant Onboarding System incident report or technical "
        "knowledge base article for retrieval, aiming to find relevant resolution "
        "steps and troubleshooting steps"
    )

    embed_model = get_embedding_model()
    
    instructed_docs = [Document(
        page_content=f"{embed_instruction}:{doc.page_content}",
        metadata=doc.metadata) for doc in documents]
    
    docs = text_splitter.split_documents(instructed_docs)

    print("Creating FAISS Index...")
    vector_store = FAISS.from_documents(docs, embed_model)

    print(f"Saving FAISS index to: {INDEX_PATH}")
    vector_store.save_local(INDEX_PATH)

    print("Done! Document embeddings are ready for RAG.")

if __name__ == "__main__":
    logger.info("Starting ingestion process...")

    load_dotenv()

    documents = []
    documents.extend(tickets_dataset_to_documents())
    documents.extend(kb_dataset_to_documents())
    build_faiss_index(documents)




